import asyncio
import logging
from typing import List, Dict, Any

from aiopath import AsyncPath

from clean_folder.additional import move_file, async_rmtree, unzip


logging.basicConfig(
    level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s"
)

# This will create new folders
new_directory = ["images", "video", "documents", "audio", "archives", "books"]
# The extensions that will move to created folders
EXTENSIONS_ = [
    [".jpeg", ".png", ".jpg", ".svg"],
    [".avi", ".mp4", ".mov", ".mkv"],
    [".doc", ".docx", ".txt", ".pdf", ".xlsx", ".pptx", ".ppt", ".djvu"],
    [".mp3", ".ogg", ".wav", ".amr", ".flac"],
    [".zip", ".tar", ".rar"],
    [".fb2"],
]

#  {".jpeg": "images", ".png": "images"}
EXTENSIONS = {"other": "other"}
for keys, value in zip(EXTENSIONS_, new_directory):
    for key in keys:
        EXTENSIONS[key] = value

moved_files = []
deleted_folders = []


async def read_folder(path: AsyncPath, base_dir: AsyncPath, extensions: Dict):
    """
    Recursively reads and processes files and directories in a specified folder.
    Files are moved to corresponding directories based on their extensions,
    and empty directories are deleted.

    Parameters:
        path (AsyncPath): The directory path to read and process.
        base_dir (AsyncPath): The base directory where files will be moved.
        extensions (Dict): A dictionary mapping file extensions to target directory names.

    Behavior:
        - Recursively iterates through the directory and its subdirectories.
        - Moves files to directories based on their extensions (as defined in `extensions`).
        - Deletes empty directories after processing.
        - Logs errors if file movement or directory deletion fails.

    Notes:
        - This function is useful for organizing files into specific directories based on their types.
        - It ensures that empty directories are cleaned up after processing.
        - Errors during file movement or directory deletion are logged for debugging.

    Examples:
        >>> await read_folder(AsyncPath("path/to/source"), AsyncPath("path/to/destination"), {".txt": "text_files", ".jpg": "images"})
        # Moves .txt files to "text_files" and .jpg files to "images", then deletes empty directories.
    """
    async for element in path.iterdir():
        if await element.is_dir() and element.name not in extensions.values():
            await read_folder(element, base_dir, extensions)
            empty = True
            async for _ in element.iterdir():
                empty = False
                break
            if empty:
                try:
                    deleted_folders.append(await async_rmtree(element))
                except OSError:
                    logging.error(f"Error with file {element} in folder {element}")
        else:
            if await element.is_file():
                if element.suffix in extensions.keys():
                    path_to_move = base_dir / extensions[element.suffix]
                else:
                    path_to_move = base_dir / "other"
                # move file
                try:
                    await path_to_move.mkdir(exist_ok=True, parents=True)
                    moved_files.append(await move_file(element, path, path_to_move))
                except OSError:
                    logging.error(f"Error with file {element.name} in folder {path}")


async def log_work(path: AsyncPath) -> dict:
    """
    Recursively logs the contents of a directory, including files and subdirectories,
    and counts the occurrences of each file extension.

    Parameters:
        path (AsyncPath): The directory path to log and analyze.

    Returns:
        dict: A nested dictionary where:
              - Keys are directory names or file extensions.
              - Values are either subdirectories' dictionaries or counts of file extensions.

    Behavior:
        - Recursively iterates through the directory and its subdirectories.
        - Prints the contents of each directory.
        - Counts the occurrences of each file extension in the directory.
        - Returns a nested dictionary representing the directory structure and file extension counts.

    Notes:
        - This function is useful for analyzing and logging the structure of a directory tree.
        - It prints the contents of each directory to the console for visibility.
        - The returned dictionary can be used for further analysis or reporting.

    Examples:
        >>> await log_work(AsyncPath("path/to/directory"))
        # Logs the contents of "path/to/directory" and returns a dictionary with file extension counts.
    """
    ext = {}
    async for element in path.iterdir():
        if await element.is_dir():
            print(f"{'-'*100}\nContent of {element}:")
            ext[str(element.name)] = await log_work(element)
        else:
            if await element.is_file():
                print(f"{' ':^10}{element.name:<40}")
                if str(element.suffix) not in ext.keys():
                    ext[str(element.suffix)] = 0
                ext[str(element.suffix)] += 1
    return ext


async def main(path: AsyncPath):
    """
    The main function that orchestrates file processing, including reading folders,
    unzipping archives, moving files, and logging results.

    Parameters:
        path (AsyncPath): The root directory path where the operations will be performed.

    Behavior:
        1. Reads and processes files in the specified directory using `read_folder`.
        2. Unzips archives in the directory using `unzip`.
        3. Prints a list of moved files and deleted folders.
        4. Logs the results of file extensions and their counts using `log_work`.
        5. Prints a summary of file extensions and their counts.

    Notes:
        - This function serves as the entry point for the file processing workflow.
        - It relies on other helper functions (`read_folder`, `unzip`, `log_work`) to perform
          specific tasks.
        - The results are printed to the console in a formatted manner.

    Examples:
        >>> await main(AsyncPath("path/to/directory"))
        # Processes files, unzips archives, moves files, and logs results.
    """
    await read_folder(path, path, EXTENSIONS)
    await unzip(path, new_directory[4])
    print(f"{'-'*100}\nMoved files:")
    for folder in moved_files:
        print(f"{' ':^10}{folder}")
    print(f"{'-'*100}\nRemoved from pc:")
    for folder in deleted_folders:
        print(f"{' ':^10}{folder}")
    ext_dict = await log_work(path)
    print(f"{'-'*200}\nExtensions of exists files:")
    for key_dir, val in ext_dict.items():
        print(f"{' ':^10}{key_dir}:")
        for key_ext, val_ext in val.items():
            print(f"{' ':^20}{key_ext:<10}{val_ext}")


if __name__ == "__main__":
    while True:
        command = input("Write path to clearn or 'exit' -> ")
        # folder_path = f"A:\\test"
        if command == "exit":
            break
        try:
            asyncio.run(main(AsyncPath(command)))
        except OSError:
            print("Wrong path")
