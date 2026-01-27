# Copyright 2025 Softwell S.r.l. - Licensed under Apache License 2.0
# See LICENSE file for details
"""Example: Simple table.

This example shows how to create a basic table with rows and cells.
"""

from pathlib import Path

from genro_print.print_app import PrintApp

HERE = Path(__file__).parent


class SimpleTable(PrintApp):
    """Document with a simple table."""

    def recipe(self, root):
        root.document(width=210.0, height=297.0)

        root.paragraph(content="Simple Table Example", style="Heading1")
        root.spacer(height=10.0)

        # Create a table with 3 columns
        table = root.table(col_widths=[50.0, 80.0, 50.0])

        # Header row
        header = table.row()
        header.cell(content="ID")
        header.cell(content="Name")
        header.cell(content="Price")

        # Data rows
        row1 = table.row()
        row1.cell(content="001")
        row1.cell(content="Apple")
        row1.cell(content="1.50")

        row2 = table.row()
        row2.cell(content="002")
        row2.cell(content="Banana")
        row2.cell(content="0.75")

        row3 = table.row()
        row3.cell(content="003")
        row3.cell(content="Orange")
        row3.cell(content="2.00")


if __name__ == "__main__":
    report = SimpleTable()
    output = HERE / "simple_table.pdf"
    report.save(str(output))
    print(f"PDF saved to {output}")
