"""Create or verify a personal installation without replacing existing content."""

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path


DEFAULT_SOURCE = (
    Path(__file__).resolve().parents[1]
    / ".github" / "skills" / "case-session-to-wiki"
)


class InstallError(ValueError):
    pass


def is_link(path):
    return path.is_symlink() or bool(
        getattr(path.lstat(), "st_file_attributes", 0) & 0x400
    )


def check_parents(path):
    for item in (path, *path.parents):
        if item.exists() and is_link(item):
            raise InstallError("Linked or reparse-point installation paths are not supported.")


def manifest(folder):
    if not folder.is_dir() or not (folder / "SKILL.md").is_file():
        raise InstallError("The skill directory must contain SKILL.md.")
    result = {}
    for path in sorted(folder.rglob("*")):
        if is_link(path):
            raise InstallError("The skill bundle must not contain links or reparse points.")
        if path.is_file():
            relative = path.relative_to(folder)
            if "__pycache__" in relative.parts or path.suffix == ".pyc":
                continue
            result[relative.as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def install(source, destination):
    source = Path(source).absolute()
    destination = Path(destination).absolute()
    check_parents(source)
    check_parents(destination)
    expected = manifest(source)
    if destination.exists():
        if manifest(destination) != expected:
            raise InstallError(
                "Destination differs; refusing to overwrite. Review local edits and "
                "use a new explicitly selected destination for a staged upgrade."
            )
        return {"status": "unchanged", "files_verified": len(expected)}
    if destination.is_relative_to(source):
        raise InstallError("An installation must not be nested inside its source bundle.")
    destination.parent.mkdir(parents=True, exist_ok=True)
    check_parents(destination.parent)
    try:
        shutil.copytree(
            source, destination,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
        )
    except OSError as error:
        raise InstallError(
            "Installation failed; a partial destination may remain. Inspect it before retrying."
        ) from error
    if manifest(destination) != expected:
        raise InstallError("Installation hash verification failed; no success is claimed.")
    return {"status": "installed", "files_verified": len(expected)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument(
        "--destination", type=Path,
        default=Path.home() / ".copilot" / "skills" / "case-session-to-wiki",
    )
    args = parser.parse_args(argv)
    try:
        result = install(args.source, args.destination)
    except (InstallError, OSError) as error:
        message = str(error) if isinstance(error, InstallError) else "Cannot access installation files."
        print(json.dumps({"status": "failed", "error": message}))
        return 1
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
