# Copyright 2025 Softwell S.r.l. - Licensed under Apache License 2.0
# See LICENSE file for details

"""LRC component mixin — reusable composite elements for Layout/Row/Cell builder."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from genro_builders.builder import component

if TYPE_CHECKING:
    from genro_builders.builder_bag import Component


class LRCComponentsMixin:
    """Reusable components for LRC-based PDF reports."""

    @component(sub_tags="*", slots=["content"])
    def page_template(
        self,
        comp: Component,
        title: str = "",
        header_height: float = 20.0,
        footer_height: float = 15.0,
        footer_text: str = "",
        width: float = 210.0,
        height: float = 297.0,
        margin: float = 10.0,
        border_width: float = 0.0,
        **kwargs: Any,  # noqa: ARG002
    ) -> dict[str, Any]:
        """Page template with header, content area, and footer.

        The content area is elastic (fills remaining space).
        Returns a 'content' slot where the user adds their elements.

        Args:
            comp: Component Bag (provided by decorator)
            title: Header title text
            header_height: Height of header row in mm
            footer_height: Height of footer row in mm
            footer_text: Footer text (empty = no footer text)
            width: Page width in mm
            height: Page height in mm
            margin: Page margin (all sides) in mm
            border_width: Border width for layout
        """
        layout = comp.layout(
            width=width, height=height,
            top=margin, bottom=margin, left=margin, right=margin,
            border_width=border_width,
        )

        # Header row (fixed height)
        if header_height > 0:
            header_row = layout.row(height=header_height, border=bool(border_width))
            header_row.cell(content=title)

        # Content area (elastic — fills remaining space)
        content_row = layout.row()
        content_cell = content_row.cell()

        # Footer row (fixed height)
        if footer_height > 0:
            footer_row = layout.row(height=footer_height, border=bool(border_width))
            footer_row.cell(content=footer_text)

        return {"content": content_cell}

    @component(sub_tags="")
    def two_column_row(
        self,
        comp: Component,
        left_content: str = "",
        right_content: str = "",
        left_width: float = 0.0,
        right_width: float = 0.0,
        height: float = 0.0,
        border: bool = False,
        **kwargs: Any,  # noqa: ARG002
    ) -> Component:
        """Two-column row: left and right cells side by side.

        If widths are 0, they split equally (elastic).

        Args:
            comp: Component Bag (provided by decorator)
            left_content: Text for left cell
            right_content: Text for right cell
            left_width: Left cell width (0 = elastic)
            right_width: Right cell width (0 = elastic)
            height: Row height (0 = elastic)
            border: Whether cells have borders
        """
        row = comp.row(height=height, border=border)
        row.cell(width=left_width, content=left_content)
        row.cell(width=right_width, content=right_content)
        return comp

    @component(sub_tags="")
    def label_value_row(
        self,
        comp: Component,
        label: str = "",
        value: str = "",
        label_width: float = 40.0,
        height: float = 8.0,
        border: bool = False,
        **kwargs: Any,  # noqa: ARG002
    ) -> Component:
        """Row with a fixed-width label and elastic value cell.

        Args:
            comp: Component Bag (provided by decorator)
            label: Label text
            value: Value text
            label_width: Width of label cell in mm
            height: Row height in mm
            border: Whether cells have borders
        """
        row = comp.row(height=height, border=border)
        row.cell(width=label_width, content=label, lbl=None)
        row.cell(content=value)
        return comp
