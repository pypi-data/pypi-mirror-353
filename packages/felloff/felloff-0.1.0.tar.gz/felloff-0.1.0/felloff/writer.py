# SPDX-FileCopyrightText: © 2025 scy
#
# SPDX-License-Identifier: MIT

import json
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, date, datetime
from enum import Enum
from typing import Any, TextIO

from .frontmatter import Format, FrontMatter


class ChangeType(Enum):
    DELETE = 0
    STRING = 1
    JSON = 2
    TIME = 3
    LIST = 4


class ListMode(Enum):
    REPLACE = 1
    APPEND = 2
    REMOVE = 3


@dataclass
class Change:
    type: ChangeType
    name: str
    value: Any = None
    list_mode: ListMode | None = None


def parse_time(value: str) -> datetime | date:
    if value == "now":
        return datetime.now(tz=UTC).astimezone()
    if value == "utcnow":
        return datetime.now(tz=UTC)
    if value == "today":
        return datetime.now(tz=UTC).astimezone().date()
    if value == "utctoday":
        return datetime.now(tz=UTC).date()
    try:
        return date.fromisoformat(value)
    except ValueError:
        try:
            return datetime.fromisoformat(value)
        except ValueError as e:
            raise e from None


def apply_changes(  # noqa: C901, PLR0912
    fm: FrontMatter,
    changes: Iterable[Change],
) -> FrontMatter:
    for change in changes:  # noqa: PLR1702
        if change.type == ChangeType.DELETE and change.name in fm:
            del fm[change.name]
        elif change.type == ChangeType.STRING:
            fm[change.name] = change.value
        elif change.type == ChangeType.JSON:
            fm[change.name] = json.loads(change.value)
        elif change.type == ChangeType.TIME:
            fm[change.name] = parse_time(change.value)
        elif change.type == ChangeType.LIST:
            existing = fm.get(change.name)
            if change.list_mode == ListMode.APPEND and existing:
                if isinstance(existing, list):
                    existing.extend(change.value)
                else:
                    fm[change.name] = [existing, *change.value]
            elif change.list_mode == ListMode.REMOVE:
                if isinstance(existing, list):
                    for i in range(len(existing) - 1, -1, -1):
                        if existing[i] in change.value:
                            del existing[i]
            else:
                fm[change.name] = change.value
    return fm


def write_stream(
    stream: TextIO,
    fm: FrontMatter,
    format: type[Format],
    main: Iterable[str],
    **kwargs: Any,  # noqa: ANN401
) -> None:
    format.write_fm(stream, fm, delimiters=True, **kwargs)
    stream.writelines(line + "\n" for line in main)
