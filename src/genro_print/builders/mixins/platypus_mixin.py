# Copyright 2025 Softwell S.r.l. - Licensed under Apache License 2.0
# See LICENSE file for details

"""PlatypusMixin — high-level ReportLab Platypus flowable elements."""

from __future__ import annotations

from genro_builders.builder import element


class PlatypusMixin:
    """Platypus flowable elements: paragraph, spacer, pagebreak, image, table."""

    @element(
        sub_tags="",
        _meta={"compile_type": "platypus", "compile_class": "Paragraph"},
    )
    def paragraph(
        self,
        content: str = "",
        style: str = "Normal",
        bullet_text: str | None = None,
    ) -> None:
        """A paragraph of text."""
        ...

    @element(
        sub_tags="",
        _meta={"compile_type": "platypus", "compile_class": "Spacer"},
    )
    def spacer(
        self,
        width: float = 0.0,
        height: float = 10.0,
    ) -> None:
        """Vertical space between elements."""
        ...

    @element(
        sub_tags="",
        _meta={"compile_type": "platypus", "compile_class": "PageBreak"},
    )
    def pagebreak(self) -> None:
        """Force a page break."""
        ...

    @element(
        sub_tags="",
        _meta={"compile_type": "platypus", "compile_class": "Image"},
    )
    def image(
        self,
        src: str = "",
        width: float | None = None,
        height: float | None = None,
        kind: str = "direct",
        mask: str | None = None,
        lazy: int = 1,
    ) -> None:
        """An image flowable."""
        ...

    @element(
        sub_tags="row",
        _meta={"compile_type": "platypus", "compile_class": "Table"},
    )
    def table(
        self,
        col_widths: list[float] | None = None,
        row_heights: list[float] | None = None,
        repeat_rows: int = 0,
        repeat_cols: int = 0,
        split_by_row: int = 1,
        h_align: str = "CENTER",
    ) -> None:
        """A table flowable."""
        ...

    @element(sub_tags="cell", parent_tags="table")
    def row(self) -> None:
        """A table row. Contains cell elements."""
        ...

    @element(sub_tags="", parent_tags="row")
    def cell(
        self,
        content: str = "",
        colspan: int = 1,
        rowspan: int = 1,
        align: str | None = None,
        valign: str | None = None,
        background: str | None = None,
    ) -> None:
        """A table cell."""
        ...
