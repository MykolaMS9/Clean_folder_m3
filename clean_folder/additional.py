import asyncio
import logging
import os
import re

from aiopath import AsyncPath
import aioshutil
import errno
import patoolib
import shutil
import stat


logging.getLogger("patool").setLevel(logging.ERROR)

CYRILLIC_SYMBOLS = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ"
TRANSLATION = (
    "a",
    "b",
    "v",
    "g",
    "d",
    "e",
    "e",
    "j",
    "z",
    "i",
    "j",
    "k",
    "l",
    "m",
    "n",
    "o",
    "p",
    "r",
    "s",
    "t",
    "u",
    "f",
    "h",
    "ts",
    "ch",
    "sh",
    "sch",
    "",
    "y",
    "",
    "e",
    "yu",
    "ya",
    "je",
    "i",
    "ji",
    "g",
)
TRANS = {}
for c, l in zip(CYRILLIC_SYMBOLS, TRANSLATION):
    TRANS[ord(c)] = l
    TRANS[ord(c.upper())] = l.upper()


async def normalize(file_name: str) -> str:
    """
    Normalizes a file name by replacing Cyrillic characters with their Latin equivalents
    and replacing all non-alphanumeric characters with an underscore "_".

    Parameters:
        file_name (str): The input string containing the file name to be normalized.

    Returns:
        str: The normalized string where:
             - Cyrillic characters are replaced with their Latin equivalents.
             - Non-alphanumeric characters are replaced with "_".

    Examples:
        >>> await normalize("файл_з_кирилицею.txt")
        "fail_z_kiryliceiu.txt"

        >>> await normalize("file_with_123_and_!@#.txt")
        "file_with_123_and____.txt"

        >>> await normalize("мій_документ.pdf")
        "mii_dokument.pdf"
    """
    word = []
    for val in file_name:
        if re.findall("[а-яА-ЯіІїЇґ]", val):
            word.append(TRANS[ord(val)])
        elif re.findall("[a-zA-Z0-9]", val):
            word.append(val)
        else:
            word.append("_")
    return "".join(word)


async def re_name(_name: str) -> str:
    """
    Renames a file by incrementing a numeric suffix or adding a new one if it doesn't exist.
    The function assumes that the numeric suffix is separated by an underscore "_".

    Parameters:
        _name (str): The input file name, including its extension.

    Returns:
        str: The renamed file name with an incremented numeric suffix or a new suffix added.

    Examples:
        >>> await re_name("file_1.txt")
        "file_2.txt"

        >>> await re_name("document.pdf")
        "document_1.pdf"

        >>> await re_name("data_10.csv")
        "data_11.csv"

        >>> await re_name("image.png")
        "image_1.png"
    """
    file_name, extension = _name.rsplit(".", 1)
    num = file_name.split("_")[-1]
    if num.isdigit():
        if "_" in file_name:
            return _name.replace(f"_{num}", f"_{int(num)+1}")
        return _name.replace(f"{num}", f"{num}_{1}")
    return _name.replace(file_name, f"{file_name}_{1}")


async def move_file(
    element: AsyncPath, exist_path: AsyncPath, path_to_move: AsyncPath
) -> str:
    """
    Moves a file from the source directory to the target directory, ensuring that the file name
    is normalized and unique in the target directory. If a file with the same name already exists,
    the function renames the file by incrementing a numeric suffix.

    Parameters:
        element (AsyncPath): The path to the file to be moved.
        exist_path (AsyncPath): The source directory path where the file currently resides.
        path_to_move (AsyncPath): The target directory path where the file will be moved.

    Returns:
        str: A message indicating the successful move of the file, including the target directory
             and the new file name.

    Raises:
        OSError: If an error occurs during the file move operation.

    Examples:
        >>> await move_file(AsyncPath("source/file.txt"), AsyncPath("source"), AsyncPath("target"))
        "target     <-- moved target/file.txt"

        >>> await move_file(AsyncPath("source/document_1.pdf"), AsyncPath("source"), AsyncPath("target"))
        "target     <-- moved target/document_2.pdf"
    """
    try:
        file_name: str = element.name
        _name, extension = file_name.rsplit(".", 1)
        file_name = await normalize(_name)
        file_name = f"{file_name}.{extension}"
        element_to_move = path_to_move.joinpath(file_name)
        while await element_to_move.exists():
            file_name = await re_name(file_name)
            element_to_move = path_to_move / file_name
        await aioshutil.move(element, element_to_move)
        return f"{str(path_to_move.name):<10} <-- moved {element_to_move}"
    except OSError:
        raise OSError(f"Error with file {element.name} in folder {exist_path}")


