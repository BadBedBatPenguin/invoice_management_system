import shutil
from pathlib import Path

from fastapi import UploadFile


def get_unique_filename(directory: Path, filename: str) -> Path:
    directory.mkdir(parents=True, exist_ok=True)

    file_path = directory / filename
    if not file_path.exists():
        return file_path

    stem = file_path.stem
    suffix = file_path.suffix
    counter = 1

    while True:
        new_filename = f"{stem} ({counter}){suffix}"
        new_file_path = directory / new_filename
        if not new_file_path.exists():
            return new_file_path
        counter += 1


def save_to_file_system(path: Path, file: UploadFile):
    with path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
