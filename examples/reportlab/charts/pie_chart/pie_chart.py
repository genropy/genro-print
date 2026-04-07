# Copyright 2025 Softwell S.r.l. - Licensed under Apache License 2.0
# See LICENSE file for details
"""Example: Pie Charts in ReportLab Builder.

Demonstrates pie charts with:
- Simple pie chart
- Pie chart with labels
- Custom colors and start angle
"""

from pathlib import Path

from genro_print import PrintApp


class PieChartDemo(PrintApp):
    """Demonstration of pie chart element."""

    def recipe(self, root):
        doc = root.document(width=210.0, height=297.0)

        # Title
        doc.setfont(psfontname="Helvetica-Bold", size=18)
        doc.drawstring(x=20, y=20, text="Pie Chart Examples")

        # --- Example 1: Simple pie chart ---
        doc.setfont(psfontname="Helvetica-Bold", size=12)
        doc.drawstring(x=20, y=45, text="1. Simple Pie Chart")

        doc.pie_chart(
            data=[35, 25, 20, 15, 5],
            x=20,
            y=55,
            width=70,
            height=70,
            colors=["#4472C4", "#ED7D31", "#A5A5A5", "#FFC000", "#5B9BD5"],
        )

        # Manual legend
        doc.setfont(psfontname="Helvetica", size=8)
        labels = ["Category A (35%)", "Category B (25%)", "Category C (20%)",
                  "Category D (15%)", "Category E (5%)"]
        colors = ["#4472C4", "#ED7D31", "#A5A5A5", "#FFC000", "#5B9BD5"]
        for i, (label, color) in enumerate(zip(labels, colors)):
            y_pos = 60 + i * 6
            doc.setfillcolor(color=color)
            doc.rect(x=100, y=y_pos, width=4, height=4, fill=1, stroke=0)
            doc.setfillcolor(color="black")
            doc.drawstring(x=106, y=y_pos + 1, text=label)

        # --- Example 2: Pie chart with labels ---
        doc.setfont(psfontname="Helvetica-Bold", size=12)
        doc.drawstring(x=20, y=140, text="2. Pie Chart with Labels")

        doc.pie_chart(
            data=[40, 30, 20, 10],
            labels=["Sales", "Marketing", "R&D", "Admin"],
            x=20,
            y=150,
            width=80,
            height=80,
            colors=["#70AD47", "#4472C4", "#ED7D31", "#A5A5A5"],
            start_angle=90,
        )

        # --- Example 3: Different start angle ---
        doc.setfont(psfontname="Helvetica-Bold", size=12)
        doc.drawstring(x=120, y=140, text="3. Different Start Angle")

        doc.pie_chart(
            data=[50, 30, 20],
            labels=["Major", "Medium", "Minor"],
            x=120,
            y=150,
            width=70,
            height=70,
            colors=["#FF6B6B", "#4ECDC4", "#45B7D1"],
            start_angle=0,  # Start from right instead of top
        )

        # --- Example 4: Many slices ---
        doc.setfont(psfontname="Helvetica-Bold", size=12)
        doc.drawstring(x=20, y=245, text="4. Many Slices")

        doc.pie_chart(
            data=[15, 14, 13, 12, 11, 10, 9, 8, 8],
            x=20,
            y=255,
            width=60,
            height=60,
            colors=[
                "#264653", "#2A9D8F", "#E9C46A", "#F4A261", "#E76F51",
                "#606C38", "#283618", "#DDA15E", "#BC6C25"
            ],
        )

        # Footer
        doc.setfont(psfontname="Helvetica", size=8)
        doc.setfillcolor(color="#666666")
        doc.drawstring(x=20, y=290, text="Generated with genro-print")


if __name__ == "__main__":
    report = PieChartDemo()
    output = Path(__file__).parent / "pie_chart.pdf"
    report.save(str(output))
    print(f"PDF saved to {output}")
