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
from reportlab.pdfgen import canvas

if TYPE_CHECKING:
    from genro_print.computed import ComputedCell, ComputedLayout, ComputedRow


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

        # Draw content if present
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
        return toColor(color)
