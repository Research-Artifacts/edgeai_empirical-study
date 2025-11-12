import csv
import logging
import os
from typing import List, Dict, Optional

import pandas as pd
from langdetect import detect, LangDetectException

from utils import format_datetime, Menu, HandleCsvFiles

# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------
logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# Globals (kept as-is to preserve behavior and paths)
# -----------------------------------------------------------------------------
ROOT = os.getcwd()

list_file = Menu.list_files_2_menu
recursive_list = Menu.recursive_folder_navigation
concat = HandleCsvFiles.concat_csv_files


def get_valid_option(valid_options):
    """
    Prompt the user for a valid option from the menu.
    Ensures the user input is an integer within the valid options.
    """
    valid_options = set(valid_options)
    while True:
        try:
            user_input = int(input("Enter your choice: "))
        except (ValueError, TypeError):
            logger.warning("Invalid input. Please enter a number.")
            continue
        except (EOFError, KeyboardInterrupt):
            logger.error("Input cancelled by user.")
            raise
        if user_input in valid_options:
            return user_input
        logger.warning("Invalid option. Please choose one of %s.", sorted(valid_options))


def handle_concatenate():
    """Handle the concatenation of files."""
    dataset_folder = f"{ROOT}/dataset"
    data_path = recursive_list(dataset_folder, "Folder")
    logger.info("Selected path for concatenation: %s", data_path)
    concat(data_path)


def handle_remove_duplicates():
    """Handle removing duplicates from a file."""
    path = recursive_list(ROOT, "Folder")
    file_name = list_file(path, "File")

    file_out_name = f"[NO-DUPLICATED]_repo-files_{format_datetime()}.csv"
    input_file = os.path.join(ROOT, "dataset/processed_data", file_name)
    output_file = os.path.join(ROOT, "dataset/processed_data", file_out_name)

    try:
        remove_duplicates(input_file, output_file)
        logger.info("Duplicates removed and saved to %s", output_file)
    except Exception as exc:
        logger.exception("Failed to remove duplicates: %s", exc)


def handle_filter_descriptions():
    """Handle filtering descriptions by language (English)."""
    path = recursive_list(ROOT, "Folder")
    file_name = list_file(path, "File")

    file_out_name = f"[ENGLISH-DESC]_repo-files_{format_datetime()}.csv"
    input_file = os.path.join(ROOT, "dataset/processed_data", file_name)
    output_file = os.path.join(ROOT, "dataset/processed_data", file_out_name)

    try:
        filter_english_descriptions(input_file, output_file)
        logger.info("Filtered descriptions saved to %s", output_file)
    except Exception as exc:
        logger.exception("Failed to filter descriptions: %s", exc)


