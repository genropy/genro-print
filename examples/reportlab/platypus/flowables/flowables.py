# Copyright 2025 Softwell S.r.l. - Licensed under Apache License 2.0
# See LICENSE file for details
"""Example: Platypus flowables demonstration.

This example shows how Platypus flowables automatically handle:
- Text wrapping in paragraphs
- Page breaks when content overflows
- Table layout and cell wrapping
"""

from pathlib import Path

from genro_print.print_app import PrintApp

HERE = Path(__file__).parent


class FlowablesDemo(PrintApp):
    """Demonstration of Platypus flowables."""

    def recipe(self, root):
        root.document(width=210.0, height=297.0)

        # Title
        root.paragraph(content="Platypus Flowables Demo", style="Title")
        root.spacer(height=10.0)

        # Section 1: Paragraphs with automatic wrapping
        root.paragraph(content="1. Automatic Text Wrapping", style="Heading1")
        root.spacer(height=5.0)

        long_text = (
            "This is a long paragraph that demonstrates how Platypus automatically "
            "wraps text to fit within the page margins. The text will flow naturally "
            "from line to line without any manual intervention. This is one of the "
            "key features of Platypus - it handles all the complex layout calculations "
            "for you, so you can focus on the content rather than the formatting. "
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod "
            "tempor incididunt ut labore et dolore magna aliqua."
        )
        root.paragraph(content=long_text)
        root.spacer(height=10.0)

        # Section 2: Multiple paragraphs
        root.paragraph(content="2. Multiple Paragraphs", style="Heading1")
        root.spacer(height=5.0)

        for i in range(5):
            root.paragraph(
                content=f"Paragraph {i + 1}: This is some sample text that will be "
                f"wrapped automatically. Each paragraph is a separate flowable."
            )
            root.spacer(height=5.0)

        # Section 3: Tables
        root.paragraph(content="3. Tables as Flowables", style="Heading1")
        root.spacer(height=5.0)

        table = root.table(col_widths=[30.0, 100.0, 50.0])

        # Header
        header = table.row()
        header.cell(content="ID")
        header.cell(content="Description")
        header.cell(content="Value")

        # Data rows
        for i in range(10):
            row = table.row()
            row.cell(content=str(i + 1))
            row.cell(content=f"Item number {i + 1} with description")
            row.cell(content=f"{(i + 1) * 100}.00")

        root.spacer(height=10.0)

        # Section 4: Page breaks
        root.paragraph(content="4. Automatic Page Breaks", style="Heading1")
        root.spacer(height=5.0)

        root.paragraph(
            content="When content exceeds the page height, Platypus automatically "
            "creates new pages. The following paragraphs will demonstrate this."
        )
        root.spacer(height=5.0)

        # Generate enough content to cause page breaks
        for i in range(20):
            root.paragraph(
                content=f"Block {i + 1}: Lorem ipsum dolor sit amet, consectetur "
                "adipiscing elit. Sed do eiusmod tempor incididunt ut labore et "
                "dolore magna aliqua. Ut enim ad minim veniam, quis nostrud "
                "exercitation ullamco laboris."
            )
            root.spacer(height=8.0)


if __name__ == "__main__":
    report = FlowablesDemo()
    output = HERE / "flowables.pdf"
    report.save(str(output))
    print(f"PDF saved to {output}")
