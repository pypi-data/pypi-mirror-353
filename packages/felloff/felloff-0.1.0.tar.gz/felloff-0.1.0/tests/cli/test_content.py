# SPDX-FileCopyrightText: © 2025 scy
#
# SPDX-License-Identifier: MIT

from felloff import cli


YAML_CONTENT = ["This document will be used for **testing**."]

NO_FM_CONTENT = [
    "# A document without front matter",
    "",
    "This document has no front matter at all!",
]


def test_simple_get(fixtures_path, capsys):
    cli.run(["main", str(fixtures_path / "yaml.md")])
    assert capsys.readouterr().out == "\n".join(YAML_CONTENT) + "\n"


def test_get_without_front_matter(fixtures_path, capsys):
    cli.run(["main", str(fixtures_path / "no-front-matter.md")])
    assert capsys.readouterr().out == "\n".join(NO_FM_CONTENT) + "\n"