def _read_csv_safe(file_path: str) -> pd.DataFrame:
    """Read CSV with sane defaults and clear error if the file is missing/corrupt."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"CSV not found: {file_path}")
    return pd.read_csv(file_path)


def remove_duplicates(input_file: str, output_file: str) -> None:
    """
    Read a CSV file and remove duplicate rows based on 'name', 'full_name', and 'URL' columns.

    :param input_file: Path to the input CSV file.
    :param output_file: Path to the CSV file without duplicates.
    """
    df = _read_csv_safe(input_file)

    # Ensure subset columns exist; if any is missing, fall back to all columns to preserve behavior.
    subset_cols = ["name", "full_name", "URL"]
    existing_subset = [c for c in subset_cols if c in df.columns]
    if not existing_subset:
        logger.warning(
            "None of expected columns %s found. Falling back to full-row duplicate removal.",
            subset_cols,
        )
        df_unique = df.drop_duplicates()
    else:
        df_unique = df.drop_duplicates(subset=existing_subset)

    # Persist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    df_unique.to_csv(output_file, index=False)
    logger.info("File saved without duplicates at '%s'.", output_file)


def filter_english_descriptions(input_file: str, output_file: str) -> None:
    """
    Read a CSV file, keep only rows whose 'desc.' language is English, and save to output.

    :param input_file: Path to the input CSV file.
    :param output_file: Path to the filtered CSV file (English descriptions only).
    """
    df = _read_csv_safe(input_file)

    if "desc." not in df.columns:
        logger.warning(
            "Column 'desc.' was not found. Saving empty file to preserve pipeline behavior."
        )
        pd.DataFrame(columns=df.columns).to_csv(output_file, index=False)
        return

    english_rows = []
    for _, row in df.iterrows():
        description = "" if pd.isna(row["desc."]) else str(row["desc."])
        if not description.strip():
            continue
        try:
            if detect(description) == "en":
                english_rows.append(row)
        except LangDetectException:
            # Ignore rows with empty/undetectable descriptions
            continue

    df_english = pd.DataFrame(english_rows)
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    df_english.to_csv(output_file, index=False)
    logger.info("File saved with English descriptions at '%s'.", output_file)


def load_repos_from_csv(file_path: str) -> List[Dict]:
    """
    Load repositories from a single CSV file.

    Expected columns (min): 'name', 'desc.', 'search_term'
    - 'search_term' may contain comma-separated values; we'll split and strip.
    """
    repos: List[Dict] = []
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"CSV not found: {file_path}")

    with open(file_path, mode="r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            raw_terms = row.get("search_term") or ""
            terms = [t.strip() for t in raw_terms.split(",")] if raw_terms else []
            row["search_term"] = terms
            repos.append(row)
    logger.info("[CSV] Loaded %d repositories from %s", len(repos), file_path)
    return repos


def filter_repos_by_exclusion_terms(
    output_path: Optional[str] = None,
    term: Optional[str] = None,
) -> Optional[str]:
    """
    Filter a SINGLE CSV file by exclusion terms and save the result.

    Args:
        output_path: directory for the filtered CSV. If None, uses ROOT/dataset/processed_data.
        term: label used in the output filename (e.g., the search seed). If None, inferred from filename.

    Returns:
        The saved CSV filepath, or None if there was nothing to save.
    """
    folder_path = f"{ROOT}/dataset/processed_data"
    file_path = list_file(folder_path, "File")  # kept as-is to preserve current behavior

    # Default output dir
    if output_path is None:
        output_path = f"{ROOT}/dataset/processed_data"
    os.makedirs(output_path, exist_ok=True)

    # Try to infer 'term' from filename if not provided
    if term is None:
        base = os.path.basename(file_path)
        tokens = os.path.splitext(base)[0].split("_")
        term = tokens[1] if len(tokens) >= 2 else tokens[0]
        logger.debug("[Filter] Inferred term '%s' from filename '%s'", term, base)

    exclusion_terms = {
        "courses", "toy", "tutorial", "classes", "books", "book",
        "guidelines", "tools", "tool", "demos", "demo", "simulator",
        "simulators", "class", "course", "toys", "cutting-edge", "library",
        "cuttingedge", "cutting_edge", "cutting edge",
    }

    repos = load_repos_from_csv(file_path)

    def _concat_text(repo: Dict) -> str:
        name = repo.get("name") or ""
        desc = repo.get("desc.") or ""
        terms_txt = " ".join(repo.get("search_term", []) or [])
        return f"{name} {desc} {terms_txt}".lower()

    filtered_repos: List[Dict] = []
    for repo in repos:
        haystack = _concat_text(repo)
        if any(term_ex in haystack for term_ex in exclusion_terms):
            continue
        filtered_repos.append(repo)

    saved = save_filtered_repository(filtered_repos, output_path, term)
    logger.info(
        "[Filter] Input: %d repos | Filtered: %d repos | Saved: %s",
        len(repos),
        len(filtered_repos),
        saved or "nothing",
    )
    return saved


def save_filtered_repository(
    repos: List[Dict],
    output_path: str,
    term: str,
) -> Optional[str]:
    """
    Persist filtered repositories to CSV.
    Returns the saved filepath or None if nothing to save.
    """
    if not repos:
        logger.warning("[Save] No repositories to save after filtering.")
        return None

    filename = f"[EXCLUSION-TERM]_{term}_{format_datetime()}.csv"
    file_path = os.path.join(output_path, filename)

    # Collect all keys across repos to keep columns stable
    keys = sorted({k for repo in repos for k in repo.keys()})
    with open(file_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(repos)

    logger.info("[Save] Filtered repositories saved to '%s'", file_path)
    return file_path


def main_menu():
    """
    Display the main menu and route the user to the appropriate functionality.
    """
    menu_options = {
        1: handle_concatenate,
        2: handle_remove_duplicates,
        3: handle_filter_descriptions,
        4: filter_repos_by_exclusion_terms,
    }

    print("\n=== Main Menu ===")
    print("Select the processing type:")
    print("[1] - Concatenate")
    print("[2] - Remove Duplicates")
    print("[3] - Filter by Language Descriptions")
    print("[4] - Filter by Exclusion Terms")
    print("=================")

    option = get_valid_option(menu_options.keys())
    menu_options[option]()


if __name__ == "__main__":
    main_menu()


# import csv
# import logging
# import os
# import pandas as pd
#
# from langdetect import detect, LangDetectException
#
# from typing import List, Dict, Optional
#
# from utils import format_datetime, Menu, HandleCsvFiles
#
# logger = logging.getLogger(__name__)
# ROOT = os.getcwd()
#
# list_file       = Menu.list_files_2_menu
# recursive_list  = Menu.recursive_folder_navigation
#
# concat = HandleCsvFiles.concat_csv_files
#
#
# def get_valid_option(valid_options):
#     """
#     Prompts the user for a valid option from the menu.
#     Ensures the user input is an integer within the valid options.
#     """
#     while True:
#         try:
#             user_input = int(input("Enter your choice: "))
#             if user_input in valid_options:
#                 return user_input
#             else:
#                 print(f"Invalid option. Please choose one of {list(valid_options)}.")
#         except ValueError:
#             print("Invalid input. Please enter a number.")
#
# def handle_concatenate():
#     """Handles the concatenation of files."""
#     dataset_folder = f"{ROOT}/dataset"
#     data_path = recursive_list(dataset_folder, 'Folder')
#     print(data_path)
#     concat(data_path)
#
#
# def handle_remove_duplicates():
#     """Handles removing duplicates from a file."""
#     path = recursive_list(ROOT, 'Folder')
#     file_name = list_file(path, 'File')
#     file_out_name = f"[NO-DUPLICATED]_repo-files_{format_datetime()}.csv"
#     input_file = os.path.join(ROOT, "dataset/processed_data", file_name)
#     output_file = os.path.join(ROOT, "dataset/processed_data", file_out_name)
#     remove_duplicates(input_file, output_file)
#     print(f"Duplicates removed and saved to {output_file}")
#
#
# def handle_filter_descriptions():
#     """Handles filtering descriptions by language."""
#     path = recursive_list(ROOT, 'Folder')
#     file_name = list_file(path, 'File')
#     file_out_name = f"[ENGLISH-DESC]_repo-files_{format_datetime()}.csv"
#     input_file = os.path.join(ROOT, "dataset/processed_data", file_name)
#     output_file = os.path.join(ROOT, "dataset/processed_data", file_out_name)
#     filter_english_descriptions(input_file, output_file)
#     print(f"Filtered descriptions saved to {output_file}")
#
#
# def remove_duplicates(input_file: str, output_file: str) -> None:
#     """
#     Read CSV file and remove duplicate rows based =in 'Nome' and 'URL' columns.
#
#     :param input_file: Path to save CSV file input.
#     :param output_file: Path to save duplicated CSV file.
#     """
#     # Read CSV file
#     df = pd.read_csv(input_file)
#
#     # Remove duplicates based on 'Nome' e 'URL columns'
#     df_unique = df.drop_duplicates(subset=['name', 'full_name', 'URL'])
#
#     # Salve resulting DataFrame in a new CSV file
#     df_unique.to_csv(output_file, index=False)
#     print(f"File saved without duplicates in './data_analysis/{output_file}'.")
#
#
# def filter_english_descriptions(input_file: str, output_file: str) -> None:
#     """
#     Read a CSV file, filter english descriptions and save the filtered CSV file.
#
#     :param input_file: Path to read input CSV file.
#     :param output_file: Path to save CSV file with only english description projects.
#     """
#     # Read a CSV file
#     df = pd.read_csv(input_file)
#
#     # Filter only english descriptions
#     english_rows = []
#     for _, row in df.iterrows():
#         description = str(row['desc.'])  # Convert to string if null values exists
#         try:
#             # Detect description language
#             if detect(description) == 'en':
#                 english_rows.append(row)
#         except LangDetectException:
#             # Ignored rows with empty or undetectable descriptions.
#             continue
#
#     # Creat a DataFrame with filtered rows and save in a file
#     df_english = pd.DataFrame(english_rows)
#     df_english.to_csv(output_file, index=False)
#     print(f"File saved with English descriptions in '{output_file}'.")
#
#
# def load_repos_from_csv(file_path: str) -> List[Dict]:
#     """
#     Load repositories from a single CSV file.
#
#     Expected columns (min): 'name', 'desc', 'search_term'
#     - 'search_term' may contain comma-separated values; we'll split and strip.
#     """
#     repos: List[Dict] = []
#     with open(file_path, mode='r', encoding='utf-8-sig', newline='') as f:
#         reader = csv.DictReader(f)
#         for row in reader:
#             raw_terms = row.get('search_term') or ''
#             # normalize to list of trimmed strings
#             terms = [t.strip() for t in raw_terms.split(',')] if raw_terms else []
#             row['search_term'] = terms
#             repos.append(row)
#     logger.info("[CSV] Loaded %d repositories from %s", len(repos), file_path)
#     return repos
#
#
# def filter_repos_by_exclusion_terms(
#     output_path: Optional[str] = None,
#     term: Optional[str] = None,
# ) -> Optional[str]:
#     """
#     Filter a SINGLE CSV file by exclusion terms and save the result.
#
#     Args:
#         file_path: path to the input CSV (single file).
#         output_path: directory where the filtered CSV will be written. If None, uses
#                      f\"{ROOT}/dataset/data_analysis/filtered_by_exclusion_criteria/\".
#         term: label used in the output filename (e.g., the search seed). If None,
#               we try to infer from the input filename pattern.
#         prefix: string added to the output filename.
#
#     Returns:
#         The saved CSV filepath, or None if there was nothing to save.
#     """
#     folder_path = f"{ROOT}/dataset/processed_data"
#     file_path = list_file(folder_path, 'File')
#
#     # Default output dir
#     if output_path is None:
#         output_path = f"{ROOT}/dataset/processed_data"
#     os.makedirs(output_path, exist_ok=True)
#
#     # Try to infer 'term' from filename if not provided
#     if term is None:
#         # Example pattern: <prefix>_<TERM>_repos_*.csv  -> grab the 2nd token
#         base = os.path.basename(file_path)
#         tokens = os.path.splitext(base)[0].split('_')
#         term = tokens[1] if len(tokens) >= 2 else tokens[0]
#         logger.debug("[Filter] Inferred term '%s' from filename '%s'", term, base)
#
#     exclusion_terms = {
#         "courses", "toy", "tutorial", "classes", "books", "book",
#         "guidelines", "tools", "tool", "demos", "demo", "simulator",
#         "simulators", "class", "course", "toys", "cutting-edge", "library",
#         "cuttingedge", "cutting_edge", "Cutting edge", "Cutting-edge",
#         "cutting-edge"
#     }
#
#     repos = load_repos_from_csv(file_path)
#
#     def _concat_text(repo: Dict) -> str:
#         name = repo.get('name') or ''
#         desc = repo.get('desc.') or ''
#         terms = ' '.join(repo.get('search_term', []) or [])
#         return f"{name} {desc} {terms}".lower()
#
#     filtered_repos: List[Dict] = []
#     for repo in repos:
#         haystack = _concat_text(repo)
#         if any(term_ex in haystack for term_ex in exclusion_terms):
#             continue
#         filtered_repos.append(repo)
#
#     saved = save_filtered_repository(filtered_repos, output_path, term)
#     logger.info("[Filter] Input: %d repos | Filtered: %d repos | Saved: %s",
#                 len(repos), len(filtered_repos), saved or "nothing")
#     return saved
#
#
# def save_filtered_repository(
#     repos: List[Dict],
#     output_path: str,
#     term: str,
# ) -> Optional[str]:
#     """
#     Persist filtered repositories to CSV.
#     Returns the saved filepath or None if nothing to save.
#     """
#     if not repos:
#         logger.warning("[Save] No repositories to save after filtering.")
#         return None
#
#     filename = f"[EXCLUSION-TERM]_{term}_{format_datetime()}.csv"
#     file_path = os.path.join(output_path, filename)
#
#     keys = sorted({k for repo in repos for k in repo.keys()})
#     with open(file_path, mode='w', newline='', encoding='utf-8') as f:
#         writer = csv.DictWriter(f, fieldnames=keys)
#         writer.writeheader()
#         writer.writerows(repos)
#
#     logger.info("[Save] Filtered repositories saved to '%s'", file_path)
#     return file_path
#
#
# def main_menu():
#     """
#     Displays the main menu and routes the user to the appropriate functionality.
#     Adheres to software engineering standards and ISO 25010 quality principles.
#     """
#     # Dicionário de opções mapeando entradas do usuário para funções específicas
#     menu_options = {
#         1: handle_concatenate,
#         2: handle_remove_duplicates,
#         3: handle_filter_descriptions,
#         4: filter_repos_by_exclusion_terms,
#     }
#
#     print("\n=== Main Menu ===")
#     print("Select the processing type:")
#     print("[1] - Concatenate")
#     print("[2] - Remove Duplicates")
#     print("[3] - Filter by Language Descriptions")
#     print("[4] - Filter by Exclusion Terms")
#     print("=================")
#
#     # Captura e valida a entrada do usuário
#     option = get_valid_option(menu_options.keys())
#
#     # Executa a função correspondente à opção selecionada
#     menu_options[option]()
#
#
# if __name__ == "__main__":
#     main_menu()
