# Copyright 2025 Softwell S.r.l. - Licensed under Apache License 2.0
# See LICENSE file for details
"""PrintApp - Base class for print documents built with Bag.

Workflow:
    1. App instantiated → creates _page (recipe Bag) and _data (data Bag)
    2. recipe(root) → populates the recipe Bag (the "human-readable recipe")
    3. render() → compiles the recipe and generates PDF bytes

IMPORTANT: recipe() is called ONCE at instantiation to create the recipe.
compile() transforms the recipe into PDF output.

Example:
    from genro_print import PrintApp

    class MyReport(PrintApp):
        def recipe(self, root):
            root.document(width=210.0, height=297.0)
            root.paragraph(content="Hello World")
            root.spacer(height=10.0)
            root.paragraph(content="This is a report")

    if __name__ == "__main__":
        pdf_bytes = MyReport().render()
        # or save to file
        MyReport().save("report.pdf")
"""

from __future__ import annotations

from genro_bag import Bag

from genro_print.builders import ReportLabBuilder


class PrintApp:
    """Base class for print documents built with Bag.

    Subclass and override recipe(root) to define your document.
    The root is a Bag with ReportLabBuilder - use it to add elements.
    """

    def __init__(self) -> None:
        self._page = Bag(builder=ReportLabBuilder)
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
