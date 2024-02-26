import os
import shutil
import sys
import re
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

# Define file extension categories
CATEGORIES = {
    "images": ['jpeg', 'png', 'jpg', 'svg'],
    "video": ['avi', 'mp4', 'mov', 'mkv'],
    "documents": ['doc', 'docx', 'txt', 'pdf', 'xlsx', 'pptx'],
    "music": ['mp3', 'ogg', 'wav', 'amr'],
    "archives": ['zip', 'rar', 'gz', 'tar']
}

# Dictionary for transliterating Cyrillic symbols to Latin equivalents
CYRILLIC_SYMBOLS = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюяєії'
TRANSLATION = ('a', 'b', 'v', 'g', 'd', 'e', 'e', 'zh', 'z', 'i', 'y',
               'k', 'l', 'm', 'n', 'o', 'p', 'r', 's', 't', 'u', 'f',
               'kh', 'ts', 'ch', 'sh', 'shch', '', 'y', '', 'e', 'yu',
               'ya', 'ye', 'i', 'yi')

TRANS = {}

# Fill out the transliteration from Cyrillic to Latin
for cyr, lat in zip(CYRILLIC_SYMBOLS, TRANSLATION):
    TRANS[ord(cyr)] = lat
    TRANS[ord(cyr.upper())] = lat.upper()


def normalise(filename):
    """
    Normalises the filename by transliterating Cyrillic characters to Latin,
    replacing spaces with underscores, and removing all non-alphanumeric
    characters (except for the dot used in file extensions).

    Parameters:
        filename (str): The original filename to be normalized.

    Returns:
        str: The normalized filename.
    """
    normal_name = filename.translate(TRANS)
    normal_name = re.sub(r'\W', '_', normal_name)
    return normal_name


# Initialise dictionary to track files by category
file_info = {category: [] for category in CATEGORIES}
file_info["unknown"] = []

# Sets to keep track of known and unknown file extensions
known_extensions = set()
unknown_extensions = set()


def process_file(item_path, base_path):
    """
    Processes a single file by determining its category based on the file
    extension, moving it to the corresponding directory within the base_path,
    and handling archives by unpacking them.

    Parameters:
        item_path (str): The full path to the file being processed.
        base_path (str): The base directory where the categorized folders
                         are located.

    Returns:
        str: The category of the processed file.
    """
    _, ext = os.path.splitext(item_path)
    ext = ext.lstrip('.').lower()
    category = None
    for cat, exts in CATEGORIES.items():
        if ext in exts:
            category = cat
            known_extensions.add(ext)
            break
    if category is None:
        category = "unknown"
        unknown_extensions.add(ext)

    new_name = (normalise(os.path.splitext(os.path.basename(item_path))[0]) +
                '.' + ext)
    target_dir = os.path.join(base_path, category)
    os.makedirs(target_dir, exist_ok=True)
    shutil.move(item_path, os.path.join(target_dir, new_name))
    file_info[category].append(new_name)

    # Special handling for archives
    if category == "archives":
        archive_dir = os.path.join(target_dir, new_name.rsplit('.', 1)[0])
        os.makedirs(archive_dir, exist_ok=True)
        try:
            shutil.unpack_archive(os.path.join(target_dir, new_name),
                                  archive_dir)
        except shutil.ReadError:
            print("Warning: Unable to unpack archive",
                  f"{os.path.join(target_dir, new_name)}")

    return category


def remove_empty_folders(path):
    """
    Recursively removes empty folders from a specified path.

    Parameters:
        path (str): The root path from which empty folders will be removed.

    Returns:
        None
    """
    for dirpath, dirnames, filenames in os.walk(path, topdown=False):
        if not dirnames and not filenames:
            os.rmdir(dirpath)
            # print(f"Removed empty folder: {dirpath}")


def process_folder(folder_path: str, base_path: str):
    """
    Processes all files within a folder recursively, categorising them, moving
    to the appropriate directory, and unpacking archives if necessary.
    Uses ThreadPoolExecutor to parallelize processing.

    Parameters:
        folder_path (str): The path to the folder to process.
        base_path (str): The base path where categorized folders
                         will be stored.

    Returns:
        None
    """
    with ThreadPoolExecutor() as executor:
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            if os.path.isdir(item_path):
                # Submit directory processing to the executor
                executor.submit(process_folder, item_path, base_path)
            else:
                # Submit file processing to the executor
                executor.submit(process_file, item_path, base_path)
    # Remove empty folders after processing
    remove_empty_folders(folder_path)


def main(folder_path: str):
    """
    Main function that validates the input folder path, processes the folder
    by categorising its contents, and prints the result of processed files.

    Parameters:
        folder_path (str): The path to the folder to be processed.

    Returns:
        None
    """
    folder = Path(folder_path)
    if not folder.is_dir():
        print("The provided path is not a valid directory.")
        sys.exit(1)

    process_folder(folder_path, folder_path)

    # Print file information
    for category, files in file_info.items():
        if files:
            print(f"{category.capitalize()}:")
            for file in files:
                print(f" - {file}")

    # Print known and unknown extensions
    print("Known extensions:", known_extensions)
    print("Unknown extensions:", unknown_extensions)


def console_script():
    """
    Entry point for the console script. Validates command line arguments and
    executes the main function with the provided folder path.

    Parameters:
        None

    Returns:
        None
    """
    if len(sys.argv) != 2:
        print("Usage: file-sorter <path_to_folder>")
        sys.exit(1)

    main(sys.argv[1])


if __name__ == "__main__":
    console_script()
