# Copyright 2025 Softwell S.r.l. - Licensed under Apache License 2.0
# See LICENSE file for details
"""LRCPrintApp - Base class for Layout/Row/Cell documents.

Workflow:
    1. App instantiated → creates _page (recipe Bag) and _data (data Bag)
    2. recipe(root) → populates the recipe Bag with layout/row/cell structure
    3. render() → compiles the recipe and generates PDF bytes

Example:
    from genro_print import LRCPrintApp

    class MyReport(LRCPrintApp):
        def recipe(self, root):
            layout = root.layout(width=210.0, height=297.0, top=10.0, bottom=10.0)
            row = layout.row(height=30.0)
            row.cell(width=60.0, content="Label")
            row.cell(content="Value")  # elastic width

    if __name__ == "__main__":
        MyReport().save("report.pdf")
"""

from __future__ import annotations

from genro_bag import Bag

from genro_print.builders import LRCPrintBuilder
from genro_print.renderers import LRCReportLabRenderer


class LRCPrintApp:
    """Base class for Layout/Row/Cell documents.

    Subclass and override recipe(root) to define your document.
    The root is a Bag with LRCPrintBuilder - use layout/row/cell methods.
    """

    def __init__(self) -> None:
        self._page = Bag(builder=LRCPrintBuilder)
        self._data = Bag()
        self.recipe(self._page)

    @property
    def page(self) -> Bag:
        """The page Bag (document structure)."""
        return self._page

    @property
    def data(self) -> Bag:
        """The data Bag (application data for future binding)."""
        return self._data

    def recipe(self, root: Bag) -> None:
        """Override this method to build your document.

        Args:
            root: The page Bag. Add elements by calling layout(), row(), cell().
        """

    def render(self) -> bytes:
        """Render the document to PDF bytes.

        Returns:
            PDF content as bytes.
        """
        computed = self._page.builder.compile(self._page)
        renderer = LRCReportLabRenderer(computed)
        return renderer.render()

    def save(self, filepath: str) -> None:
        """Render and save the document to a file.

        Args:
            filepath: Path to save the PDF file.
        """
        pdf_bytes = self.render()
        with open(filepath, "wb") as f:
            f.write(pdf_bytes)
