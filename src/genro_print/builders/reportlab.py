# Copyright 2025 Softwell S.r.l. - Licensed under Apache License 2.0
# See LICENSE file for details

"""
ReportLabBuilder: PDF renderer using ReportLab.

Receives a ComputedLayout (produced by LRCPrintBuilder) and generates
a PDF using the ReportLab Canvas API.

Responsibilities:
- Translate ComputedLayout into ReportLab calls
- Handle coordinate transformation (top-left → bottom-left)
- Handle unit conversion (mm → points)
- Produce PDF

NOT responsible for:
- Calculating elastic dimensions (that's LRCPrintBuilder's job)
- Defining Layout/Row/Cell structure
"""

from __future__ import annotations

from io import BytesIO
from typing import TYPE_CHECKING

try:
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas

    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    mm = 1  # fallback for type checking

if TYPE_CHECKING:
    from genro_print.computed import ComputedCell, ComputedLayout


class ReportLabBuilder:
    """Builder that generates PDF from ComputedLayout using ReportLab.

    Example usage:
        ```python
        from genro_bag import Bag
        from genro_print.builders import LRCPrintBuilder, ReportLabBuilder

        # 1. Create document with LRCPrintBuilder
        doc = Bag(builder=LRCPrintBuilder)
        layout = doc.layout(width=210, height=297)
        layout.row(height=30).cell(content="Hello")

        # 2. Compile to ComputedLayout
        computed = LRCPrintBuilder.compile(doc)

        # 3. Render to PDF
        pdf_bytes = ReportLabBuilder(computed).render()
        ```
    """

    def __init__(self, computed: ComputedLayout) -> None:
        """Initialize the builder with a ComputedLayout.

        Args:
            computed: Layout with pre-calculated dimensions

        Raises:
            ImportError: If reportlab is not installed
        """
        if not REPORTLAB_AVAILABLE:
            msg = "ReportLab required: pip install reportlab"
            raise ImportError(msg)

        self.computed = computed
        self.page_width = computed.width * mm
        self.page_height = computed.height * mm
        self._canvas: canvas.Canvas | None = None

    def render(self, output: BytesIO | str | None = None) -> bytes:
        """Render the ComputedLayout to PDF.

        Args:
            output: Output destination (BytesIO, file path, or None for internal BytesIO)

        Returns:
            PDF bytes
        """
        # Prepare output
        if output is None:
            output = BytesIO()
        elif isinstance(output, str):
            # File path - write directly
            self._canvas = canvas.Canvas(
                output,
                pagesize=(self.page_width, self.page_height),
            )
            self._render_layout(self.computed)
            self._canvas.save()
            with open(output, "rb") as f:
                return f.read()

        # BytesIO
        self._canvas = canvas.Canvas(
            output,
            pagesize=(self.page_width, self.page_height),
        )
        self._render_layout(self.computed)
        self._canvas.save()

        output.seek(0)
        return output.read()

    def _render_layout(self, layout: ComputedLayout) -> None:
        """Render a layout and all its rows/cells."""
        if self._canvas is None:
            return

        # Layout border (if present)
        if layout.border_width > 0:
            self._draw_rect(
                x=layout.x,
                y=layout.y,
                width=layout.width,
                height=layout.height,
                stroke=True,
                stroke_width=layout.border_width,
                stroke_color=layout.border_color,
            )

        # Render rows
        for row in layout.rows:
            for cell in row.cells:
                self._render_cell(cell)

    def _render_cell(self, cell: ComputedCell) -> None:
        """Render a single cell."""
        if self._canvas is None:
            return

        # Cell border
        if cell.border and cell.border_width > 0:
            self._draw_rect(
                x=cell.x,
                y=cell.y,
                width=cell.computed_width,
                height=cell.computed_height,
                stroke=True,
                stroke_width=cell.border_width,
                stroke_color=cell.border_color,
            )

        # Nested layout (recursion)
        if cell.nested_layout:
            self._render_layout(cell.nested_layout)
            return

        # Text content
        if cell.content:
            self._draw_text(
                text=cell.content,
                x=cell.x,
                y=cell.y,
                width=cell.computed_width,
                height=cell.computed_height,
                lbl=cell.lbl,
                lbl_height=cell.lbl_height,
            )

    def _draw_rect(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        stroke: bool = True,
        fill: bool = False,
        stroke_width: float = 0.3,
        stroke_color: str = "black",
    ) -> None:
        """Draw a rectangle.

        Note: ReportLab uses bottom-left coordinates, so we transform Y.
        """
        if self._canvas is None:
            return

        # Transform coordinates (top-left → bottom-left)
        rl_x = x * mm
        rl_y = self.page_height - (y + height) * mm
        rl_width = width * mm
        rl_height = height * mm

        self._canvas.setStrokeColor(stroke_color)
        self._canvas.setLineWidth(stroke_width * mm)
        self._canvas.rect(
            rl_x,
            rl_y,
            rl_width,
            rl_height,
            stroke=1 if stroke else 0,
            fill=1 if fill else 0,
        )

    def _draw_text(
        self,
        text: str,
        x: float,
        y: float,
        width: float,  # noqa: ARG002
        height: float,
        lbl: str | None = None,
        lbl_height: float = 0,
    ) -> None:
        """Draw text in a cell.

        If there's a label, draw it above the content.
        """
        if self._canvas is None:
            return

        # Internal padding
        padding = 2  # mm

        # ReportLab coordinates
        rl_x = (x + padding) * mm

        if lbl and lbl_height > 0:
            # Draw label
            lbl_y = self.page_height - (y + lbl_height) * mm
            self._canvas.setFont("Helvetica", 8)
            self._canvas.drawString(rl_x, lbl_y + 2 * mm, lbl)

            # Draw content below the label
            content_y = self.page_height - (y + lbl_height + (height - lbl_height) / 2) * mm
        else:
            # Center vertically
            content_y = self.page_height - (y + height / 2) * mm

        self._canvas.setFont("Helvetica", 10)
        self._canvas.drawString(rl_x, content_y, text)
