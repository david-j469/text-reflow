"""Command-line entry point."""
import argparse
import os
import sys

from . import __version__
from .core import wrap_text

DEFAULT_WIDTH = 72
CONFIG_FILENAME = ".reflowrc"


class InputError(Exception):
    """A file exists but can't be read as text, e.g. it isn't valid UTF-8."""

    def __init__(self, path, reason):
        super().__init__(f"{path}: {reason}")
        self.path = path
        self.reason = reason


def _read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        try:
            return f.read()
        except UnicodeDecodeError:
            raise InputError(path, "not valid UTF-8") from None


def read_input(paths):
    """Read and concatenate input from files, or from stdin if no files are given."""
    if not paths or paths == ["-"]:
        return sys.stdin.read()
    chunks = []
    for path in paths:
        if path == "-":
            chunks.append(sys.stdin.read())
        else:
            chunks.append(_read_file(path))
    return "\n\n".join(chunks)


def load_config_width(directory=None):
    """Look for a width setting in .reflowrc in `directory` (default: cwd).

    The file holds simple "key = value" lines; only "width" is recognized.
    Blank lines and "#" comments are ignored. Returns None if the file is
    missing or has no usable width line, so the caller can fall back to a
    default.
    """
    path = os.path.join(directory or os.getcwd(), CONFIG_FILENAME)
    if not os.path.isfile(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.split("#", 1)[0].strip()
            if not line or "=" not in line:
                continue
            key, _, value = line.partition("=")
            if key.strip() == "width":
                try:
                    return int(value.strip())
                except ValueError:
                    return None
    return None


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="reflow",
        description="Normalize messy hard-wrapped text and rewrap it to a fixed width.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="files to read (default: stdin). Use '-' to read stdin explicitly.",
    )
    parser.add_argument(
        "-w", "--width",
        type=int,
        default=None,
        help="target line width (default: 72, or the width set in .reflowrc)",
    )
    parser.add_argument(
        "-i", "--in-place",
        action="store_true",
        help="rewrite each input file with the wrapped text instead of printing to stdout",
    )
    args = parser.parse_args(argv)

    if args.width is None:
        args.width = load_config_width()
    if args.width is None:
        args.width = DEFAULT_WIDTH

    if args.in_place:
        if not args.files or "-" in args.files:
            parser.error("--in-place requires one or more real files, not stdin")
        exit_code = 0
        for path in args.files:
            try:
                text = _read_file(path)
                wrapped = wrap_text(text, width=args.width)
                with open(path, "w", encoding="utf-8") as f:
                    f.write(wrapped)
                    f.write("\n")
            except OSError as exc:
                print(f"reflow: {exc.filename}: {exc.strerror}", file=sys.stderr)
                exit_code = 1
            except InputError as exc:
                print(f"reflow: {exc.path}: {exc.reason}", file=sys.stderr)
                exit_code = 1
        return exit_code

    try:
        text = read_input(args.files)
    except OSError as exc:
        print(f"reflow: {exc.filename}: {exc.strerror}", file=sys.stderr)
        return 1
    except InputError as exc:
        print(f"reflow: {exc.path}: {exc.reason}", file=sys.stderr)
        return 1
    sys.stdout.write(wrap_text(text, width=args.width))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
