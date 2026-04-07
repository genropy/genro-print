# Copyright 2025 Softwell S.r.l. - Licensed under Apache License 2.0
# See LICENSE file for details
"""Example: Styled table with colors and alignment.

This example shows how to create a table with styling options.
"""

from pathlib import Path

from genro_print import PrintApp

HERE = Path(__file__).parent


class StyledTable(PrintApp):
    """Document with a styled table."""

    def recipe(self, root):
        root.document(width=210.0, height=297.0)

        root.paragraph(content="Styled Table Example", style="Heading1")
        root.spacer(height=10.0)

        # Create a styled table
        table = root.table(
            col_widths=[40.0, 100.0, 60.0, 60.0],
            style="grid",
        )

        # Header row with background
        header = table.row()
        header.cell(content="Code", align="CENTER", bgcolor="#CCCCCC")
        header.cell(content="Description", align="LEFT", bgcolor="#CCCCCC")
        header.cell(content="Qty", align="CENTER", bgcolor="#CCCCCC")
        header.cell(content="Total", align="RIGHT", bgcolor="#CCCCCC")

        # Data rows with alternating colors
        row1 = table.row()
        row1.cell(content="A001", align="CENTER")
        row1.cell(content="Professional Services")
        row1.cell(content="10", align="CENTER")
        row1.cell(content="1,000.00", align="RIGHT")

        row2 = table.row()
        row2.cell(content="A002", align="CENTER", bgcolor="#F0F0F0")
        row2.cell(content="Software License", bgcolor="#F0F0F0")
        row2.cell(content="5", align="CENTER", bgcolor="#F0F0F0")
        row2.cell(content="2,500.00", align="RIGHT", bgcolor="#F0F0F0")

        row3 = table.row()
        row3.cell(content="A003", align="CENTER")
        row3.cell(content="Support Package")
        row3.cell(content="1", align="CENTER")
        row3.cell(content="500.00", align="RIGHT")

        # Total row
        root.spacer(height=5.0)
        total_table = root.table(col_widths=[200.0, 60.0])
        total_row = total_table.row()
        total_row.cell(content="TOTAL:", align="RIGHT", bgcolor="#EEEEEE")
        total_row.cell(content="4,000.00", align="RIGHT", bgcolor="#EEEEEE")


if __name__ == "__main__":
    report = StyledTable()
    output = HERE / "styled_table.pdf"
    report.save(str(output))
    print(f"PDF saved to {output}")
