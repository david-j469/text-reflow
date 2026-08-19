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

Early. Paragraph detection is "blank line separates paragraphs" and nothing
smarter yet - it doesn't know about bullet lists, indented code blocks, or
Markdown headers. See the issues for what's planned.
