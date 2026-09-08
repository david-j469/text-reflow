# reflow

A small command-line tool that fixes text with bad line wrapping.

Text pasted from an email client, exported from a PDF, or copied out of a
terminal often has hard newlines in the middle of sentences, at whatever
width the source happened to use. Editing it is annoying because every line
break is fake except the paragraph breaks. `reflow` throws away the fake
breaks and rewraps each paragraph to a width you choose.

## Usage

From a file:

```
$ reflow notes.txt
```

From stdin:

```
$ cat notes.txt | reflow
$ pbpaste | reflow -w 80
```

Multiple files are concatenated (with a blank line between them) before
wrapping:

```
$ reflow chapter1.txt chapter2.txt
```

To rewrite files in place instead of printing to stdout, add `-i` (or
`--in-place`). Each file is wrapped and overwritten separately, so this
one doesn't do the multi-file concatenation above:

```
$ reflow -i --width 80 notes.txt
```

`-i` requires at least one real file; it doesn't make sense with stdin.

`reflow --version` prints the installed version and exits.

If you don't want to pass `-w` every time, drop a `.reflowrc` in the
current directory with a `width` line:

```
width = 80
```

`#` starts a comment, blank lines are ignored, and `width` is the only
setting read right now. An explicit `-w` on the command line always wins
over the file.

Example. Given this input, where the paragraph was hard-wrapped at some
arbitrary width and then edited so the lines no longer line up:

```
This is a paragraph that was
wrapped a while ago at a narrow width and then
someone added a clause in the middle without
rewrapping it so now the lines are ragged.

Second paragraph, short.
```

Running `reflow -w 40` produces:

```
This is a paragraph that was wrapped a
while ago at a narrow width and then
someone added a clause in the middle
without rewrapping it so now the lines
are ragged.

Second paragraph, short.
```

Blank lines are preserved as paragraph breaks; everything else about the
original layout is discarded.

## Install

No dependencies beyond the standard library. Run it straight from a checkout:

```
$ python -m reflow.cli notes.txt
```

or install it locally:

```
$ pip install .
$ reflow notes.txt
```

## Status

Early. Paragraphs are split on blank lines; bullet and numbered list items
are detected and kept on their own line with a hanging indent instead of
being merged into the paragraph around them. Lines indented with a tab or
4+ spaces are treated as a code block and passed through unwrapped.
Markdown headers aren't handled specially yet. See the issues for what's
planned.