async def unzip(path: AsyncPath, archive_dir):
    """
    Extracts files from archives found in a specified directory and organizes them into subdirectories.
    Each archive is extracted into a folder named after the archive (without its extension),
    and the original archive file is deleted after extraction.

    Parameters:
        path (AsyncPath): The directory path to search for archives.
        archive_dir (str): The suffix of the subdirectories containing the archives.

    Behavior:
        - Iterates through all subdirectories in the specified path that end with `archive_dir`.
        - For each file in these subdirectories, checks if it is an archive.
        - Extracts the archive into a folder named after the archive (without its extension).
        - Deletes the original archive file after successful extraction.
        - Logs an error if extraction fails.

    Notes:
        - Uses `patoolib` for archive extraction.
        - Skips files without extensions.
        - Creates necessary directories if they do not exist.

    Examples:
        >>> await unzip(AsyncPath("path/to/archives"), "archive_dir")
        # Archives in "path/to/archives/archive_dir" are extracted into subfolders.
    """
    async for folder in path.iterdir():
        if await folder.is_dir() and folder.name.endswith(archive_dir):
            async for element in folder.iterdir():
                if not await element.is_dir():
                    try:
                        file_name = element.name.rsplit(".", 1)
                        if len(file_name) < 2:  # Перевіряємо наявність розширення
                            continue
                        path_to_move = folder / file_name[0]
                        await path_to_move.mkdir(exist_ok=True, parents=True)
                        await asyncio.to_thread(
                            patoolib.extract_archive,
                            str(element),
                            outdir=str(path_to_move),
                        )
                        await asyncio.to_thread(os.remove, str(element))
                    except OSError:
                        logging.error(f"Error with file: {element}")


async def handle_remove_readonly(func, path, exc):
    """
    Handles the removal of read-only files or directories by changing their permissions
    and retrying the operation. This function is designed to be used as an error handler
    for file or directory removal operations.

    Parameters:
        func (callable): The function that caused the error (e.g., `os.rmdir`, `os.remove`).
        path (str): The path to the file or directory that caused the error.
        exc (tuple): A tuple containing the exception type, value, and traceback.

    Behavior:
        - If the error is due to a permission issue (`errno.EACCES`), changes the file or
          directory permissions to `0777` (read, write, and execute for all users) and retries
          the operation.
        - If the error is not related to permissions, re-raises the exception.

    Notes:
        - This function is typically used with `shutil.rmtree` or similar functions to handle
          read-only files or directories during deletion.
        - Uses `asyncio.to_thread` to run synchronous I/O operations in a thread pool.

    Examples:
        >>> await handle_remove_readonly(os.remove, "readonly_file.txt", (PermissionError, PermissionError(13, 'Permission denied'), None))
        # Changes permissions of "readonly_file.txt" and retries the removal.
    """
    exc_value = exc[1]
    if func in (os.rmdir, os.remove) and exc_value.errno == errno.EACCES:
        await asyncio.to_thread(
            os.chmod, path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO
        )  # 0777
        await asyncio.to_thread(func, path)
    else:
        raise exc_value


async def async_rmtree(filename: AsyncPath):
    """
    Asynchronously removes a directory tree (including all files and subdirectories).
    Handles read-only files or directories by changing their permissions and retrying the removal.

    Parameters:
        filename (AsyncPath): The path to the directory to be removed.

    Returns:
        AsyncPath: The path of the removed directory.

    Behavior:
        - Uses `shutil.rmtree` to remove the directory tree.
        - Handles read-only files or directories by calling `handle_remove_readonly` to change
          permissions and retry the removal.
        - Runs the synchronous `shutil.rmtree` operation in a thread pool using `asyncio.to_thread`.

    Notes:
        - This function is useful for asynchronous environments where blocking I/O operations
          (like directory removal) need to be offloaded to a thread pool.
        - The `handle_remove_readonly_sync` function is a bridge between synchronous `shutil.rmtree`
          and the asynchronous `handle_remove_readonly` function.

    Examples:
        >>> await async_rmtree(AsyncPath("path/to/directory"))
        # Removes the directory tree at "path/to/directory" and returns the path.
    """
    loop = asyncio.get_running_loop()

    def sync_rmtree():
        shutil.rmtree(
            filename, ignore_errors=False, onerror=handle_remove_readonly_sync
        )

    def handle_remove_readonly_sync(func, path, exc):
        future = asyncio.run_coroutine_threadsafe(
            handle_remove_readonly(func, path, exc), loop
        )
        future.result()

    await asyncio.to_thread(sync_rmtree)
    return filename
