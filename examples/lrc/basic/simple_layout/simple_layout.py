# Copyright 2025 Softwell S.r.l. - Licensed under Apache License 2.0
# See LICENSE file for details
"""Example: Simple Layout/Row/Cell document.

This example shows the basic usage of LRCPrintApp with layout, rows, and cells.
"""

from pathlib import Path

from genro_print import LRCPrintApp

HERE = Path(__file__).parent


class SimpleLayout(LRCPrintApp):
    """Simple document using Layout/Row/Cell model."""

    def recipe(self, root):
        # Create layout with margins
        layout = root.layout(
            width=210.0,
            height=297.0,
            top=10.0,
            bottom=10.0,
            left=10.0,
            right=10.0,
            border_width=0.3,
        )

        # Header row (fixed height)
        header = layout.row(height=25.0, border=True)
        header.cell(width=50.0, content="LOGO", border=True)
        header.cell(content="Company Name Inc.", border=True)  # elastic

        # Spacer row
        layout.row(height=10.0)

        # Info rows
        info1 = layout.row(height=12.0, border=True)
        info1.cell(width=40.0, content="Name:", border=True)
        info1.cell(content="Mario Rossi", border=True)

        info2 = layout.row(height=12.0, border=True)
        info2.cell(width=40.0, content="Address:", border=True)
        info2.cell(content="Via Roma 1, 20100 Milano", border=True)

        info3 = layout.row(height=12.0, border=True)
        info3.cell(width=40.0, content="Phone:", border=True)
        info3.cell(content="+39 02 1234567", border=True)

        # Spacer
        layout.row(height=10.0)

        # Three column row
        cols = layout.row(height=20.0, border=True)
        cols.cell(content="Column 1", border=True)  # elastic
        cols.cell(content="Column 2", border=True)  # elastic
        cols.cell(content="Column 3", border=True)  # elastic


if __name__ == "__main__":
    report = SimpleLayout()
    output = HERE / "simple_layout.pdf"
    report.save(str(output))
    print(f"PDF saved to {output}")
