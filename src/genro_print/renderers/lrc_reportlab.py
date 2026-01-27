# Copyright 2025 Softwell S.r.l. - Licensed under Apache License 2.0
# See LICENSE file for details
"""LRCReportLabRenderer: Renders ComputedLayout to PDF using ReportLab.

This renderer takes a ComputedLayout (produced by LRCPrintBuilder.compile())
and generates a PDF using ReportLab's canvas.

Coordinate system:
- ComputedLayout uses mm with origin at top-left
- ReportLab uses points (1mm = 2.834645pt) with origin at bottom-left
- This renderer handles the conversion automatically
"""

from __future__ import annotations

from io import BytesIO
from typing import TYPE_CHECKING

from reportlab.lib.colors import HexColor, toColor
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from genro_print.computed import CellElementType

if TYPE_CHECKING:
    from genro_print.computed import (
        ComputedCell,
        ComputedCellElement,
        ComputedLayout,
        ComputedRow,
    )


class LRCReportLabRenderer:
    """Renders ComputedLayout to PDF using ReportLab canvas."""

    def __init__(self, layout: ComputedLayout) -> None:
        self._layout = layout
        self._page_height = layout.height * mm  # in points

    def render(self) -> bytes:
        """Render the layout to PDF bytes."""
        buffer = BytesIO()

        c = canvas.Canvas(
            buffer,
            pagesize=(self._layout.width * mm, self._layout.height * mm),
        )

        self._render_layout(c, self._layout)

        c.save()
        return buffer.getvalue()

    def _render_layout(self, c: canvas.Canvas, layout: ComputedLayout) -> None:
        """Render a layout and all its rows/cells."""
        # Draw layout border if present
        if layout.border_width > 0:
            self._draw_rect(
                c,
                x=layout.x,
                y=layout.y,
                width=layout.width,
                height=layout.height,
                stroke_width=layout.border_width,
                stroke_color=layout.border_color,
            )

        # Render each row
        for row in layout.rows:
            self._render_row(c, row)

    def _render_row(self, c: canvas.Canvas, row: ComputedRow) -> None:
        """Render a row and all its cells."""
        for cell in row.cells:
            self._render_cell(c, cell)

    def _render_cell(self, c: canvas.Canvas, cell: ComputedCell) -> None:
        """Render a single cell."""
        # Draw cell border if present
        if cell.border and cell.border_width > 0:
            self._draw_rect(
                c,
                x=cell.x,
                y=cell.y,
                width=cell.computed_width,
                height=cell.computed_height,
                stroke_width=cell.border_width,
                stroke_color=cell.border_color,
            )

        # Calculate content area (accounting for label if present)
        content_y = cell.y
        content_height = cell.computed_height

        # Draw label if present
        if cell.lbl and cell.lbl_height > 0:
            self._draw_text(
                c,
                text=cell.lbl,
                x=cell.x + 1,  # small padding
                y=cell.y + 1,
                width=cell.computed_width - 2,
                height=cell.lbl_height,
                font_size=8,
                color="#666666",
            )
            content_y += cell.lbl_height
            content_height -= cell.lbl_height

        # Draw content if present (simple text, backward compatible)
        if cell.content:
            self._draw_text(
                c,
                text=cell.content,
                x=cell.x + 1,
                y=content_y + 1,
                width=cell.computed_width - 2,
                height=content_height - 2,
                font_size=10,
            )

        # Render cell elements (image, paragraph, spacer)
        if cell.elements:
            self._render_cell_elements(
                c,
                elements=cell.elements,
                x=cell.x + 1,
                y=content_y + 1,
                width=cell.computed_width - 2,
                height=content_height - 2,
            )

        # Render nested layout if present
        if cell.nested_layout:
            self._render_layout(c, cell.nested_layout)

    def _draw_rect(
        self,
        c: canvas.Canvas,
        x: float,
        y: float,
        width: float,
        height: float,
        stroke_width: float = 0.5,
        stroke_color: str = "black",
        fill_color: str | None = None,
    ) -> None:
        """Draw a rectangle. Coordinates in mm, origin top-left."""
        # Convert to points and flip Y
        x_pt = x * mm
        y_pt = self._page_height - (y * mm) - (height * mm)  # flip Y
        width_pt = width * mm
        height_pt = height * mm

        c.setStrokeColor(self._parse_color(stroke_color))
        c.setLineWidth(stroke_width * mm)

        if fill_color:
            c.setFillColor(self._parse_color(fill_color))
            c.rect(x_pt, y_pt, width_pt, height_pt, stroke=1, fill=1)
        else:
            c.rect(x_pt, y_pt, width_pt, height_pt, stroke=1, fill=0)

    def _draw_text(
        self,
        c: canvas.Canvas,
        text: str,
        x: float,
        y: float,
        width: float,  # noqa: ARG002
        height: float,  # noqa: ARG002
        font_size: float = 10,
        font_name: str = "Helvetica",
        color: str = "black",
    ) -> None:
        """Draw text. Coordinates in mm, origin top-left.

        Args:
            c: ReportLab canvas
            text: Text to draw
            x: X coordinate in mm
            y: Y coordinate in mm
            width: Available width in mm (for future text wrapping)
            height: Available height in mm (for future text wrapping)
            font_size: Font size in points
            font_name: Font name
            color: Text color
        """
        # Convert to points and flip Y
        x_pt = x * mm
        # Text baseline is at bottom, so we position from top and add font size
        y_pt = self._page_height - (y * mm) - font_size

        c.setFont(font_name, font_size)
        c.setFillColor(self._parse_color(color))
        c.drawString(x_pt, y_pt, text)

    def _parse_color(self, color: str) -> HexColor:
        """Parse color string to ReportLab color."""
        if color.startswith("#"):
            return HexColor(color)
        result: HexColor = toColor(color)
        return result

    def _render_cell_elements(
        self,
        c: canvas.Canvas,
        elements: list[ComputedCellElement],
        x: float,
        y: float,
        width: float,
        height: float,  # noqa: ARG002
    ) -> None:
        """Render cell child elements (image, paragraph, spacer).

        Args:
            c: ReportLab canvas
            elements: List of cell elements to render
            x: Starting X coordinate in mm
            y: Starting Y coordinate in mm
            width: Available width in mm
            height: Available height in mm
        """
        current_y = y

        for elem in elements:
            if elem.element_type == CellElementType.IMAGE:
                current_y = self._render_image_element(
                    c, elem, x, current_y, width
                )
            elif elem.element_type == CellElementType.PARAGRAPH:
                current_y = self._render_paragraph_element(
                    c, elem, x, current_y, width
                )
            elif elem.element_type == CellElementType.SPACER:
                current_y += elem.attrs.get("height", 5)

    def _render_image_element(
        self,
        c: canvas.Canvas,
        elem: ComputedCellElement,
        x: float,
        y: float,
        available_width: float,
    ) -> float:
        """Render an image element. Returns new Y position."""
        attrs = elem.attrs
        src = attrs.get("src", "")
        if not src:
            return y

        img_width = attrs.get("width", 0)
        img_height = attrs.get("height", 0)
        align = attrs.get("align", "left")

        # Load image to get dimensions if needed
        try:
            img = ImageReader(src)
            native_width, native_height = img.getSize()

            # Calculate dimensions
            if img_width == 0 and img_height == 0:
                # Use native size (convert pixels to mm, assuming 72 dpi)
                img_width = native_width * 25.4 / 72
                img_height = native_height * 25.4 / 72
            elif img_width == 0:
                # Calculate width from height preserving aspect ratio
                img_width = img_height * native_width / native_height
            elif img_height == 0:
                # Calculate height from width preserving aspect ratio
                img_height = img_width * native_height / native_width

            # Horizontal alignment
            if align == "center":
                img_x = x + (available_width - img_width) / 2
            elif align == "right":
                img_x = x + available_width - img_width
            else:
                img_x = x

            # Draw image (convert mm to points, flip Y)
            x_pt = img_x * mm
            y_pt = self._page_height - (y * mm) - (img_height * mm)

            c.drawImage(
                img,
                x_pt,
                y_pt,
                width=img_width * mm,
                height=img_height * mm,
                preserveAspectRatio=True,
            )

            new_y: float = y + img_height
            return new_y
        except Exception:
            # If image fails to load, just skip it
            return y

    def _render_paragraph_element(
        self,
        c: canvas.Canvas,
        elem: ComputedCellElement,
        x: float,
        y: float,
        width: float,  # noqa: ARG002
    ) -> float:
        """Render a paragraph element. Returns new Y position."""
        attrs = elem.attrs
        content = attrs.get("content", "")
        if not content:
            return y

        font_name = attrs.get("font_name", "Helvetica")
        font_size = attrs.get("font_size", 10)
        color = attrs.get("color", "black")

        # Simple single-line text for now
        x_pt = x * mm
        y_pt = self._page_height - (y * mm) - font_size

        c.setFont(font_name, font_size)
        c.setFillColor(self._parse_color(color))
        c.drawString(x_pt, y_pt, content)

        # Approximate line height
        line_height: float = font_size * 1.2 / mm  # convert back to mm
        return y + line_height
