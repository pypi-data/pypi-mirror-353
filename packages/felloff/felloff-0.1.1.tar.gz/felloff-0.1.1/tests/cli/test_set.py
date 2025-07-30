# SPDX-FileCopyrightText: © 2025 scy
#
# SPDX-License-Identifier: MIT

import shlex

import pytest

from felloff import cli
from felloff.writer import Change, ChangeType, ListMode


def test_replace_value(fixtures_path, capsys):
    cli.run(["set", str(fixtures_path / "yaml.md"), "title", "my new title"])
    output = capsys.readouterr().out
    assert "\ntitle: my new title\n" in output
    assert "An example document" not in output


def test_create_fm(fixtures_path, capsys):
    cli.run(
        [
            "set",
            str(fixtures_path / "no-front-matter.md"),
            "title",
            "foo",
            "--time",
            "created",
            "2025-06-06",
            "--json",
            "id",
            "1",
        ]
    )
    assert capsys.readouterr().out.startswith(
        "---\ntitle: foo\ncreated: 2025-06-06\nid: 1\n---\n"
    )


def test_delete_fields(fixtures_path, capsys):
    cli.run(
        [
            "set",
            str(fixtures_path / "yaml.md"),
            "--delete",
            "tags",
            "title",
            "nonexistent",
        ]
    )
    output = capsys.readouterr().out
    assert "An example document" not in output
    assert "tags:" not in output


def test_delete_all_fields(fixtures_path, capsys):
    cli.run(
        [
            "set",
            str(fixtures_path / "yaml.md"),
            "--delete",
            "tags",
            "title",
            "created",
        ]
    )
    assert "---" not in capsys.readouterr().out


@pytest.mark.parametrize(
    ("options", "expected"),
    [
        ("", []),
        (
            "author scy",
            [Change(type=ChangeType.STRING, name="author", value="scy")],
        ),
        (
            "-d tags",
            [Change(type=ChangeType.DELETE, name="tags", value=None)],
        ),
        (
            "-l tags foo bar",
            [
                Change(
                    type=ChangeType.LIST,
                    name="tags",
                    value=["foo", "bar"],
                    list_mode=ListMode.REPLACE,
                )
            ],
        ),
        (
            "-l tags foo bar -t modified now",
            [
                Change(
                    type=ChangeType.LIST,
                    name="tags",
                    value=["foo", "bar"],
                    list_mode=ListMode.REPLACE,
                ),
                Change(
                    type=ChangeType.TIME,
                    name="modified",
                    value="now",
                ),
            ],
        ),
        (
            "--end-list-with . -l tags foo bar . -t modified now",
            [
                Change(
                    type=ChangeType.LIST,
                    name="tags",
                    value=["foo", "bar"],
                    list_mode=ListMode.REPLACE,
                ),
                Change(
                    type=ChangeType.TIME,
                    name="modified",
                    value="now",
                ),
            ],
        ),
        (
            "--end-list-with . -l tags foo bar . baz quux -t modified now",
            [
                Change(
                    type=ChangeType.LIST,
                    name="tags",
                    value=["foo", "bar"],
                    list_mode=ListMode.REPLACE,
                ),
                Change(
                    type=ChangeType.STRING,
                    name="baz",
                    value="quux",
                ),
                Change(
                    type=ChangeType.TIME,
                    name="modified",
                    value="now",
                ),
            ],
        ),
    ],
)
def test_options_to_changelist(options: list[str], expected: list[Change]):
    args, more = cli.prepare().parse_known_args(
        ["set", "/dev/null", *shlex.split(options)]
    )
    args.more = more
    changelist = cli.set_build_changelist(args)
    assert changelist == expected
