"""Command-line entry point."""
import argparse
import sys

from .core import wrap_text


def read_input(paths):
    """Read and concatenate input from files, or from stdin if no files are given."""
    if not paths or paths == ["-"]:
        return sys.stdin.read()
    chunks = []
    for path in paths:
        if path == "-":
            chunks.append(sys.stdin.read())
        else:
            with open(path, "r", encoding="utf-8") as f:
                chunks.append(f.read())
    return "\n\n".join(chunks)


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="reflow",
        description="Normalize messy hard-wrapped text and rewrap it to a fixed width.",
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="files to read (default: stdin). Use '-' to read stdin explicitly.",
    )
    parser.add_argument(
        "-w", "--width",
        type=int,
        default=72,
        help="target line width (default: 72)",
    )
    args = parser.parse_args(argv)

    text = read_input(args.files)
    sys.stdout.write(wrap_text(text, width=args.width))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
