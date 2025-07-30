# SPDX-FileCopyrightText: © 2025 scy
#
# SPDX-License-Identifier: MIT

from felloff import reader


def test_split(fixtures_path):
    fm, lines = reader.fm_and_main(reader.read_file(fixtures_path / "yaml.md"))
    lines_list = list(lines)
    assert fm.dict["title"] == "An example document"
    assert lines_list[0] == "This document will be used for **testing**."
