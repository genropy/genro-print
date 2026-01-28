# Copyright 2025 Softwell S.r.l. - Licensed under Apache License 2.0
# See LICENSE file for details
"""EnhancedPrintApp - Declarative print documents with inherited styles.

Uses ReportLabEnhancedBuilder for purely declarative API with styledblock
containers and inherited styles.

Example:
    from genro_print import EnhancedPrintApp

    class MyReport(EnhancedPrintApp):
        def recipe(self, root):
            doc = root.document(width=210.0, height=297.0)

            # Block with shared style
            header = doc.styledblock(fontname="Helvetica-Bold", size=18, color="navy")
            header.statictext(x=20, y=30, text="Report Title")

            # Nested block overrides size
            subtitle = header.styledblock(size=12)
            subtitle.statictext(x=20, y=45, text="Generated 2025-01-27")

            # Shapes with shared style
            shapes = doc.styledblock(fill_color="lightblue", stroke_color="navy")
            shapes.styledrect(x=20, y=60, width=170, height=50)
            shapes.styledcircle(x_cen=105, y_cen=85, radius=15)

    if __name__ == "__main__":
        MyReport().save("report.pdf")
"""

from __future__ import annotations

from genro_bag import Bag

from genro_print.builders.reportlab_enhanced_builder import ReportLabEnhancedBuilder


class EnhancedPrintApp:
    """Base class for declarative print documents with inherited styles.

    Subclass and override recipe(root) to define your document.
    The root is a Bag with ReportLabEnhancedBuilder.
    """

    def __init__(self) -> None:
        self._page = Bag(builder=ReportLabEnhancedBuilder)
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
            root: The page Bag. Add elements by calling methods on it.
        """

    def render(self) -> bytes:
        """Render the document to PDF bytes.

        Returns:
            PDF content as bytes.
        """
        computed = self._page.builder.compile(self._page)
        result: bytes = self._page.builder.render(computed)
        return result

    def save(self, filepath: str) -> None:
        """Render and save the document to a file.

        Args:
            filepath: Path to save the PDF file.
        """
        pdf_bytes = self.render()
        with open(filepath, "wb") as f:
            f.write(pdf_bytes)
