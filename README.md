# File Organizer and Processor

This project provides a set of asynchronous Python functions to organize, process, and clean up files and directories. It includes features such as file normalization, archive extraction, directory cleanup, and logging of file extensions.

## Features

- **File Normalization**: Normalizes file names by replacing Cyrillic characters with Latin equivalents and replacing non-alphanumeric characters with underscores.
- **Archive Extraction**: Extracts files from archives and organizes them into subdirectories named after the archive.
- **Directory Cleanup**: Recursively removes empty directories and handles read-only files during deletion.
- **File Organization**: Moves files to specific directories based on their extensions.
- **Logging**: Logs the structure of directories and counts file extensions for analysis.

# Installation
1. **Install Dependencies**:
   This project uses Poetry for dependency management. Follow these steps to set up the environment:
   Install Poetry (if not already installed):
   
   ```bash
   pip install poetry
   ```


2. **Clone the repository (if you haven't already):**
   Ensure you have Python 3.7+ installed. Install the required libraries using:
   ```bash
   git clone https://github.com/MykolaMS9/folder_organizer.git
   cd file-organizer
   ```
3. **Set up the virtual environment and install dependencies:**
   Run the following command to create a virtual environment and install all required dependencies:
   ```bash
   poetry install
   ```

4. **Activate the virtual environment:**
After installing dependencies, activate the virtual environment:
   ```bash
   poetry shell
   ```
   
5. **Verify installation:**
Ensure all dependencies are installed correctly by running:
   ```bash
   poetry check
   ```
   
## Example
   Here’s how you can install and set up the project using Poetry:

   ```bash
   # Clone the repository
   git clone https://github.com/your-repo/file-organizer.git
   cd file-organizer
   
   # Install dependencies using Poetry
   poetry install
   
   # Activate the virtual environment
   poetry shell
   
   # Run the project
   python main.py
   ```

# Usage

1. **Run program with `python main.py`**
   ```bash
   python main.py
   ```
2. **Specify the path to the directory containing the files to be organized and processed.**
   ```bash
   Write path to clean or 'exit' -> C:\Users\YourName\Documents\TestFolder
   ```
3. **The program will process the files and organize them into subdirectories based on their extensions.**
   ```bash
   ----------------------------------------------------------------------------------------------------
   Moved files:
              C:\Users\YourName\Documents\TestFolder\text_files\file1.txt
              C:\Users\YourName\Documents\TestFolder\images\photo1.jpg
   ----------------------------------------------------------------------------------------------------
   Removed from pc:
              C:\Users\YourName\Documents\TestFolder\empty_folder
   ----------------------------------------------------------------------------------------------------
   Extensions of exists files:
              text_files:
                         .txt       5
              images:
                         .jpg       3
   ```
## Documentation
   Full documentation is available by sending: [Documentation](https://MykolaMS9.github.io/folder_organizer)

## Functions Overview

### `normalize(file_name: str) -> str`
Normalizes a file name by replacing Cyrillic characters with Latin equivalents and non-alphanumeric characters with underscores.

### `re_name(_name: str) -> str`
Renames a file by incrementing a numeric suffix or adding a new one if it doesn't exist.

### `move_file(element: AsyncPath, exist_path: AsyncPath, path_to_move: AsyncPath) -> str`
Moves a file to a target directory, ensuring the file name is normalized and unique.

### `unzip(path: AsyncPath, archive_dir: str)`
Extracts files from archives in a specified directory and organizes them into subdirectories.

### `handle_remove_readonly(func, path, exc)`
Handles the removal of read-only files or directories by changing their permissions and retrying the operation.

### `async_rmtree(filename: AsyncPath) -> AsyncPath`
Asynchronously removes a directory tree, handling read-only files or directories.

### `log_work(path: AsyncPath) -> dict`
Recursively logs the contents of a directory and counts the occurrences of each file extension.

### `read_folder(path: AsyncPath, base_dir: AsyncPath, extensions: Dict)`
Recursively processes files and directories, moving files based on their extensions and deleting empty directories.

### `main(path: AsyncPath)`
The main function that orchestrates file processing, including reading folders, unzipping archives, moving files, and logging results.

