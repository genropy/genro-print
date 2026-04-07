# Copyright 2025 Softwell S.r.l. - Licensed under Apache License 2.0
# See LICENSE file for details

"""DocumentMixin — document root element shared by all print builders."""

from __future__ import annotations

from genro_builders.builder import element


class DocumentMixin:
    """Document root element with page size and margins."""

    @element(sub_tags="*")
    def document(
        self,
        width: float = 210.0,
        height: float = 297.0,
        left_margin: float = 10.0,
        right_margin: float = 10.0,
        top_margin: float = 10.0,
        bottom_margin: float = 10.0,
        title: str | None = None,
        author: str | None = None,
    ) -> None:
        """Document root element with page size and margins."""
        ...
