from typing import List
import shutil
from threading import Thread
import logging
import argparse
from pathlib import Path
from additional import normalize, check_name

"""
    Script for sorting files in a specific folder.

    Usage:
        python script.py --folder /path/to/folder

    Arguments:
    -f, --folder: Path to the folder to be sorted.
    
    python main.py -f C:/Users/MS/Desktop
"""

parser = argparse.ArgumentParser(description="App for sorting files in specific folder")
parser.add_argument("-f", "--folder", default=True)

args = vars(parser.parse_args())
folder_path = args.get("folder")
current_folder = Path(folder_path)
folders = []
points = "-" * 100

# created new folders
new_directory = ["images", "video", "documents", "audio", "archives"]
FOLDERS = [current_folder.joinpath(new_dir) for new_dir in new_directory]
EXTENSIONS = [
    [".jpeg", ".png", ".jpg", ".svg"],
    [".avi", ".mp4", ".mov", ".mkv"],
    [".doc", ".docx", ".txt", ".pdf", ".xlsx", ".pptx", ".ppt", ".djvu"],
    [".mp3", ".ogg", ".wav", ".amr", ".flac"],
    [".zip", ".gz", ".tar"],
]
STR_EXTENSIONS = "".join(["".join(val) for val in EXTENSIONS])


def create_folders(folders_list: List[Path]):
    """
    Creates directories from a list of paths. If a directory already exists, it does not raise an error.

    This function iterates through a list of directory paths and creates them if they do not already exist.
    The `parents=True` argument ensures that any missing parent directories are also created.
    The `exist_ok=True` argument prevents the function from raising an error if a directory already exists.

    Parameters:
        folders_list (List[Path]): A list of Path objects representing the directories to be created.

    Example:
        >>> folders = [Path("folder1"), Path("folder2/subfolder")]
        >>> create_folders(folders)
        # Creates 'folder1' and 'folder2/subfolder' if they don't already exist.
    """
    for path_folder in folders_list:
        path_folder.mkdir(exist_ok=True, parents=True)


def graphs_folder(path: Path):
    """
    Recursively traverses a directory and collects all subdirectories that are not in the `FOLDERS` list.

    This function iterates through all items in the given directory. If an item is a directory and not in the
    `FOLDERS` list, it adds the directory to the `folders` list and recursively processes its contents.

    Parameters:
        path (Path): The root directory to start traversing.

    Note:
        - `FOLDERS` is assumed to be a predefined list of directories to exclude.
        - `folders` is assumed to be a predefined list where new directories are stored.

    Example:
        >>> FOLDERS = [Path("exclude_this_folder")]
        >>> folders = []
        >>> graphs_folder(Path("root_folder"))
        # Adds all subdirectories of 'root_folder' to `folders`, except those in `FOLDERS`.
    """
    for val in path.iterdir():
        if val.is_dir() and val not in FOLDERS:
            folders.append(val)
            graphs_folder(val)


unknown_files = []
deleted_folders = []
ex_folders = [[], [], [], [], []]
ex_unknown = []
moved_files = []


