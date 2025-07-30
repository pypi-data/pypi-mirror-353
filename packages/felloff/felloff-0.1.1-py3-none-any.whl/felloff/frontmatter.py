# SPDX-FileCopyrightText: © 2025 scy
#
# SPDX-License-Identifier: MIT

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, TextIO

from ruamel.yaml import YAML as RuamelYAML  # noqa: N811
from ruamel.yaml.comments import (
    CommentedMap as YAMLCommentedMap,
)
from ruamel.yaml.comments import (
    CommentedSeq as YAMLCommentedSeq,
)


FrontMatter = dict[str, Any] | YAMLCommentedMap


@dataclass
class Format(ABC):
    name: str
    open_delim: str
    close_delim: str

    @classmethod
    def write_fm(
        cls,
        stream: TextIO,
        fm: FrontMatter,
        *,
        delimiters: bool,
        **kwargs: Any,  # noqa: ANN401
    ) -> None:
        if not len(fm):
            return
        if delimiters:
            stream.write(cls.open_delim + "\n")
        cls.dump(fm, stream, **kwargs)
        if delimiters:
            stream.write(cls.close_delim + "\n")

    @classmethod
    def by_open_delim(cls, delim: str) -> "type[Format] | None":
        return OPEN_DELIM_TO_FORMAT.get(delim)

    @staticmethod
    @abstractmethod
    def dump(fm: FrontMatter, stream: TextIO) -> None: ...

    @staticmethod
    @abstractmethod
    def load(lines: list[str]) -> FrontMatter: ...


@dataclass
class YAML(Format):
    name: str = "YAML"
    open_delim: str = "---"
    close_delim: str = "---"

    @staticmethod
    def dump(
        fm: FrontMatter,
        stream: TextIO,
        *,
        compact_new_lists: bool | None = None,
    ) -> None:
        def list_representer(dumper, data):  # noqa: ANN001, ANN202
            return dumper.represent_sequence(
                "tag:yaml.org,2002:seq",
                data,
                flow_style=None
                if isinstance(data, YAMLCommentedSeq)
                else compact_new_lists,
            )

        yaml = RuamelYAML()
        if compact_new_lists is not None:
            yaml.representer.add_representer(list, list_representer)
        yaml.dump(fm, stream)

    @staticmethod
    def load(lines: list[str]) -> YAMLCommentedMap:
        return RuamelYAML().load("\n".join(lines))


OPEN_DELIM_TO_FORMAT = {cls.open_delim: cls for cls in [YAML]}
