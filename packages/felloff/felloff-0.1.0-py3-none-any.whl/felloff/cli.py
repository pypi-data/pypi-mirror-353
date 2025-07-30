# SPDX-FileCopyrightText: © 2025 scy
#
# SPDX-License-Identifier: MIT

import contextlib
import datetime
import json
import shutil
import sys
import tempfile
import textwrap
from argparse import (
    ArgumentParser,
    FileType,
    Namespace,
    RawDescriptionHelpFormatter,
)
from enum import Enum
from pathlib import Path
from typing import Any, TextIO


class JSONEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:  # noqa: ANN401
        if isinstance(o, datetime.date):
            return o.isoformat()
        return super().default(o)


def wrap(text: str) -> str:
    return "\n".join(textwrap.wrap(text, shutil.get_terminal_size().columns))


def add_input_file_arg(parser: ArgumentParser) -> None:
    parser.add_argument(
        "input",
        type=FileType("r"),
        help="input file to read (use `-` for standard input)",
    )


def prepare() -> ArgumentParser:
    parser = ArgumentParser()

    subparsers = parser.add_subparsers(
        metavar="COMMAND",
        help="One of the following subcommands:",
        required=True,
    )

    parser_front = subparsers.add_parser(
        "front",
        help="print the file's front matter",
        description="Return the front matter of a given input.",
    )
    parser_front.add_argument(
        "-d",
        "--delimiters",
        action="store_true",
        dest="delimiters",
        help="include the original front matter delimiters in the output",
    )
    parser_front.add_argument(
        "-D",
        "--no-delimiters",
        action="store_false",
        dest="delimiters",
        help="don't include the delimiters in the output (the default)",
    )
    parser_front.add_argument(
        "-f",
        "--format",
        choices=("original", "json"),
        default="original",
        help="select the output format (default: %(default)s)",
    )
    parser_front.set_defaults(func=front_action)
    add_input_file_arg(parser_front)

    parser_main = subparsers.add_parser(
        "main",
        help="print the file's main content, without the front matter",
        description="Return the main content of a given input, without any "
        "front matter.",
    )
    parser_main.set_defaults(func=main_action)
    add_input_file_arg(parser_main)

    parser_set = subparsers.add_parser(
        "set",
        usage="%(prog)s [options] input CHANGES...",
        help="set front matter values",
        formatter_class=RawDescriptionHelpFormatter,
        description=wrap("Set one or more front matter values.")
        + "\n\n"
        + wrap(
            "CHANGES is a list of one or more changes that you'd like to "
            "apply. Each consists of a TYPE, a NAME, and a VALUE, provided as "
            "separate arguments. Sometimes, one or the other are optional; "
            "see the following paragraphs for details."
        )
        + "\n\n"
        + wrap("TYPE is one of the following flags:")
        + "\n"
        "  -s, --string  parse the following values as strings\n"
        "  -j, --json    parse the following values as JSON\n"
        "  -t, --time    parse the following values as date or datetime "
        "(see below)\n"
        "  -l, --list    parse the following values as a list of strings "
        "(see below)\n"
        "  -a, --append  like --list, but append to existing list (if any)\n"
        "  -r, --remove  like --list, but remove from existing list (if any)\n"
        "  -d, --delete  delete the given field(s), don't specify VALUEs\n"
        + wrap("If you don't specify a TYPE, the default is --string.")
        + "\n\n"
        + wrap(
            "NAME is the name of the front matter field and always required. "
            "Names starting with `-` are supported, but only immediately "
            "after a TYPE, because this is where they are not ambiguous. In "
            "other words, if you call `%(prog)s` from a script and don't know "
            "the names in advance, it is recommended to repeat the TYPE "
            "before each NAME. Also, names that look like one of the options "
            "listed below (e.g. `--help`) will only work if you use `--` to "
            "stop option parsing before listing your CHANGES."
        )
        + "\n\n"
        + wrap(
            "VALUE is the value you'd like to set and always required, except "
            "in combination with --delete, in which case you must not specify "
            "a VALUE until you have selected another TYPE."
        )
        + "\n\n"
        + wrap(
            "For --time values, the accepted formats are ISO dates (e.g. "
            "2025-06-06) and ISO datetimes (e.g. 2025-06-06T12:34+0200), as "
            "understood by Python's date.fromisoformat and "
            "datetime.fromisoformat. Alternatively, you may use the literal "
            "values `now` or `today` to get the current local datetime or "
            "date. If you use `utcnow` or `utctoday`, the values will be "
            "converted to universal time."
        )
        + "\n\n"
        + wrap(
            "With --list (and --append, and --replace), the next arguments "
            "(after the initial NAME) are interpreted as a list of strings, "
            "one per argument, until hitting an argument that starts with a "
            "`-`. To include values that start with `-` in the list, you "
            "should pass something like `--end-list-with . --` in your "
            "arguments. This will keep reading list items until it hits one "
            "that is exactly `.`, and also stop the normal argument parsing. "
            "You can set `--end-list-with` to any string, even the empty one "
            "(i.e. `--end-list-with ''`)."
        ),
        epilog=wrap("An example invocation would look like this:")
        + "\n\n  %(prog)s --in-place some-file.md "
        "author scy title 'My first post' "
        "-d draft review "
        "-j id 1 -l tags example post\n\n"
        + wrap(
            "It would set an author and title as well as two tags, and remove "
            "the `draft` and `review` fields, if they exist. It also sets the "
            "value of `id` to the number 1; using the JSON type is a nice "
            "trick to use non-string values."
        ),
    )
    parser_set.add_argument(
        "-c",
        "--clear",
        action="store_true",
        help="drop all existing front matter content",
    )
    parser_set.add_argument(
        "-i",
        "--in-place",
        action="store_true",
        help="write the result back to the input file",
    )
    parser_set.add_argument(
        "--end-list-with",
        metavar="TOKEN",
        help="keep reading list items even if they start with `-`, until "
        "the TOKEN is encountered",
    )
    parser_set.add_argument(
        "--yaml-new-lists",
        choices=["block", "flow"],
        default="flow",
        help="when creating new lists in YAML, should they use the compact "
        '"flow" style or the multi-line "block" style? (default: %(default)s)',
    )
    add_input_file_arg(parser_set)
    parser_set.set_defaults(func=set_action)

    return parser