def move_files(fol_path: Path, index: int):
    """
    Moves files from a source folder to a destination folder based on their file extensions.

    This function iterates through all files in the source folder (`fol_path`). If a file's extension matches
    one of the extensions in `EXTENSIONS[index]`, it moves the file to the corresponding destination folder
    (`FOLDERS[index]`). The file name is normalized and checked for uniqueness before moving.

    Files with unknown extensions (not in `STR_EXTENSIONS`) are added to the `unknown_files` list.

    A log of moved and renamed files is stored in `moved_files`.

    Parameters:
        fol_path (Path): The source folder containing files to move.
        index (int): The index used to access the corresponding extensions and destination folder in `EXTENSIONS` and `FOLDERS`.

    Note:
        - `EXTENSIONS`: A predefined list of lists, where each sublist contains file extensions for a specific category.
        - `FOLDERS`: A predefined list of destination folders corresponding to each category.
        - `STR_EXTENSIONS`: A predefined string or list of all known file extensions.
        - `unknown_files`: A predefined list to store files with unknown extensions.
        - `ex_unknown`: A predefined list to store unknown file extensions.
        - `moved_files`: A predefined list to store logs of moved files.
        - `ex_folders`: A predefined list to store file extensions of moved files.

    Example:
        >>> EXTENSIONS = [[".txt", ".doc"], [".jpg", ".png"]]
        >>> FOLDERS = [Path("text_files"), Path("image_files")]
        >>> STR_EXTENSIONS = ".txt .doc .jpg .png"
        >>> unknown_files = []
        >>> ex_unknown = []
        >>> moved_files = []
        >>> ex_folders = [[] for _ in range(len(FOLDERS))]
        >>> move_files(Path("source_folder"), 0)
        # Moves .txt and .doc files from 'source_folder' to 'text_files'.
    """
    log_list = [
        f"From folder //{str(fol_path.name)}// removed to //{new_directory[index]}// next files:"
    ]
    for element in fol_path.iterdir():
        if element.is_file() and element.suffix in EXTENSIONS[index]:
            namefile = FOLDERS[index].joinpath(
                f"{normalize(check_name(element, FOLDERS[index]))}{element.suffix}"
            )
            shutil.move(element, namefile)
            ex_folders[index].append(element.suffix)
            if element.name == namefile.name:
                log_list.append("{:^10}{:<40}".format("", f"{element.name}"))
            else:
                log_list.append(
                    "{:^10}{:<40}{:^7}{:<40}".format(
                        "Renamed", f"{element.name}", "-->", f"{namefile.name}"
                    )
                )
        elif element.is_file() and element.suffix not in STR_EXTENSIONS:
            unknown_files.append(element.name)
            ex_unknown.append(element.suffix)
    moved_files.append(log_list)


def print_logging_files(file_list: List[List[Path]]):
    """
    Prints a formatted log of files from a nested list of file paths.

    This function iterates through a nested list of file paths (`file_list`). For each sublist that contains more than one
    file path, it prints a separator (`points`) followed by the file paths in the sublist.

    Parameters:
        file_list (List[List[Path]]): A nested list of file paths to log.

    Note:
        - `points` is assumed to be a predefined separator (e.g., a string of dashes or equal signs).
        - Each sublist in `file_list` represents a group of related file paths.

    Example:
        >>> points = "=" * 50
        >>> file_list = [
        ...     [Path("file1.txt"), Path("file2.txt")],
        ...     [Path("file3.jpg")],
        ...     [Path("file4.doc"), Path("file5.doc")]
        ... ]
        >>> print_logging_files(file_list)
        ==================================================
        file1.txt
        file2.txt
        ==================================================
        file4.doc
        file5.doc
    """
    for val in file_list:
        if len(val) > 1:
            print(points)
            for val_ in val:
                print(val_)
                # print('{:^5}{:<40}'.format('', f'{val_}'))


def print_files(path, text):
    """
    Prints the names of all files and directories in the specified path, preceded by a descriptive text.

    This function checks if the provided path exists. If it does, it prints the given `text` and then iterates
    through all items (files and directories) in the path, printing their names in a formatted manner.

    Parameters:
        path (Path): The directory path to list files and directories from.
        text (str): A descriptive text to print before listing the files.

    Example:
        >>> print_files(Path("example_folder"), "Files in example_folder:")
        Files in example_folder:
              file1.txt
              file2.txt
              subfolder/
    """
    if path:
        print(text)
        for val in path.iterdir():
            print("{:^10}{:<40}".format("", f"{val.name}"))


def print_extensions(value, text):
    """
    Prints a formatted list of unique file extensions preceded by a descriptive text.

    This function checks if the provided list of extensions (`value`) is not empty. If it contains items,
    it prints the given `text` and then prints the unique file extensions in a formatted manner.

    Parameters:
        value (list): A list of file extensions to print.
        text (str): A descriptive text to print before listing the extensions.

    Example:
        >>> extensions = [".txt", ".jpg", ".txt", ".png"]
        >>> print_extensions(extensions, "Unique file extensions:")
        Unique file extensions:
                   .txt, .jpg, .png
    """
    if value:
        print(text)
        print("{:^15}{:<50}".format("", f'{", ".join(set(value))}'))


