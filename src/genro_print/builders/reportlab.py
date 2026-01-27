# Copyright 2025 Softwell S.r.l. - Licensed under Apache License 2.0
# See LICENSE file for details

"""
ReportLabBuilder: PDF renderer using ReportLab.

Riceve un ComputedLayout (prodotto da LRCPrintBuilder) e genera
un PDF usando le API ReportLab Canvas.

Responsabilità:
- Tradurre ComputedLayout in chiamate ReportLab
- Gestire trasformazione coordinate (top-left → bottom-left)
- Gestire unità di misura (mm → points)
- Produrre PDF

NON è responsabile di:
- Calcolare dimensioni elastiche (questo è compito di LRCPrintBuilder)
- Definire la struttura Layout/Row/Cell
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
    mm = 1  # fallback per type checking

if TYPE_CHECKING:
    from genro_print.computed import ComputedCell, ComputedLayout


class ReportLabBuilder:
    """Builder che genera PDF da ComputedLayout usando ReportLab.

    Esempio d'uso:
        ```python
        from genro_bag import Bag
        from genro_print.builders import LRCPrintBuilder, ReportLabBuilder

        # 1. Crea documento con LRCPrintBuilder
        doc = Bag(builder=LRCPrintBuilder)
        layout = doc.layout(width=210, height=297)
        layout.row(height=30).cell(content="Hello")

        # 2. Compila in ComputedLayout
        computed = LRCPrintBuilder.compile(doc)

        # 3. Renderizza in PDF
        pdf_bytes = ReportLabBuilder(computed).render()
        ```
    """

    def __init__(self, computed: ComputedLayout) -> None:
        """Inizializza il builder con un ComputedLayout.

        Args:
            computed: Layout con dimensioni già calcolate

        Raises:
            ImportError: Se reportlab non è installato
        """
        if not REPORTLAB_AVAILABLE:
            msg = "ReportLab required: pip install reportlab"
            raise ImportError(msg)

        self.computed = computed
        self.page_width = computed.width * mm
        self.page_height = computed.height * mm
        self._canvas: canvas.Canvas | None = None

    def render(self, output: BytesIO | str | None = None) -> bytes:
        """Renderizza il ComputedLayout in PDF.

        Args:
            output: Destinazione output (BytesIO, path file, o None per BytesIO interno)

        Returns:
            bytes del PDF generato
        """
        # Prepara output
        if output is None:
            output = BytesIO()
        elif isinstance(output, str):
            # Path file - scrivi direttamente
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
        """Renderizza un layout e tutte le sue righe/celle."""
        if self._canvas is None:
            return

        # Bordo layout (se presente)
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

        # Renderizza righe
        for row in layout.rows:
            for cell in row.cells:
                self._render_cell(cell)

    def _render_cell(self, cell: ComputedCell) -> None:
        """Renderizza una singola cella."""
        if self._canvas is None:
            return

        # Bordo cella
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

        # Layout annidato (ricorsione)
        if cell.nested_layout:
            self._render_layout(cell.nested_layout)
            return

        # Contenuto testuale
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
        """Disegna un rettangolo.

        Nota: ReportLab usa coordinate bottom-left, quindi trasformiamo Y.
        """
        if self._canvas is None:
            return

        # Trasforma coordinate (top-left → bottom-left)
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
        """Disegna testo in una cella.

        Se c'è una label, la disegna sopra il contenuto.
        """
        if self._canvas is None:
            return

        # Padding interno
        padding = 2  # mm

        # Coordinate ReportLab
        rl_x = (x + padding) * mm

        if lbl and lbl_height > 0:
            # Disegna label
            lbl_y = self.page_height - (y + lbl_height) * mm
            self._canvas.setFont("Helvetica", 8)
            self._canvas.drawString(rl_x, lbl_y + 2 * mm, lbl)

            # Disegna contenuto sotto la label
            content_y = self.page_height - (y + lbl_height + (height - lbl_height) / 2) * mm
        else:
            # Centra verticalmente
            content_y = self.page_height - (y + height / 2) * mm

        self._canvas.setFont("Helvetica", 10)
        self._canvas.drawString(rl_x, content_y, text)
