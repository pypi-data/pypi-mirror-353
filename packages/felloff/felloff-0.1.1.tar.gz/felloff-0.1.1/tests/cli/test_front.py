# SPDX-FileCopyrightText: © 2025 scy
#
# SPDX-License-Identifier: MIT

import json

from felloff import cli


YAML_FRONT = """\
---
title: An example document
created: 2025-06-06  # Start of the felloff project.
tags: [test, example]
---""".split("\n")  # noqa: SIM905


def test_simple_get(fixtures_path, capsys):
    cli.run(["front", str(fixtures_path / "yaml.md")])
    assert capsys.readouterr().out == "\n".join(YAML_FRONT[1:-1]) + "\n"


def test_get_with_delim(fixtures_path, capsys):
    cli.run(["front", "--delimiters", str(fixtures_path / "yaml.md")])
    assert capsys.readouterr().out == "\n".join(YAML_FRONT) + "\n"


def test_get_without_front_matter(fixtures_path, capsys):
    cli.run(["front", str(fixtures_path / "no-front-matter.md")])
    assert not capsys.readouterr().out


def test_get_json(fixtures_path, capsys):
    cli.run(["front", "--format", "json", str(fixtures_path / "yaml.md")])
    assert json.loads(capsys.readouterr().out)["created"] == "2025-06-06"