def delete_dir(path: Path):
    """
    Recursively deletes empty directories within the specified path, excluding directories in the `FOLDERS` list.

    This function checks if the provided path is not in the `FOLDERS` list. If it is not, it recursively deletes
    all empty subdirectories within the path. If the path itself becomes empty after deleting its contents,
    it is also deleted and added to the `deleted_folders` list.

    Parameters:
        path (Path): The directory path to process.

    Note:
        - `FOLDERS` is assumed to be a predefined list of directories to exclude from deletion.
        - `deleted_folders` is assumed to be a predefined list to store paths of deleted directories.

    Example:
        >>> FOLDERS = [Path("keep_this_folder")]
        >>> deleted_folders = []
        >>> delete_dir(Path("example_folder"))
        # Deletes all empty subdirectories in 'example_folder', excluding 'keep_this_folder'.
    """
    if path not in FOLDERS:
        for element in path.iterdir():
            if element.is_dir():
                delete_dir(element)
        if not any(path.iterdir()):
            deleted_folders.append(path)
            path.rmdir()


def main():
    """
    Main function to organize files in a directory into categorized folders.

    This function performs the following steps:
    1. Sets up logging and creates predefined folders for file organization.
    2. Recursively traverses the current directory to collect subdirectories.
    3. Uses multithreading to move files into categorized folders based on their extensions.
    4. Deletes empty directories after moving files.
    5. Prints logs of moved files, deleted folders, and categorized files.
    6. Handles unknown files and prints their extensions.
    7. Unpacks archives into their respective folders and deletes the original archive files.

    Note:
        - `FOLDERS`: A predefined list of folders for categorized files (e.g., Photos, Videos, Documents, etc.).
        - `EXTENSIONS`: A predefined list of lists, where each sublist contains file extensions for a specific category.
        - `folders`: A list to store directories to process.
        - `moved_files`: A list to store logs of moved files.
        - `deleted_folders`: A list to store paths of deleted directories.
        - `unknown_files`: A list to store files with unknown extensions.
        - `ex_folders`: A list to store file extensions of moved files.
        - `ex_unknown`: A list to store unknown file extensions.
        - `points`: A predefined separator for formatting logs.
    """
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    create_folders(FOLDERS)
    folders.append(current_folder)
    graphs_folder(current_folder)

    threads = []
    for folder in folders:
        for ind in range(5):
            threads.append(Thread(target=move_files, args=(folder, ind)))
            threads[-1].start()
    [th.join() for th in threads]
    delete_dir(current_folder)
    # printing
    print_logging_files(moved_files)
    print(points)
    print(f"Deleted empty folders:")
    for val in deleted_folders:
        print("{:^3}{:<40}".format("", f"{val}"))
    print(points)
    [
        print_files(v1, v2)
        for v1, v2 in zip(
            FOLDERS, ["Photo:", "Video:", "Documents:", "Music:", "Archives:"]
        )
    ]
    if unknown_files:
        (
            print("Next unknown file:")
            if len(unknown_files) == 1
            else print(f"Next unknown files:")
        )
        for val in set(unknown_files):
            print("{:^10}{:<40}".format("", f"{val}"))
    print(points)
    [
        print_extensions(v1, v2)
        for v1, v2 in zip(
            ex_folders,
            [
                "Image extensions:",
                "Video extensions:",
                "Documents extensions:",
                "Audio extensions:",
                "Archives extensions:",
            ],
        )
    ]
    print_extensions(ex_unknown, "Unknown extensions:")
    print(points)
    # unpacking and deleting archives
    for val in FOLDERS[4].iterdir():
        if val.suffix in EXTENSIONS[4]:
            name = val.name.split(".")
            fold_dir = FOLDERS[4].joinpath(name[0])
            fold_dir.mkdir(exist_ok=True, parents=True)
            shutil.unpack_archive(str(val), str(fold_dir))
            val.unlink(missing_ok=True)  # delete archive


if __name__ == "__main__":
    main()
