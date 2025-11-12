# -*- coding: utf-8 -*-
"""
GitHub repository miner for the EdgeAI replication dataset.
- English logs/messages
- Robust pagination & de-duplication
- Rate-limit/backoff handling
- CSV persistence with timestamped filename
"""

import csv
import logging
import os
import time
from pathlib import Path
from typing import List, Dict, Optional, Tuple

import requests

# --- Project config ---
# Prefer pulling TOKEN and last_year_date from your config module.
# If you already centralize "headers" there, that's fine; we build ours here.
try:
    from .config import NUM_COMMITS, PER_PAGE, MAX_RESP, TOKEN, last_year_date
except Exception as exc:  # Fallbacks / safety defaults if needed
    logging.warning("Falling back to default constants: %s", exc)
    NUM_COMMITS = 100
    PER_PAGE = 50
    MAX_RESP = 400
    TOKEN = os.getenv("GITHUB_TOKEN", "")
    # last_year_date like '2024-01-01' or dynamic (you can compute it in config)
    last_year_date = os.getenv("GITHUB_LAST_YEAR_DATE", "2024-01-01")

# --- Logging setup ---
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s | %(levelname)s | %(name)s:%(lineno)d - %(message)s",
)
logger = logging.getLogger("edgeai.repo_miner")

# --- HTTP client config ---
BASE_URL = "https://api.github.com"
HEADERS = {
    "Accept": "application/vnd.github.v3+json",
}
if TOKEN:
    print(TOKEN)
    # Prefer the modern "Bearer" form (the legacy "token" form still works but is discouraged)
    HEADERS["Authorization"] = f"Bearer {TOKEN}"

# --- FS paths ---
ROOT = Path(os.getcwd()).resolve()
OUTPUT_DIR = ROOT / "dataset" / "raw_data2"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# --- Utils ---
def format_datetime() -> str:
    """Return a compact timestamp for filenames, e.g., 2025-11-12_120501."""
    import datetime as _dt
    return _dt.datetime.now().strftime("%Y-%m-%d_%H%M%S")


def github_get(
    url: str,
    params: Optional[Dict] = None,
    max_retries: int = 5,
    backoff_base: float = 2.0,
    timeout: int = 30,
) -> requests.Response:
    """
    GitHub GET with basic rate-limit & transient error handling.
    - Retries on 429/403 (rate limit) and 5xx
    - Exponential backoff
    """
    attempt = 0
    while True:
        r = requests.get(url, headers=HEADERS, params=params or {}, timeout=timeout)

        # Success fast-path
        if 200 <= r.status_code < 300:
            remaining = r.headers.get("X-RateLimit-Remaining")
            if remaining is not None:
                logger.debug("Rate limit remaining: %s", remaining)
            return r

        # Handle rate limit (403 with "rate limit exceeded") or explicit 429
        if r.status_code in (403, 429):
            reset = r.headers.get("X-RateLimit-Reset")
            if reset and r.status_code == 403 and "rate limit" in r.text.lower():
                # Sleep until reset if possible
                try:
                    reset_epoch = int(reset)
                    wait_s = max(0, reset_epoch - int(time.time()) + 2)
                    logger.warning("Rate limit hit. Sleeping until reset in ~%ss", wait_s)
                    time.sleep(wait_s)
                    attempt += 1
                    if attempt > max_retries:
                        r.raise_for_status()
                    continue
                except Exception:
                    # Fallback to backoff
                    pass

        # Retry on 5xx or fall back for other transient errors
        if r.status_code >= 500 or r.status_code in (403, 429):
            if attempt >= max_retries:
                logger.error("Max retries exceeded for %s (status=%s, body=%s)", url, r.status_code, r.text[:200])
                r.raise_for_status()
            sleep_s = backoff_base ** attempt
            logger.warning("Transient error %s. Retrying in %.1fs ...", r.status_code, sleep_s)
            time.sleep(sleep_s)
            attempt += 1
            continue

        # Non-retryable client errors
        logger.error("GitHub request failed: %s - %s", r.status_code, r.text[:200])
        r.raise_for_status()


def search_github_repos(
    search_term: str,
    sort: str = "stars",
    order: str = "desc",
    per_page: int = PER_PAGE,
) -> List[Dict]:
    """
    Search repositories with de-duplication and page-through logic until MAX_RESP.
    """
    url = f"{BASE_URL}/search/repositories"
    query = f"{search_term} in:name,description,topics, pushed:>{last_year_date} stars:>10"

    all_repositories: List[Dict] = []
    seen_ids = set()
    page = 1

    logger.info("Searching term '%s' ...", search_term)

    while len(all_repositories) < MAX_RESP:
        params = {
            "q": query,
            "sort": sort,
            "order": order,
            "per_page": per_page,
            "page": page,
        }
        r = github_get(url, params=params)
        data = r.json()
        items = data.get("items", []) or []

        if not items:
            logger.info("No more results (page=%s).", page)
            break

        added = 0
        for repo in items:
            rid = repo.get("id")
            if rid not in seen_ids:
                seen_ids.add(rid)
                all_repositories.append(repo)
                added += 1
                if len(all_repositories) >= MAX_RESP:
                    break

        logger.info(
            "Page %d fetched: %d items | %d added | total unique=%d",
            page, len(items), added, len(all_repositories),
        )

        if len(items) < per_page:
            logger.info("Reached last page (items < per_page).")
            break

        page += 1
        time.sleep(3)  # be nice to the API

    return all_repositories[:MAX_RESP]


