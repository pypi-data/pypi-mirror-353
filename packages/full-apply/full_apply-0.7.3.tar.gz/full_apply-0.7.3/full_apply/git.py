import subprocess as sp
from pathlib import Path

# TODO Use proper Git library

# TODO This relies on being executed from within the Git repo; should instead
# TODO find Git repo root & execute from there, adjusting paths as necessary


def is_tracked(path: Path) -> bool:
    # Stolen from: https://stackoverflow.com/a/2406813/2748899
    cp = sp.run(
        ["git", "ls-files", "--error-unmatch", "--", path], stderr=sp.DEVNULL
    )
    return cp.returncode == 0


def add(path: Path) -> None:
    sp.run(["git", "add", "--", path], check=True)


def mv(old: Path, new: Path) -> None:
    sp.run(["git", "mv", "--", old, new], check=True)
