import os
from argparse import ArgumentParser, Namespace
from glob import glob

from reqlint import ReqLint


def parse_args() -> Namespace:
    args = ArgumentParser(
        prog="reqlint",
        description="Lint Python files for requests without timeout parameters.",
    )
    args.add_argument(
        "files",
        nargs="*",
        help="Files or directories to lint. If a directory is provided, all Python files within it will be checked.",
    )
    args.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        default=False,
        help="Recursively search for Python files in directories.",
    )
    return args.parse_args()


def collect_files(args) -> list[str]:
    retval = set()

    for filepath in args.files:
        if os.path.isdir(filepath):
            for file in glob(f"{filepath}/**/*.py", recursive=args.recursive):
                retval.add(file)
        elif os.path.isfile(filepath) and filepath.endswith(".py"):
            retval.add(filepath)
    return list(retval)


def Main():
    args = parse_args()
    files = collect_files(args)
    for filepath in files:
        with open(filepath, "r") as f:
            code = f.read()
            for error in ReqLint().lint(code):
                print(f"{filepath}: {error}")


if __name__ == "__main__":
    Main()