def _count_commits_range(owner: str, repo_name: str, since: Optional[str], until: Optional[str]) -> int:
    """
    Count commits by paging through /commits with optional date range.
    Note: REST does not expose a single-count endpoint; GraphQL could be used for faster totals.
    """
    commits_url = f"{BASE_URL}/repos/{owner}/{repo_name}/commits"
    total = 0
    page = 1

    while True:
        params = {"per_page": 100, "page": page}
        if since:
            params["since"] = since
        if until:
            params["until"] = until

        r = github_get(commits_url, params=params)
        commits = r.json() or []
        batch = len(commits)
        total += batch

        if batch < 100:
            break

        page += 1

    return total


def count_total_commits(owner: str, repo_name: str) -> int:
    """Total commits on the default branch (approximation via REST pagination)."""
    try:
        return _count_commits_range(owner, repo_name, since=None, until=None)
    except Exception as exc:
        logger.error("Failed to count commits for %s/%s: %s", owner, repo_name, exc)
        return 0


def count_commits_2024(owner: str, repo_name: str) -> int:
    """Commits within 2024 (inclusive)."""
    try:
        return _count_commits_range(
            owner, repo_name,
            since="2024-01-01T00:00:00Z",
            until="2024-12-31T23:59:59Z",
        )
    except Exception as exc:
        logger.error("Failed to count 2024 commits for %s/%s: %s", owner, repo_name, exc)
        return 0


def get_contributors_count(owner: str, repo_name: str) -> int:
    """
    Count 'contributors' (GitHub API /contributors). Note this is not 'collaborators' with permissions.
    """
    url = f"{BASE_URL}/repos/{owner}/{repo_name}/contributors"
    try:
        r = github_get(url, params={"per_page": 100})
        data = r.json() or []
        return len(data)
    except Exception as exc:
        logger.error("Failed to fetch contributors for %s/%s: %s", owner, repo_name, exc)
        return 0


class HandleCsv:
    """
    CSV handler for writing the selected repository fields into a timestamped file.
    """

    HEADER = [
        "name", "full_name", "URL", "desc.", "total_commits", "last_commit", "commits_2024",
        "stars", "fork", "forks", "lang", "size", "score", "template", "archived", "disabled",
        "contributors_url", "collaborators_url", "contributors", "search_term",
    ]

    def __init__(self, repos: List[Dict], term: str, prefix: str = ""):
        self.term = term
        self.repos = repos or []
        self.prefix = prefix
        self.output_path: Optional[Path] = None

    def handling_to_save(self) -> None:
        """Create output path and trigger CSV writing."""
        filename = f"{self.prefix}{self.term}_repos_{format_datetime()}.csv"
        self.output_path = OUTPUT_DIR / filename
        self.save_to_csv()
        logger.info("Data saved to %s", self.output_path)

    def save_to_csv(self) -> None:
        """Write repository rows into CSV (one file per term run)."""
        if not self.repos:
            logger.warning("No data to persist for term '%s'.", self.term)
            return

        assert self.output_path is not None, "Output path must be set before saving."
        with self.output_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(self.HEADER)

            for repo in self.repos:
                owner = repo["owner"]["login"]
                name = repo["name"]
                full_name = repo["full_name"]

                total_commits = count_total_commits(owner, name)
                last_commit = repo.get("pushed_at")
                commits_2024 = count_commits_2024(owner, name)

                writer.writerow([
                    name,
                    full_name,
                    repo.get("html_url"),
                    repo.get("description"),
                    total_commits,
                    last_commit,
                    commits_2024,
                    repo.get("stargazers_count"),
                    repo.get("fork"),
                    repo.get("forks"),
                    repo.get("language"),
                    repo.get("size"),
                    repo.get("score"),
                    repo.get("is_template"),
                    repo.get("archived"),
                    repo.get("disabled"),
                    repo.get("contributors_url"),
                    repo.get("collaborators_url"),
                    get_contributors_count(owner, name),
                    self.term,
                ])

    @staticmethod
    def load_repos_from_csv(file_path: Path) -> List[Dict]:
        """Utility reader if you need to reload previously saved repos."""
        rows: List[Dict] = []
        with Path(file_path).open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # 'search_term' is a single term in this file; keep as str for now
                rows.append(row)
        return rows


def search_and_save_management(term: str) -> None:
    """Run the search for a single term and persist its results."""
    logger.info("Starting search for term: %s", term)
    repos = search_github_repos(term, per_page=PER_PAGE)
    if not repos:
        logger.warning("No repositories found for '%s'.", term)
        return

    handler = HandleCsv(repos, term, prefix="RAW_")
    handler.handling_to_save()


def main() -> None:
    search_terms = [
        "edge ai",
        # "edge_ai", "edgeiot", "edge iot",
        # "edge-tpu", "edgetpu", "edge tpu", "edge_tpu",
        # "tiny-ml", "tinyml", "tiny ml", "tiny_ml",
        # "edge-impulse", "edgeimpulse", "edge impulse", "edge_impulse",
        # "edge-architecture", "edgearchitecture", "edge architecture", "edge_architecture",
        # "edge-ai-architecture", "edgeaiarchitecture", "edge ai architecture", "edge_ai_architecture",
    ]
    for term in search_terms:
        search_and_save_management(term)
        # Small courtesy sleep to avoid tight loops across terms
        time.sleep(2)


if __name__ == "__main__":
    main()
    logger.info("Process done.")
