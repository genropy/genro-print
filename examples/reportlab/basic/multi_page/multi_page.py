# Copyright 2025 Softwell S.r.l. - Licensed under Apache License 2.0
# See LICENSE file for details
"""Example: Multi-page document with page breaks.

This example shows how to create a document spanning multiple pages.
"""

from pathlib import Path

from genro_print.print_app import PrintApp

HERE = Path(__file__).parent


class MultiPage(PrintApp):
    """Document with multiple pages."""

    def recipe(self, root):
        root.document(width=210.0, height=297.0)

        # Page 1: Title page
        root.spacer(height=100.0)
        root.paragraph(content="Multi-Page Document", style="Title")
        root.spacer(height=20.0)
        root.paragraph(content="A demonstration of page breaks and multi-page content")
        root.spacer(height=50.0)
        root.paragraph(content="Page 1 of 3")

        # Page break
        root.pagebreak()

        # Page 2: Content
        root.paragraph(content="Chapter 1: Introduction", style="Heading1")
        root.spacer(height=10.0)

        for i in range(15):
            root.paragraph(
                content=f"This is paragraph {i + 1} of the introduction chapter. "
                "It contains some text to demonstrate how content flows across pages."
            )
            root.spacer(height=5.0)

        # Page break
        root.pagebreak()

        # Page 3: Table of data
        root.paragraph(content="Chapter 2: Data Table", style="Heading1")
        root.spacer(height=10.0)

        table = root.table(col_widths=[30.0, 80.0, 50.0, 50.0])

        header = table.row()
        header.cell(content="#")
        header.cell(content="Item")
        header.cell(content="Value")
        header.cell(content="Status")

        for i in range(20):
            row = table.row()
            row.cell(content=str(i + 1))
            row.cell(content=f"Item number {i + 1}")
            row.cell(content=f"{(i + 1) * 100}")
            row.cell(content="Active" if i % 2 == 0 else "Pending")


if __name__ == "__main__":
    report = MultiPage()
    output = HERE / "multi_page.pdf"
    report.save(str(output))
    print(f"PDF saved to {output}")
