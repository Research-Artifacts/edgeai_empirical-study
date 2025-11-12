import os
import json
import pandas as pd

from datetime import datetime

ROOT = os.getcwd()

# def save_json_format(file_path, data):
#     with open(file_path, 'w') as outfile:
#         json.dump(data, outfile)


def format_datetime():
    """Returns the current datetime in a format suitable for filenames."""
    return datetime.now().strftime("%Y-%m-%d_%H:%M:%S")


# def load_environment_variables():
#     # Verificar se o arquivo .env existe
#     if not os.path.exists(".env"):
#         raise FileNotFoundError("The .env file NOT FOUND in the currently directory.")


class Menu:

    @staticmethod
    def list_files_2_menu(root, word):
        # Folder receives 'f' for any 'f' within the root, if the join of root + f is a directory
        folders = [f for f in os.listdir(root) if not os.path.isdir(os.path.join(root, f))
                   and not f.startswith('.')
                   and not f.startswith('_')]

        print('\n')
        for i, pastas in enumerate(folders):
            print('{} - {}'.format(i, pastas))
        folder = int(input(f'\nWhich {word} do you want to do with?\n'))
        return os.path.join(root, folders[folder])


    @staticmethod
    def list_folders_2_menu(root: str) -> list[str]:
        """
         List all folders in the given root directory, excluding hidden folders
         and those starting with '_'.

         Args:
             root (str): Path to the root directory.

         Returns:
             list: List of folder names in the root directory.
         """
        return [
            folder for folder in os.listdir(root)
            if os.path.isdir(os.path.join(root, folder))
               and not folder.startswith('.')
               and not folder.startswith('_')
        ]


    @staticmethod
    def recursive_folder_navigation(path: str, word: str) -> str:
        """
        Navigate folders recursively until the user selects a directory without subdirectories
        or decides to exit.

        Args:
            path (str): Path to the root directory.
            word (str): Word to display in choice prompt.

        Returns:
            str: Path to the selected folder, or None if the user exits.
        """
        while True:
            folders = Menu.list_folders_2_menu(path)

            if not folders:
                print(f"No more subfolders in: {path}")
                return path

            print('\nAvailable folder options:\n')
            for index, folder_name in enumerate(folders):
                print(f'{index} - {folder_name}')
            print(f'{len(folders)} - Exit')

            try:
                selected_index = int(input(f'\nWhich {word} do you want to select? '))
                if selected_index == len(folders):  # Exit option
                    print("Exiting navigation.")
                    return None

                selected_folder = os.path.join(path, folders[selected_index])
                path = selected_folder  # Update root for the next iteration
            except (ValueError, IndexError):
                print("Invalid selection. Please choose a valid number.")


class HandleCsvFiles:

    @staticmethod
    def concat_csv_files(folder_path: str) -> None:
        """
        Reads CSV files in a folder, adds a 'Keyword' column with a keyword extracted from the file name,
        and saves all the concatenated data into a new CSV file.

        Args:
            folder_path (str): Path to the folder containing the CSV files.
        """
        lista_dfs = []

        # Iterates over the files in the folder and processes only CSV files
        for file_name in os.listdir(folder_path):
            if file_name.endswith('.csv'):
                file_path = os.path.join(folder_path, file_name)
                print(f"Processing file: {file_name}")

                try:
                    # Reads the CSV file and adds the 'Keyword' column
                    df = pd.read_csv(file_path)
                    # keyword = file_name.split('_')[1]  # Extract the keyword before the first '_'
                    # df['Keyword'] = keyword
                    lista_dfs.append(df)
                except Exception as e:
                    print(f"Error reading file {file_name}: {e}")
    # Concatenate DataFrames and save to a new CSV file
        if lista_dfs:
            folder_name = folder_path.split('/')[-1]
            df_concat = pd.concat(lista_dfs, ignore_index=True)
            output_file = f"dataset/processed_data/[CONCATENATED]-{folder_name}-{format_datetime()}.csv"

            # output_file = os.path.join(f"{ROOT}/dataset/data_analysis_2/{folder_name}-concatenated_output_{format_datetime()}.tables")
            df_concat.to_csv(output_file, index=False)
            print(f"Concatenated file & saved in: {output_file}")
        else:
            print("No CSV file processed.")