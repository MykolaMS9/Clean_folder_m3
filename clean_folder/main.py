from typing import List
import shutil
from threading import Thread
import logging
import argparse
from pathlib import Path
from additional import normalize, check_name

"""
-f --folder -> path folder

python main.py -f C:/Users/MS/Desktop
"""

parser = argparse.ArgumentParser(description="App for sorting files in specific folder")
parser.add_argument('-f', '--folder', default=True)

args = vars(parser.parse_args())
folder_path = args.get('folder')
current_folder = Path(folder_path)
folders = []
points = '-' * 100

# created new folders
new_directory = ['images', 'video', 'documents', 'audio', 'archives']
FOLDERS = [current_folder.joinpath(new_dir) for new_dir in new_directory]
EXTENSIONS = [['.jpeg', '.png', '.jpg', '.svg'],
              ['.avi', '.mp4', '.mov', '.mkv'],
              ['.doc', '.docx', '.txt', '.pdf', '.xlsx', '.pptx', '.ppt', '.djvu'],
              ['.mp3', '.ogg', '.wav', '.amr', '.flac'],
              ['.zip', '.gz', '.tar']]
STR_EXTENSIONS = ''.join([''.join(val) for val in EXTENSIONS])


def create_folders(folders_list: List[Path]):
    for path_folder in folders_list:
        path_folder.mkdir(exist_ok=True, parents=True)


def graphs_folder(path: Path):
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
    log_list = [f'From folder //{str(fol_path.name)}// removed to //{new_directory[index]}// next files:']
    for element in fol_path.iterdir():
        if element.is_file() and element.suffix in EXTENSIONS[index]:
            namefile = FOLDERS[index].joinpath(f'{normalize(check_name(element, FOLDERS[index]))}{element.suffix}')
            shutil.move(element, namefile)
            ex_folders[index].append(element.suffix)
            if element.name == namefile.name:
                log_list.append('{:^10}{:<40}'.format('', f'{element.name}'))
            else:
                log_list.append('{:^10}{:<40}{:^7}{:<40}'.format('Renamed', f'{element.name}', '-->', f'{namefile.name}'))
        elif element.is_file() and element.suffix not in STR_EXTENSIONS:
            unknown_files.append(element.name)
            ex_unknown.append(element.suffix)
    moved_files.append(log_list)


def print_logging_files(file_list: List[List[Path]]):
    for val in file_list:
        if len(val) > 1:
            print(points)
            for val_ in val:
                print(val_)
                # print('{:^5}{:<40}'.format('', f'{val_}'))


def print_files(path, text):
    if path:
        print(text)
        for val in path.iterdir():
            print('{:^10}{:<40}'.format('', f'{val.name}'))


def print_extensions(value, text):
    if value:
        print(text)
        print('{:^15}{:<50}'.format('', f'{", ".join(set(value))}'))


def delete_dir(path: Path):
    if path not in FOLDERS:
        for element in path.iterdir():
            if element.is_dir():
                delete_dir(element)
        if not any(path.iterdir()):
            deleted_folders.append(path)
            path.rmdir()


def main():
    logging.basicConfig(level=logging.INFO, format='%(message)s')
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
    print(f'Deleted empty folders:')
    for val in deleted_folders:
        print('{:^3}{:<40}'.format('', f'{val}'))
    print(points)
    [print_files(v1, v2) for v1, v2 in zip(FOLDERS, ['Photo:', 'Video:', 'Documents:', 'Music:', 'Archives:'])]
    if unknown_files:
        print('Next unknown file:') if len(unknown_files) == 1 else print(f'Next unknown files:')
        for val in set(unknown_files):
            print('{:^10}{:<40}'.format('', f'{val}'))
    print(points)
    [print_extensions(v1, v2) for v1, v2 in zip(ex_folders,
                                                ['Image extensions:', 'Video extensions:', 'Documents extensions:',
                                                 'Audio extensions:', 'Archives extensions:'])]
    print_extensions(ex_unknown, 'Unknown extensions:')
    print(points)
    # unpacking and deleting archives
    for val in FOLDERS[4].iterdir():
        if val.suffix in EXTENSIONS[4]:
            name = val.name.split('.')
            fold_dir = FOLDERS[4].joinpath(name[0])
            fold_dir.mkdir(exist_ok=True, parents=True)
            shutil.unpack_archive(str(val), str(fold_dir))
            val.unlink(missing_ok=True)  # delete archive


if __name__ == '__main__':
    main()