def run(argv: list[str] | None = None) -> None:
    args, more = prepare().parse_known_args(argv)
    args.more = more
    args.func(args)


def front_action(args: Namespace) -> None:
    from . import reader

    if args.format == "json" and args.delimiters:
        raise NotImplementedError("cannot output JSON with delimiters")

    if args.format == "original":
        sections = {reader.LineSection.FRONT_MATTER}
        if args.delimiters:
            sections.add(reader.LineSection.OPENING_DELIMITER)
            sections.add(reader.LineSection.CLOSING_DELIMITER)
        reader.print_filtered(args.input, sections)
    elif args.format == "json":
        fm, _ = reader.fm_and_main(reader.read_stream(args.input))
        json.dump(fm.dict if fm else None, sys.stdout, cls=JSONEncoder)


def main_action(args: Namespace) -> None:
    from . import reader

    reader.print_filtered(args.input, {reader.LineSection.MAIN_CONTENT})


def set_action(args: Namespace) -> None:
    from . import reader
    from .frontmatter import YAML
    from .writer import (
        apply_changes,
        write_stream,
    )

    if args.input.name == "<stdin>":
        # FIXME: Matching on the name seems brittle, but as long as
        # we're using argparse.FileType I don't see a better way.
        raise ValueError(
            "cannot use --in-place when reading from standard input"
        )

    old_fm, main = reader.fm_and_main(reader.read_stream(args.input))

    new_fm = apply_changes(
        old_fm.obj if old_fm and not args.clear else {},
        set_build_changelist(args),
    )

    with contextlib.ExitStack() as stack:
        if args.in_place:
            outfile = Path(args.input.name)
            # Create a temporary file in the same directory as the input. Don't
            # delete it automatically, because we're going to move it over the
            # old file once we're done.
            tmp = tempfile.NamedTemporaryFile(  # noqa: SIM115
                "w+",
                encoding="utf-8",
                delete=False,
                dir=outfile.parent,
                prefix=f".{outfile.name}.",
            )
            tmp_path = Path(tmp.name)
            # Register a callback that will be called _last_ and delete the
            # temp file if for some reason the move didn't work.
            stack.callback(tmp_path.unlink, missing_ok=True)
            # Enter context for the temp file.
            stream: TextIO = stack.enter_context(tmp)  # type: ignore[assignment]
            # Register a callback that will be called _first_ and move the temp
            # file over the original one.
            stack.callback(tmp_path.replace, outfile)
        else:
            stream = sys.stdout

        write_stream(
            stream,
            new_fm,
            YAML,
            main,
            compact_new_lists=args.yaml_new_lists == "flow",
        )


