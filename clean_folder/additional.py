import re
from pathlib import Path

newname = 1

CYRILLIC_SYMBOLS = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ"
TRANSLATION = ("a", "b", "v", "g", "d", "e", "e", "j", "z", "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
               "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e", "yu", "ya", "je", "i", "ji", "g")
TRANS = {}
for c, l in zip(CYRILLIC_SYMBOLS, TRANSLATION):
    TRANS[ord(c)] = l
    TRANS[ord(c.upper())] = l.upper()


def normalize(file_name: Path().name):
    word = []
    for val in file_name:
        if re.findall('[а-яА-ЯіІїЇґ]', val):
            word.append(TRANS[ord(val)])
        elif re.findall('[a-zA-Z0-9]', val):
            word.append(val)
        else:
            word.append('_')
    return ''.join(word)


def check_name(exsistPath: Path, destinationPath: Path):
    global newname
    if destinationPath.joinpath(exsistPath.name).exists():
        newname += 1
        new_name = f'{str(exsistPath.name).replace(exsistPath.suffix, "")}_{newname}'
    else:
        new_name = str(exsistPath.name).replace(exsistPath.suffix, "")
    return new_name
