# Copyright 2025 Softwell S.r.l. - Licensed under Apache License 2.0
# See LICENSE file for details

"""Print application classes based on BuilderManager.

Three app classes, one for each builder type:
- PrintApp: Platypus + Canvas (classic reports)
- LRCPrintApp: Layout/Row/Cell (elastic grid)
- StyledPrintApp: Declarative styled shapes

All share the same lifecycle: store() -> recipe() -> render() -> save().
"""

from __future__ import annotations

from pathlib import Path

from genro_builders import BuilderBag, BuilderManager

from genro_print.builders.print_builder import PrintBuilder
from genro_print.builders.print_lrc_builder import PrintLRCBuilder
from genro_print.builders.print_styled_builder import PrintStyledBuilder


class _PrintAppBase(BuilderManager):
    """Base class for all print applications.

    Subclasses set _builder_class to select the builder type.
    Users override recipe() to define their document, and
    optionally store() to populate report data.

    Example:
        class MyReport(PrintApp):
            def store(self, data):
                data['title'] = 'Monthly Report'

            def recipe(self, root):
                root.document(width=210, height=297)
                root.paragraph(content='^title', style='Title')

        report = MyReport()
        report.save('report.pdf')
    """

    _builder_class: type

    def __init__(self) -> None:
        self.page = self.set_builder("page", self._builder_class)
        self.setup()
        self.build()

    def main(self, source: BuilderBag) -> None:
        """Delegates to recipe() for the user-facing API."""
        self.recipe(source)

    def recipe(self, root: BuilderBag) -> None:
        """Override to build your document.

        Args:
            root: BuilderBag with the builder's available elements.
        """

    def render(self) -> bytes:
        """Compile the document to PDF bytes."""
        result: bytes = self.page.compile(name="reportlab")
        return result

    def save(self, filepath: str | Path) -> None:
        """Render and save PDF to file.

        Args:
            filepath: Output file path.
        """
        pdf_bytes = self.render()
        Path(filepath).write_bytes(pdf_bytes)


class PrintApp(_PrintAppBase):
    """PDF app using Platypus flowables and Canvas drawing.

    Elements: document, paragraph, spacer, pagebreak, image,
    table/row/cell, drawstring, rect, circle, line, charts, qrcode.
    """

    _builder_class = PrintBuilder


class LRCPrintApp(_PrintAppBase):
    """PDF app using Layout/Row/Cell elastic grid.

    Elements: document, layout, row, cell (with elastic dimensions),
    image, paragraph, spacer, charts, qrcode.
    """

    _builder_class = PrintLRCBuilder


class StyledPrintApp(_PrintAppBase):
    """PDF app using declarative styled shapes.

    Elements: document, styledblock (with style inheritance),
    statictext, styledrect, styledcircle, styledline, charts, qrcode.
    """

    _builder_class = PrintStyledBuilder
