import requests
import csv
import os
import time
import logging

from dotenv import load_dotenv

from datetime import datetime, timedelta

from typing import List, Dict, Optional

from utils import format_datetime

load_dotenv()


root = os.getcwd()
logger = logging.getLogger(__name__)


last_year_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')

NUM_COMMITS = 50
NUM_STARS = 2

PER_PAGE = int(os.getenv('PER_PAGE'))
MAX_RESP = int(os.getenv('MAX_RESP'))

TOKEN    = os.getenv('API_TOKEN')

headers = {
    'Authorization': f'token {TOKEN}',
    'Accept': 'application/vnd.github.v3+json'
}


class HandleCsv:
    """
    Helper class to handle CSV generation for mined GitHub repositories.
    """

    def __init__(self, repos, term: str, prefix: str = "") -> None:
        """
        Initialize the CSV handler.

        Parameters
        ----------
        repos : list
            List of repository objects (as returned by the GitHub Search API).
        term : str
            Search term used to retrieve the repositories.
        prefix : str, optional
            Prefix to be added to the output CSV filename.
        """
        self.term = term
        self.csv_file = repos
        self.prefix = prefix
        self.repos = repos
        self.output_path: Optional[str] = None

    def handling_to_save(self) -> None:
        """
        Prepare output filename and trigger CSV export for the current repositories.
        """
        filename = f"{self.prefix}{self.term}_repos_{format_datetime()}.csv"
        output_folder = os.path.join(root, "dataset/raw_data")

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        self.output_path = os.path.join(output_folder, filename)

        logger.info("Saving repository data to CSV: %s", self.output_path)
        self.save_to_csv()
        logger.info("Data successfully saved to %s", self.output_path)

    def save_to_csv(self) -> None:
        """
        Save repositories data to a CSV file, including commits and collaborators information.

        Notes
        -----
        - Uses `self.repos` as the source of data.
        - Requires `self.output_path` to be set before calling this method.
        """
        if not self.repos:
            logger.warning("No repository data to save. CSV file will not be created.")
            return

        if not self.output_path:
            logger.error("Output path is not set. Aborting CSV save operation.")
            return

        with open(self.output_path, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(
                [
                    "name",
                    "full_name",
                    "URL",
                    "desc.",
                    "total_commits",
                    "last_commit",
                    "commits_2024",
                    "stars",
                    "fork",
                    "forks",
                    "lang",
                    "size",
                    "score",
                    "template",
                    "archived",
                    "disabled",
                    "contributors_url",
                    "collaborators_url",
                    "collaborators",
                    "search_term",
                ]
            )

            for repo in self.repos:
                owner = repo["owner"]["login"]
                name = repo["name"]
                full_name = repo["full_name"]
                total_commits = count_total_commits(owner, name)
                last_commit = repo["pushed_at"]
                commits_2024 = count_commits_2024(owner, name)
                fork = repo["fork"]
                forks = repo["forks"]
                size = repo["size"]
                score = repo["score"]
                archived = repo["archived"]
                disabled = repo["disabled"]
                contributors_url = repo["contributors_url"]
                collaborators_url = repo["collaborators_url"]
                collaborators_count = get_collaborators_count(owner, name)

                writer.writerow(
                    [
                        name,
                        full_name,
                        repo["html_url"],
                        repo["description"],
                        total_commits,
                        last_commit,
                        commits_2024,
                        repo["stargazers_count"],
                        fork,
                        forks,
                        repo["language"],
                        size,
                        score,
                        repo["is_template"],
                        archived,
                        disabled,
                        contributors_url,
                        collaborators_url,
                        collaborators_count,
                        self.term,
                    ]
                )

    def load_repos_from_csv(self, file_path: str) -> List[Dict]:
        """
        Load repositories from an existing CSV file.

        The `search_term` column is converted to a list, assuming comma-separated values.

        Parameters
        ----------
        file_path : str
            Path to the CSV file containing repository data.

        Returns
        -------
        list of dict
            List of repositories loaded from the CSV file.
        """
        repos: List[Dict] = []
        with open(file_path, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Convert search_term column to a list, assuming comma-separated values
                row["search_term"] = (
                    row.get("search_term", "").split(",") if row.get("search_term") else []
                )
                repos.append(row)
        return repos


def search_github_repos(
    search_term: str,
    sort: str = "stars",
    order: str = "desc",
    per_page: int = PER_PAGE,
) -> Optional[List[Dict]]:
    """
    Search repositories on GitHub using the REST API, ensuring unique results.

    Parameters
    ----------
    search_term : str
        Search term (e.g., 'EdgeAI').
    sort : str, optional
        Sorting criterion ('stars', 'forks', etc.). Default is 'stars'.
    order : str, optional
        Sorting order: 'asc' for ascending, 'desc' for descending. Default is 'desc'.
    per_page : int, optional
        Number of results per page (max: 100). Default is `PER_PAGE`.

    Returns
    -------
    list of dict or None
        List of repository objects (at most `MAX_RESP`), or None in case of error.
    """
    url = "https://api.github.com/search/repositories"
    query = f"{search_term} in:name,description,topics, pushed:>{last_year_date} stars:>10"

    params = {
        "q": query,
        "sort": sort,
        "order": order,
        "per_page": per_page,
    }

    all_repositories: List[Dict] = []
    seen_repos = set()
    page = 1

    logger.info("Starting GitHub search for term '%s'.", search_term)

    while len(all_repositories) < MAX_RESP:
        params["page"] = page
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
        except requests.RequestException as exc:
            logger.error("Request error while searching repositories: %s", exc)
            break

        if response.status_code != 200:
            logger.error(
                "Error while searching repositories: %s - %s",
                response.status_code,
                response.text,
            )
            break

        data = response.json()
        repositories = data.get("items", [])

        if not repositories:
            logger.info("No more repositories returned by the API (page %d).", page)
            break

        for repo in repositories:
            repo_id = repo["id"]
            if repo_id not in seen_repos:
                seen_repos.add(repo_id)
                all_repositories.append(repo)

        logger.info(
            "Page %d loaded with %d repositories (%d unique accumulated).",
            page,
            len(repositories),
            len(all_repositories),
        )

        if len(repositories) < per_page:
            logger.info("Last page reached at page %d.", page)
            break

        page += 1
        time.sleep(3)  # Avoid hitting API rate limits

    limited_results = all_repositories[:MAX_RESP]
    logger.info(
        "Search for '%s' finished with %d unique repositories (limited to %d).",
        search_term,
        len(all_repositories),
        len(limited_results),
    )
    return limited_results


def count_total_commits(owner: str, repo_name: str) -> int:
    """
    Count the total number of commits in a GitHub repository.

    Parameters
    ----------
    owner : str
        Repository owner (GitHub username or organization).
    repo_name : str
        Repository name.

    Returns
    -------
    int
        Total number of commits in the repository.
    """
    commits_url = f"https://api.github.com/repos/{owner}/{repo_name}/commits"
    params = {"per_page": 100}
    total_commits = 0
    page = 1

    while True:
        try:
            response = requests.get(
                commits_url, headers=headers, params={**params, "page": page}
            )
        except requests.RequestException as exc:
            logger.error(
                "Request error while fetching commits for %s: %s", repo_name, exc
            )
            break

        if response.status_code == 200:
            commits = response.json()
            total_commits += len(commits)
            if len(commits) < NUM_COMMITS:
                break
            page += 1
        else:
            logger.error(
                "Error while fetching commits for %s: %s - %s",
                repo_name,
                response.status_code,
                response.text,
            )
            break

    logger.debug("Total commits for %s/%s: %d", owner, repo_name, total_commits)
    return total_commits


def count_commits_2024(owner: str, repo_name: str) -> int:
    """
    Count the number of commits in the year 2024 for a GitHub repository.

    Parameters
    ----------
    owner : str
        Repository owner (GitHub username or organization).
    repo_name : str
        Repository name.

    Returns
    -------
    int
        Number of commits in 2024.
    """
    commits_url = f"https://api.github.com/repos/{owner}/{repo_name}/commits"
    params = {
        "since": "2024-01-01T00:00:00Z",
        "until": "2024-12-31T23:59:59Z",
        "per_page": 100,
    }
    total_commits_2024 = 0
    page = 1

    while True:
        try:
            response = requests.get(
                commits_url, headers=headers, params={**params, "page": page}
            )
        except requests.RequestException as exc:
            logger.error(
                "Request error while fetching 2024 commits for %s: %s", repo_name, exc
            )
            break

        if response.status_code == 200:
            commits = response.json()
            total_commits_2024 += len(commits)
            if len(commits) < NUM_COMMITS:
                break
            page += 1
        else:
            logger.error(
                "Error while fetching 2024 commits for %s: %s - %s",
                repo_name,
                response.status_code,
                response.text,
            )
            break

    logger.debug(
        "Total commits in 2024 for %s/%s: %d", owner, repo_name, total_commits_2024
    )
    return total_commits_2024


def get_collaborators_count(owner: str, repo_name: str) -> int:
    """
    Count the number of collaborators (contributors) in a GitHub repository.

    Parameters
    ----------
    owner : str
        Repository owner (GitHub username or organization).
    repo_name : str
        Repository name.

    Returns
    -------
    int
        Number of collaborators (contributors), or 0 in case of error.
    """
    collaborators_url = (
        f"https://api.github.com/repos/{owner}/{repo_name}/contributors"
    )
    params = {"per_page": 100}

    try:
        response = requests.get(collaborators_url, headers=headers, params=params)
    except requests.RequestException as exc:
        logger.error(
            "Request error while fetching collaborators for %s: %s", repo_name, exc
        )
        return 0

    if response.status_code == 200:
        collaborators = len(response.json())
        logger.debug("Collaborators for %s/%s: %d", owner, repo_name, collaborators)
        return collaborators
    else:
        logger.error(
            "Error while fetching collaborators for %s: %s - %s",
            repo_name,
            response.status_code,
            response.text,
        )
        return 0


def search_and_save_management(term: str) -> None:
    """
    Perform GitHub search for a given term and save the results to a CSV file.

    Parameters
    ----------
    term : str
        Search term to be used in the GitHub Search API.
    """
    logger.info("Searching repositories for term '%s'...", term)

    repos = search_github_repos(term, per_page=PER_PAGE)
    if not repos:
        logger.warning("No repositories found for term '%s'.", term)
        return

    handler = HandleCsv(repos, term, prefix="RAW_")
    handler.handling_to_save()


def main() -> None:
    """
    Entry point for the mining script.

    Iterates over a predefined list of EdgeAI-related search terms, retrieves
    repositories from GitHub, and stores the results as CSV files in
    `dataset/raw_data`.
    """
    search_terms = [
        "edge ai",
        "edge_ai",
        "edgeiot",
        "edge iot",
        "edge-tpu",
        "edgetpu",
        "edge tpu",
        "edge_tpu",
        "tiny-ml",
        "tinyml",
        "tiny ml",
        "tiny_ml",
        "edge-impulse",
        "edgeimpulse",
        "edge impulse",
        "edge_impulse",
        "edge-architecture",
        "edgearchitecture",
        "edge architecture",
        "edge_architecture",
        "edge-ai-architecture",
        "edgeaiarchitecture",
        "edge ai architecture",
        "edge_ai_architecture",
    ]

    logger.info("Starting GitHub mining for %d search terms.", len(search_terms))

    for term in search_terms:
        search_and_save_management(term)

    logger.info("GitHub mining process completed for all terms.")


if __name__ == "__main__":
    # Basic logging configuration for standalone execution.
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s: %(message)s",
    )
    main()
