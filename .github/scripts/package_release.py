"""Create reader downloads from a published resource checkout."""

from __future__ import annotations

import argparse
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


LANGUAGES = ("zh-hans", "zh-hant", "en", "ja", "ko")
DOCUMENTS = ("\u9644\u5f55.md", "readme.md", "version.json")


def package_release(repository: Path, destination: Path) -> list[Path]:
    repository = repository.resolve(strict=True)
    destination = destination.resolve()
    if destination == repository or destination.is_relative_to(repository):
        raise ValueError("ZIP destination must be outside the resource checkout")
    files_by_language = {}
    for language in LANGUAGES:
        directory = repository / language
        if not directory.is_dir():
            raise FileNotFoundError(directory)
        files_by_language[language] = sorted(path for path in directory.rglob("*") if path.is_file())
    documents = [repository / name for name in DOCUMENTS]
    for document in documents:
        if not document.is_file():
            raise FileNotFoundError(document)
    destination.mkdir(parents=True, exist_ok=True)
    archives = []
    for language, files in files_by_language.items():
        archive = destination / f"{language}.zip"
        with ZipFile(archive, "w", compression=ZIP_DEFLATED, compresslevel=9) as zipped:
            for path in [*files, *documents]:
                zipped.write(path, path.relative_to(repository).as_posix())
        archives.append(archive)
    return archives


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repository", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    for archive in package_release(args.repository, args.destination):
        print(archive)