def set_build_changelist(args: Namespace) -> list:  # noqa: C901, PLR0912, PLR0915
    from .writer import Change, ChangeType, ListMode

    class Expecting(Enum):
        NAME_OR_MODE = 1
        NAME = 2
        VALUE = 3
        VALUE_OR_MODE = 4

    list_mode_mapping = {
        "-a": ListMode.APPEND,
        "--append": ListMode.APPEND,
        "-l": ListMode.REPLACE,
        "--list": ListMode.REPLACE,
        "-r": ListMode.REMOVE,
        "--remove": ListMode.REMOVE,
    }

    type = ChangeType.STRING
    next = Expecting.NAME_OR_MODE
    name = ""
    arglist: list[str] | None = None
    listmode: ListMode = ListMode.REPLACE

    def commit_list() -> None:
        nonlocal type, name, arglist, listmode, next
        changes.append(Change(type, name, arglist, list_mode=listmode))
        arglist = None
        type = ChangeType.STRING
        next = Expecting.NAME_OR_MODE

    changes: list[Change] = []
    for arg in args.more:
        if next in {
            Expecting.NAME_OR_MODE,
            Expecting.VALUE_OR_MODE,
        } and arg.startswith("-"):
            if arglist is not None:
                # We're in list mode without a special terminator.
                commit_list()

            if arg in {"-d", "--delete"}:
                type = ChangeType.DELETE
            elif arg in {"-s", "--string"}:
                type = ChangeType.STRING
            elif arg in {"-j", "--json"}:
                type = ChangeType.JSON
            elif arg in {"-t", "--time"}:
                type = ChangeType.TIME
            elif arg in list_mode_mapping:
                type = ChangeType.LIST
                listmode = list_mode_mapping[arg]
                arglist = []
            else:
                raise ValueError(f"unknown change type: {arg}")
            next = Expecting.NAME
            continue
        if next in {Expecting.NAME, Expecting.NAME_OR_MODE}:
            # At this point, it's not a mode, so we handle it as a name.
            name = arg
            if type == ChangeType.DELETE:
                next = Expecting.NAME_OR_MODE
                changes.append(Change(type, name))
            else:
                # If we're in list mode and there's no list terminator
                # configured, we'll take values until something looks like a
                # mode. Else, in list mode, we'll take values until that
                # terminator is encountered. (In non-list mode, well just take
                # a single value.)
                next = (
                    Expecting.VALUE_OR_MODE
                    if arglist is not None and args.end_list_with is None
                    else Expecting.VALUE
                )
            continue
        if next in {Expecting.VALUE, Expecting.VALUE_OR_MODE}:
            # At this point, it's not a mode, so we handle it as a value.
            if arglist is None:  # not in list mode
                changes.append(Change(type, name, arg))
                next = Expecting.NAME_OR_MODE
            elif args.end_list_with is not None and arg == args.end_list_with:
                # We're in list mode and have found the end token.
                commit_list()
            else:  # in list mode, got another item
                arglist.append(arg)

    # If there are still arguments collected from list mode, add them.
    if arglist:
        commit_list()

    return changes
