# Copyright 2025 Softwell S.r.l. - Licensed under Apache License 2.0
# See LICENSE file for details

"""LRCMixin — Layout/Row/Cell elements for elastic grid layout."""

from __future__ import annotations

from genro_builders.builder import element


class LRCMixin:
    """Layout/Row/Cell elements with elastic dimension support."""

    @element(sub_tags="row")
    def layout(
        self,
        width: float = 0,
        height: float = 0,
        top: float = 0,
        bottom: float = 0,
        left: float = 0,
        right: float = 0,
        um: str = "mm",
        border_width: float = 0,
        border_color: str = "black",
    ) -> None:
        """Layout container — can only contain Row.

        Args:
            width: Total width (0 = inherit from parent)
            height: Total height (0 = inherit from parent)
            top: Top margin
            bottom: Bottom margin
            left: Left margin
            right: Right margin
            um: Unit of measure (default: mm)
            border_width: Border thickness
            border_color: Border color
        """
        ...

    @element(sub_tags="cell")
    def row(
        self,
        height: float = 0,
        border: bool | None = None,
    ) -> None:
        """Row — can only contain Cell.

        Args:
            height: Row height (0 = elastic, expands to fill)
            border: Whether it has border (None = inherit from layout)
        """
        ...

    @element(sub_tags="layout,image,paragraph,spacer")
    def cell(
        self,
        width: float = 0,
        border: bool | None = None,
        content: str | None = None,
        lbl: str | None = None,
        lbl_height: float = 0,
        lbl_class: str | None = None,
        content_class: str | None = None,
    ) -> None:
        """Cell — can contain nested Layout, content elements, or simple text.

        Args:
            width: Cell width (0 = elastic, expands to fill)
            border: Whether it has border (None = inherit from row)
            content: Text content (simple text, for backward compatibility)
            lbl: Label above content
            lbl_height: Label height
            lbl_class: CSS class for label
            content_class: CSS class for content
        """
        ...

    @element()
    def image(
        self,
        src: str = "",
        width: float = 0,
        height: float = 0,
        align: str = "left",
        valign: str = "top",
    ) -> None:
        """Image element inside a cell.

        Args:
            src: Path to image file
            width: Image width in mm (0 = auto from aspect ratio)
            height: Image height in mm (0 = auto from aspect ratio)
            align: Horizontal alignment (left, center, right)
            valign: Vertical alignment (top, middle, bottom)
        """
        ...

    @element()
    def paragraph(
        self,
        content: str = "",
        style: str = "Normal",
        font_name: str = "Helvetica",
        font_size: float = 10,
        color: str = "black",
        align: str = "left",
    ) -> None:
        """Paragraph element inside a cell."""
        ...

    @element()
    def spacer(
        self,
        height: float = 5,
    ) -> None:
        """Vertical spacer inside a cell."""
        ...
