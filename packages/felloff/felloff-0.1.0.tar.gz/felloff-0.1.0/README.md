<!--
SPDX-FileCopyrightText: © 2025 scy

SPDX-License-Identifier: CC-BY-4.0
-->

# felloff

_Because, you know, [the front](https://www.youtube.com/watch?v=3m5qxZm_JqM)._


## Description

felloff is a command-line utility (and Python library) to handle [YAML Front Matter](https://gohugo.io/content-management/front-matter/) in text files.
It can retrieve it from a file, remove it, or change it based on command-line options.

felloff is using [ruamel.yaml](https://yaml.dev/doc/ruamel-yaml/) to read and write the YAML content, which means that formatting, structure, and comments should be preserved as much as possible when it's editing your files.


## Status

felloff is not yet feature complete, but already does a few useful things.
See the examples below for whether your particular use case is among them, and see the [issues list](https://codeberg.org/scy/felloff/issues) for what is probably yet to come.


## Requirements

felloff requires Python 3.10 or higher, as well as a couple of Python packages that will be auto-installed as dependencies when you install felloff.

The input files currently need to be UTF-8 encoded, with no byte order mark.
Other encodings might be supported in the future.

felloff will probably also change your line endings to Unix-style, if they're not already.


## Installation

You can install [felloff from PyPI](https://pypi.org/project/felloff/) using Python's normal packaging tools.

- with [uv](https://docs.astral.sh/uv/) (recommended): `uv tool install felloff` or even directly run it using `uvx felloff`
- with [pipx](https://pipx.pypa.io/): `pipx install felloff`


## CLI Usage

felloff comes with command line help, which can be accessed from the usual `-h` or `--help` switches.
For example, use `felloff -h` to get a list of supported commands, and `felloff set -h` to get the `set` command explained to you.

The following sections show you how to use each subcommand based on examples.

We're using the following example document `myfile.md`:

```yaml
---
title: An example document
created: 2025-06-06  # Start of the felloff project.
tags: [test, example]
---
This document will be used for **testing**.
```

Instead of a file, you can also use the special file name `-` to read from standard input.


### `front`: Retrieve the front matter

#### Extract the front matter from a Markdown file

```console
$ felloff front myfile.md
title: An example document
created: 2025-06-06  # Start of the felloff project.
tags: [test, example]
```

#### Convert the front matter into JSON

```console
$ felloff front -f json myfile.md
{"title": "An example document", "created": "2025-06-06", "tags": ["test", "example"]}
```


### `main`: Retrieve the main content

#### Extract the main content from a Markdown file

```console
$ felloff main myfile.md
This document will be used for **testing**.
```


### `set`: Change the front matter

By default, the modified file will be printed to standard output.
If you'd like to modify the original file instead, use the `-i/--in-place` argument.

Since you might want to use field names or values that start with a dash, `felloff set` is quite picky about the order of its arguments.
**The input file name has to be supplied before the list of requested changes.**

If you don't have field names or values that start with a dash (`-`), you probably don't need to take any special measures.
If you're calling felloff from a script, however, you should use `--` after the file name to stop Python's normal argument processing, and also check out features like `--json` or `--end-list-with` to work around ambiguity.

Also, make sure that you understand how to quote arguments in your shell, especially if you're using special characters or spaces.
Most of the time, using single quotes should help.

In general, you give `felloff set` a list of changes that you'd like to do.
These include the `TYPE` of the operation (which starts with a `-`), the `NAME` of the field to modify, and the actual `VALUE`.
You can request multiple of these changes in one invocation and they will be performed in order.

If you don't specify a `TYPE`, the default is to set string values (`--string`) or stay in whatever `TYPE` you set previously.

#### Set a string value

```console
$ felloff set myfile.md --string title 'My title'
---
title: My title
created: 2025-06-06  # Start of the felloff project.
tags: [test, example]
---
This document will be used for **testing**.
```

If the field doesn't exist yet, it will be created.

`--string` can be shortened to `-s`.

Since `--string` is the default, you can also omit it, except when you want to explicitly switch back from a different mode.

#### Set a JSON value

If you need to set something to a non-string value, you'll need to pass it as JSON.

```console
$ felloff set myfile.md --json draft true id 123 nonsense '{"fruit": "strawberry"}' -s title Messy
---
title: Messy
created: 2025-06-06  # Start of the felloff project.
tags: [test, example]
draft: true
id: 123
nonsense:
  fruit: strawberry
---
This document will be used for **testing**.
```

This example also demonstrates how to set multiple fields, and how to switch back to string fields.

You can shorten `--json` to `-j`.

#### Set or update a modification date

```console
$ felloff set myfile.md --time created 2025-06-07 modified now
---
title: An example document
created: 2025-06-07  # Start of the felloff project.
tags: [test, example]
modified: 2025-06-07 14:03:45.845667+02:00
---
This document will be used for **testing**.
```

As you can see, you can pass an ISO formatted [date](https://docs.python.org/3/library/datetime.html#datetime.date.fromisoformat) (or [date and time](https://docs.python.org/3/library/datetime.html#datetime.datetime.fromisoformat)), or use some special values to get the current time.

You can also use `today` instead of `now` to just use the date without a time.
And there's `utcnow` and `utctoday` if you'd like to convert the value to UTC instead of having it in your machine's timezone.

Note that this is using native YAML date/datetime values, not strings.

#### Set to a list of strings

```console
$ felloff set myfile.md --list tags foo bar
---
title: An example document
created: 2025-06-06  # Start of the felloff project.
tags: [foo, bar]
---
This document will be used for **testing**.
```

The list continues until you specify a new `TYPE`.

`--list` can be shortened to `-l`.

If you'd like felloff to create new lists as multi-line values, you can use `--yaml-new-lists block`.
The default style is the one with the angle brackets, `--yaml-new-lists flow`.
**Lists that already existed in the original will keep their style.**

#### Edit existing lists

You can use `--append` (`-a`) to extend an existing list with new values.
If there is no existing value, a new list with your items will be created.
If there _is_ an existing value, but it's not a list, it will be made into one.

You can use `--remove` (`-r`) to remove values from a list.
If there is no existing value, or the existing value is not a list, nothing happens.

Let's do a fancy example:

```console
$ felloff set myfile.md --yaml-new-lists block --append title 'Alternative title or something' -a tags fancy --remove tags example
---
title:
- An example document
- Alternative title or something
created: 2025-06-06  # Start of the felloff project.
tags: [test, fancy]
---
This document will be used for **testing**.
```

#### Deleting existing fields

Use `--delete` (`-d`) to remove specific fields from the existing set.

```console
$ felloff set myfile.md --delete title created
---
tags: [test, example]
---
This document will be used for **testing**.
```

#### Starting from scratch

You can use the `--clear` option (`-c`) to drop all existing front matter content before applying your requested changes.

```console
$ felloff set -c myfile.md title 'A fresh start'
---
title: A fresh start
---
This document will be used for **testing**.
```
