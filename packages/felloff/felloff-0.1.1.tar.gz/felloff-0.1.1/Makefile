# SPDX-FileCopyrightText: © 2025 scy
#
# SPDX-License-Identifier: MIT

.PHONY: all fmt noqa qa test reuse


all: fmt qa test reuse


fmt:
	ruff format
	ruff check --fix


noqa:
	ruff check --add-noqa


qa:
	mypy


reuse:
	reuse lint


test:
	pytest
