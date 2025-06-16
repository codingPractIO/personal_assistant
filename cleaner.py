import os
import shutil

def remove_file(file_path):
    """
    Completely removes the specified file from the filesystem.
    :param file_path: Path to the file to be deleted.
    """
    if os.path.isfile(file_path):
        os.remove(file_path)

def move_to_archive(file_path, archive_folder="archive"):
    """
    Moves the specified file to the archive folder.
    :param file_path: Path to the file to be moved.
    :param archive_folder: Folder where the file will be moved (default: 'archive').
    """
    if not os.path.isfile(file_path):
        return

    os.makedirs(archive_folder, exist_ok=True)
    destination = os.path.join(archive_folder, os.path.basename(file_path))
    shutil.move(file_path, destination)
