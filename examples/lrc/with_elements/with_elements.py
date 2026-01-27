# Copyright 2025 Softwell S.r.l. - Licensed under Apache License 2.0
# See LICENSE file for details
"""Example: LRC cells with images, paragraphs, and spacers.

This example demonstrates:
- Adding images inside cells
- Adding paragraphs with styling inside cells
- Using spacers for vertical spacing
- Mixing content types in the same document
"""

from pathlib import Path

from genro_print.lrc_app import LRCPrintApp

HERE = Path(__file__).parent
# Use the sample logo from platypus examples
LOGO_PATH = HERE.parent.parent.parent / "reportlab/platypus/with_images/sample_logo.png"


class CellElementsDemo(LRCPrintApp):
    """Demonstration of cell content elements in LRC layout."""

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

        # === HEADER with logo and title ===
        header = layout.row(height=35.0, border=True)

        # Logo cell
        logo_cell = header.cell(width=40.0, border=True)
        if LOGO_PATH.exists():
            logo_cell.image(src=str(LOGO_PATH), width=30.0, height=30.0, align="center")

        # Title cell with paragraph
        title_cell = header.cell(border=True)  # elastic width
        title_cell.paragraph(
            content="Company Report 2025",
            font_size=18,
            font_name="Helvetica-Bold",
            color="#333333",
        )
        title_cell.spacer(height=3.0)
        title_cell.paragraph(
            content="Quarterly Financial Summary",
            font_size=12,
            color="#666666",
        )

        # === INFO ROW ===
        info_row = layout.row(height=20.0, border=True)

        info_cell1 = info_row.cell(width=60.0, border=True)
        info_cell1.paragraph(content="Date: 2025-01-27", font_size=10)

        info_cell2 = info_row.cell(width=60.0, border=True)
        info_cell2.paragraph(content="Period: Q4 2024", font_size=10)

        info_cell3 = info_row.cell(border=True)  # elastic
        info_cell3.paragraph(content="Status: Final", font_size=10, color="green")

        # === CONTENT SECTION ===
        layout.row(height=8.0, border=True).cell(
            content="Section 1: Executive Summary", border=True
        )

        content_row = layout.row(height=60.0, border=True)

        # Left column with text
        left_cell = content_row.cell(width=120.0, border=True)
        left_cell.paragraph(
            content="Revenue Growth",
            font_size=12,
            font_name="Helvetica-Bold",
        )
        left_cell.spacer(height=2.0)
        left_cell.paragraph(
            content="Total revenue increased by 15% compared to the previous quarter.",
            font_size=10,
        )
        left_cell.spacer(height=3.0)
        left_cell.paragraph(
            content="Key drivers include expanded market presence and new product launches.",
            font_size=10,
            color="#555555",
        )

        # Right column with image
        right_cell = content_row.cell(border=True)  # elastic
        if LOGO_PATH.exists():
            right_cell.image(
                src=str(LOGO_PATH), width=50.0, height=50.0, align="center"
            )

        # === METRICS SECTION ===
        layout.row(height=8.0, border=True).cell(
            content="Section 2: Key Metrics", border=True
        )

        metrics_row = layout.row(height=40.0, border=True)

        # Metric cards
        for metric, value, trend in [
            ("Revenue", "$2.4M", "+15%"),
            ("Users", "45,230", "+8%"),
            ("Orders", "12,450", "+12%"),
        ]:
            metric_cell = metrics_row.cell(border=True)  # elastic, equal widths
            metric_cell.paragraph(
                content=metric,
                font_size=10,
                color="#888888",
            )
            metric_cell.spacer(height=2.0)
            metric_cell.paragraph(
                content=value,
                font_size=16,
                font_name="Helvetica-Bold",
            )
            metric_cell.spacer(height=2.0)
            metric_cell.paragraph(
                content=trend,
                font_size=10,
                color="green",
            )

        # === FOOTER ===
        footer = layout.row(height=15.0, border=True)
        footer_cell = footer.cell(border=True)
        footer_cell.paragraph(
            content="Generated with genro-print - Confidential",
            font_size=8,
            color="#999999",
            align="center",
        )


if __name__ == "__main__":
    report = CellElementsDemo()
    output = HERE / "with_elements.pdf"
    report.save(str(output))
    print(f"PDF saved to {output}")
