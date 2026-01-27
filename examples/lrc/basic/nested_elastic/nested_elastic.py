# Copyright 2025 Softwell S.r.l. - Licensed under Apache License 2.0
# See LICENSE file for details
"""Example: Nested layouts with elastic dimensions.

This example demonstrates:
- Nested layouts inside cells
- Elastic rows (height=0) that share available space equally
- Elastic cells (width=0) that share available space equally
- Mixed fixed and elastic dimensions
"""

from pathlib import Path

from genro_print.lrc_app import LRCPrintApp

HERE = Path(__file__).parent


class NestedElastic(LRCPrintApp):
    """Document with nested layouts and elastic dimensions."""

    def recipe(self, root):
        # Main layout: A4 with margins
        layout = root.layout(
            width=210.0,
            height=297.0,
            top=10.0,
            bottom=10.0,
            left=10.0,
            right=10.0,
            border_width=0.5,
        )

        # === HEADER: fixed height ===
        header = layout.row(height=25.0, border=True)
        header.cell(width=40.0, content="LOGO", border=True)
        header.cell(content="Company Name - Elastic Width", border=True)  # elastic
        header.cell(width=30.0, content="Date", border=True)

        # === SECTION 1: Three elastic rows sharing space ===
        # Title row (fixed)
        layout.row(height=8.0, border=True).cell(
            content="Section 1: Three elastic rows (height=0)", border=True
        )

        # Three elastic rows - each gets 1/3 of remaining space in this section
        # But first we need a container... let's use a fixed section
        section1 = layout.row(height=60.0, border=True)
        section1_cell = section1.cell(border=True)  # elastic width = full

        # Nested layout inside the cell
        nested1 = section1_cell.layout()
        # Three elastic rows
        r1 = nested1.row(height=0, border=True)  # elastic - gets 20mm
        r1.cell(content="Elastic Row 1 (1/3)", border=True)

        r2 = nested1.row(height=0, border=True)  # elastic - gets 20mm
        r2.cell(content="Elastic Row 2 (1/3)", border=True)

        r3 = nested1.row(height=0, border=True)  # elastic - gets 20mm
        r3.cell(content="Elastic Row 3 (1/3)", border=True)

        # === SECTION 2: Elastic cells in a row ===
        layout.row(height=8.0, border=True).cell(
            content="Section 2: Four elastic cells (width=0)", border=True
        )

        elastic_row = layout.row(height=30.0, border=True)
        elastic_row.cell(content="Cell 1\n(1/4)", border=True)  # elastic
        elastic_row.cell(content="Cell 2\n(1/4)", border=True)  # elastic
        elastic_row.cell(content="Cell 3\n(1/4)", border=True)  # elastic
        elastic_row.cell(content="Cell 4\n(1/4)", border=True)  # elastic

        # === SECTION 3: Mixed fixed and elastic ===
        layout.row(height=8.0, border=True).cell(
            content="Section 3: Mixed fixed (50mm) and elastic cells", border=True
        )

        mixed_row = layout.row(height=25.0, border=True)
        mixed_row.cell(width=50.0, content="Fixed 50mm", border=True)
        mixed_row.cell(content="Elastic 1", border=True)  # shares remaining
        mixed_row.cell(content="Elastic 2", border=True)  # shares remaining
        mixed_row.cell(width=30.0, content="Fixed 30mm", border=True)

        # === SECTION 4: Deep nesting ===
        layout.row(height=8.0, border=True).cell(
            content="Section 4: Nested layout inside nested layout", border=True
        )

        deep_section = layout.row(height=70.0, border=True)
        deep_cell = deep_section.cell(border=True)

        # First level nesting
        level1 = deep_cell.layout(top=2.0, bottom=2.0, left=2.0, right=2.0)

        level1_header = level1.row(height=15.0, border=True)
        level1_header.cell(content="Level 1 Header", border=True)

        level1_body = level1.row(height=0, border=True)  # elastic
        level1_left = level1_body.cell(width=80.0, border=True)
        level1_right = level1_body.cell(border=True)  # elastic

        # Second level nesting (inside left cell)
        level2 = level1_left.layout()
        level2.row(height=0, border=True).cell(content="L2 Row 1", border=True)
        level2.row(height=0, border=True).cell(content="L2 Row 2", border=True)

        # Content in right cell (no nesting)
        # Note: right cell just has content, no nested layout

        # === FOOTER: fixed height ===
        footer = layout.row(height=15.0, border=True)
        footer.cell(content="Footer - Page 1", border=True)


if __name__ == "__main__":
    report = NestedElastic()
    output = HERE / "nested_elastic.pdf"
    report.save(str(output))
    print(f"PDF saved to {output}")
