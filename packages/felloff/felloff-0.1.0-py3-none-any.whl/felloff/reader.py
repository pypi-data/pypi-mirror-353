# SPDX-FileCopyrightText: © 2025 scy
#
# SPDX-License-Identifier: MIT

import itertools
from collections.abc import Collection, Iterable
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, TextIO, cast

from .frontmatter import Format, FrontMatter


class LineSection(Enum):
    OPENING_DELIMITER = 1
    FRONT_MATTER = 2
    CLOSING_DELIMITER = 3
    MAIN_CONTENT = 4


@dataclass
class LoadedFrontMatter:
    start_line: int
    end_line: int
    format: Format
    lines: list[str]
    obj: FrontMatter
    dict: dict


@dataclass
class InputLine:
    number: int
    section: LineSection
    text: str
    format: type[Format] | None = None


def read_stream(stream: TextIO) -> Iterable[InputLine]:
    section: LineSection | None = None
    format: type[Format] | None = None
    for number, line_text_raw in enumerate(stream, 1):
        line_text = line_text_raw.rstrip("\r\n")

        if section is None:
            if format := Format.by_open_delim(line_text):
                section = LineSection.OPENING_DELIMITER
            else:  # file doesn't seem to have front matter
                section = LineSection.MAIN_CONTENT
        elif section == LineSection.OPENING_DELIMITER:
            # Previous line was opening delimiter, we're now in front matter.
            section = LineSection.FRONT_MATTER
        elif section == LineSection.CLOSING_DELIMITER:
            # Previous line was closing delimiter, we're now in the content.
            section = LineSection.MAIN_CONTENT

        # If we're in the front matter (even if we just entered it), check if
        # we see a closing delimiter.
        if (
            section == LineSection.FRONT_MATTER
            and line_text == cast("type[Format]", format).close_delim
        ):
            section = LineSection.CLOSING_DELIMITER

        yield InputLine(
            number=number, section=section, text=line_text, format=format
        )


def read_file(path: Path) -> Iterable[InputLine]:
    with path.open("r") as file:
        yield from read_stream(file)


def filter_sections(
    input: Iterable[InputLine], sections: Collection[LineSection]
) -> Iterable[InputLine]:
    yield from itertools.takewhile(
        lambda line: line.section in sections,
        itertools.dropwhile(lambda line: line.section not in sections, input),
    )


def print_filtered(input: TextIO, sections: Collection[LineSection]) -> None:
    for line in filter_sections(read_stream(input), sections):
        print(line.text)  # noqa: T201


def to_dict(obj: Any) -> dict | Any:  # noqa: ANN401
    if hasattr(obj, "items"):
        return {k: to_dict(v) for k, v in obj.items()}
    if hasattr(obj, "__iter__") and not isinstance(obj, str | bytes):
        return [to_dict(item) for item in obj]
    return obj


def fm_and_main(
    input: Iterable[InputLine],
) -> tuple[LoadedFrontMatter | None, Iterable[str]]:
    fm: LoadedFrontMatter | None = None
    line: InputLine | None = None
    fm_lines: list[str] = []
    start_line = end_line = 0
    for line in input:
        if line.section == LineSection.OPENING_DELIMITER:
            start_line = line.number
        elif line.section == LineSection.CLOSING_DELIMITER:
            end_line = line.number
        elif line.section == LineSection.FRONT_MATTER:
            fm_lines.append(line.text)
        elif line.section == LineSection.MAIN_CONTENT:
            if line.format:
                fm_obj = line.format.load(fm_lines)
                fm_dict = to_dict(fm_obj)

            fm = (
                LoadedFrontMatter(
                    start_line=start_line,
                    end_line=end_line,
                    format=cast("Format", line.format),
                    lines=fm_lines,
                    obj=fm_obj,
                    dict=fm_dict,
                )
                if fm_lines
                else None
            )
            break

    return fm, itertools.chain(
        [line.text] if line else [], (line.text for line in input)
    )
