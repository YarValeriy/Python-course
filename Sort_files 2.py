import os
import shutil
import zipfile
import tarfile
import sys

c_symbols = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ!@$%^&*()-+=:;'"
l_symbols = (
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
    "_",
    "_",
    "_",
    "_",
    "_",
    "_",
    "_",
    "_",
    "_",
    "_",
    "_",
    "_",
    "_",
    "_",
    "_",
)

trans = {}
for c, l in zip(c_symbols, l_symbols):
    trans[ord(c)] = l
    trans[ord(c.upper())] = l.upper()


def normalize(string):
    return string.translate(trans)


def sort_files(folder_path):
    n_files = 0
    # Define folder names for each category
    categories = {
        "Images": ["JPEG", "PNG", "JPG", "SVG"],
        "Video": ["AVI", "MP4", "MOV", "MKV"],
        "Documents": ["DOC", "DOCX", "TXT", "PDF", "XLS", "XLSX", "PPT", "PPTX"],
        "Audio": ["MP3", "OGG", "WAV", "AMR", "M4A"],
        "Archives": ["ZIP", "GZ", "TAR"],
        "Code": ["PY", "CPP", "CXX", "CC"],
        "Markup": ["XML", "HTML", "CSS"],
        "Unknown": [],
    }

    # Create folders if they don't exist
    for category in categories:
        category_folder = os.path.join(folder_path, category)
        if not os.path.exists(category_folder):
            os.makedirs(category_folder)

    # Loop through all files and move them to the appropriate folders
    for root, dirs, files in os.walk(folder_path):
        files = [f for f in files if not f[0] == "."]  # skip hidden files
        # dirs[:] = [d for d in dirs if not d[0] == "."]  # skip hidden folders
        dirs[:] = [
            d for d in dirs if not d in list(categories.keys())
        ]  # skip service folders

        for file in files:
            split_name = file.split(".")
            if len(split_name) == 1:
                file_ext = ""
                n_file = normalize(split_name[0])
            else:
                file_ext = split_name[-1].upper()
                n_file = normalize(split_name[0]) + "." + file_ext.lower()
            file_path = os.path.join(root, file)

            # Find the category for the file
            file_category = "Unknown"
            for category, extensions in categories.items():
                if file_ext in extensions:
                    file_category = category
                    break
            if file_category == "Unknown":
                categories["Unknown"].append(file_ext)

            # Move the file to the appropriate folder
            destination_folder = os.path.join(folder_path, file_category)
            shutil.move(file_path, os.path.join(destination_folder, n_file))
            n_files += 1

    # Unpack archive files
    archives_folder = os.path.join(folder_path, "Archives")
    for root, dirs, files in os.walk(os.path.join(folder_path, "Archives")):
        for file in files:
            file_path = os.path.join(root, file)
            archive_name = file.split(".")[0]
            archive_folder = os.path.join(archives_folder, archive_name)
            # print(archive_folder)

            # Create a subfolder for the archive if it doesn't exist
            if not os.path.exists(archive_folder):
                os.makedirs(archive_folder)

            # Unpack the archive and move its contents to the subfolder
            if file.endswith(".zip"):
                with zipfile.ZipFile(file_path, "r") as zip_ref:
                    try:
                        zip_ref.extractall(archive_folder)  # names not nornmalized
                        os.remove(file_path)
                    except IOError as e:
                        print(f"Archive {file_path} corrupted!", e)
            elif file.endswith(".tar") or file.endswith(".gz"):  # never tested
                with tarfile.open(file_path, "r") as tar_ref:  # never tested
                    try:
                        tar_ref.extractall(archive_folder)  # never tested
                        os.remove(file_path)
                    except IOError as e:
                        print(f"Archive {file_path} corrupted!", e)

    # Remove empty folders
    for root, dirs, _ in os.walk(folder_path, topdown=False):
        for folder in dirs:
            folder_path = os.path.join(root, folder)
            # print(folder_path)
            sub_dirs = os.listdir(folder_path)
            sub_dirs = [
                sub for sub in sub_dirs if not sub[0] == "."
            ]  # ignore hidden subfolders when deleting folder
            # if not os.listdir(folder_path):
            if not sub_dirs:
                # os.rmdir(folder_path)
                shutil.rmtree(folder_path, ignore_errors=True)
                # print(f"{folder_path} deleted")
    return (n_files, categories["Unknown"])


if __name__ == "__main__":
    if len(sys.argv) < 2:
        folder_to_sort = input("Enter the folder path: ")
    else:
        folder_to_sort = sys.argv[1]
    response = sort_files(folder_to_sort)
    print(
        f"Files at {folder_to_sort} sorted successfully, {response[0]} files relocated, unknown extensions: {response[1]}"
    )
