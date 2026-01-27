# Copyright 2025 Softwell S.r.l. - Licensed under Apache License 2.0
# See LICENSE file for details
"""Example: Bar Charts in ReportLab Builder.

Demonstrates vertical bar charts with:
- Single data series
- Multiple data series (grouped bars)
- Custom colors
- Category labels
"""

from pathlib import Path

from genro_print.print_app import PrintApp


class BarChartDemo(PrintApp):
    """Demonstration of bar chart element."""

    def recipe(self, root):
        doc = root.document(width=210.0, height=297.0)

        # Title
        doc.setfont(psfontname="Helvetica-Bold", size=18)
        doc.drawstring(x=20, y=20, text="Bar Chart Examples")

        # --- Example 1: Simple bar chart ---
        doc.setfont(psfontname="Helvetica-Bold", size=12)
        doc.drawstring(x=20, y=45, text="1. Simple Bar Chart (single series)")

        doc.bar_chart(
            data=[[45, 32, 58, 41, 53]],
            categories=["Jan", "Feb", "Mar", "Apr", "May"],
            x=20,
            y=55,
            width=170,
            height=60,
            colors=["#4472C4"],
        )

        # --- Example 2: Grouped bar chart ---
        doc.setfont(psfontname="Helvetica-Bold", size=12)
        doc.drawstring(x=20, y=130, text="2. Grouped Bar Chart (multiple series)")

        doc.bar_chart(
            data=[
                [35, 25, 45, 30],  # Series 1: 2023
                [42, 38, 52, 35],  # Series 2: 2024
            ],
            categories=["Q1", "Q2", "Q3", "Q4"],
            x=20,
            y=140,
            width=170,
            height=60,
            colors=["#4472C4", "#ED7D31"],
            bar_width=10,
            group_spacing=8,
        )

        # Legend for grouped chart
        doc.setfont(psfontname="Helvetica", size=9)
        doc.setfillcolor(color="#4472C4")
        doc.rect(x=60, y=205, width=4, height=4, fill=1, stroke=0)
        doc.setfillcolor(color="black")
        doc.drawstring(x=66, y=206, text="2023")

        doc.setfillcolor(color="#ED7D31")
        doc.rect(x=90, y=205, width=4, height=4, fill=1, stroke=0)
        doc.setfillcolor(color="black")
        doc.drawstring(x=96, y=206, text="2024")

        # --- Example 3: Three series ---
        doc.setfont(psfontname="Helvetica-Bold", size=12)
        doc.drawstring(x=20, y=220, text="3. Three Series Comparison")

        doc.bar_chart(
            data=[
                [20, 35, 30, 25],  # Product A
                [30, 25, 35, 40],  # Product B
                [25, 30, 28, 32],  # Product C
            ],
            categories=["North", "South", "East", "West"],
            x=20,
            y=230,
            width=170,
            height=55,
            colors=["#70AD47", "#5B9BD5", "#FFC000"],
            bar_width=8,
            group_spacing=6,
        )

        # Footer
        doc.setfont(psfontname="Helvetica", size=8)
        doc.setfillcolor(color="#666666")
        doc.drawstring(x=20, y=290, text="Generated with genro-print")


if __name__ == "__main__":
    report = BarChartDemo()
    output = Path(__file__).parent / "bar_chart.pdf"
    report.save(str(output))
    print(f"PDF saved to {output}")
