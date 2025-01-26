import re
from pathlib import Path

newname = 1

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


def normalize(file_name: Path().name):
    """
    Normalizes a file name by replacing non-alphabetic characters and Cyrillic letters with Latin equivalents.

    The function iterates through each character in the file name and:
    - Replaces Cyrillic letters with their Latin equivalents using the `TRANS` dictionary.
    - Leaves Latin letters and digits unchanged.
    - Replaces all other characters with an underscore (_).

    Parameters:
        file_name (str): The file name to be normalized.

    Returns:
        str: The normalized file name.

    Example:
        >>> normalize("файл_з_кирилицею.txt")
        'fail_z_kiryliceiu.txt'
        >>> normalize("file_with_special_chars@#$.txt")
        'file_with_special_chars__.txt'
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


def check_name(exsistPath: Path, destinationPath: Path):
    """
    Checks if a file with the same name already exists in the destination path and generates a unique name if necessary.

    If a file with the same name already exists in the destination path, the function appends a number to the file name
    to make it unique. Otherwise, it returns the original file name without modification.

    Parameters:
        existPath (Path): The path of the existing file whose name needs to be checked.
        destinationPath (Path): The destination directory where the file will be moved or copied.

    Returns:
        str: A unique file name. If a file with the same name exists, it appends a number (e.g., `file_1`).
             Otherwise, it returns the original file name.

    Example:
        >>> check_name(Path("example.txt"), Path("destination_folder"))
        'example'  # If no file with the same name exists in the destination folder.
        >>> check_name(Path("example.txt"), Path("destination_folder"))
        'example_1'  # If a file named 'example' already exists in the destination folder.
    """
    global newname
    if destinationPath.joinpath(exsistPath.name).exists():
        newname += 1
        new_name = f'{str(exsistPath.name).replace(exsistPath.suffix, "")}_{newname}'
    else:
        new_name = str(exsistPath.name).replace(exsistPath.suffix, "")
    return new_name
