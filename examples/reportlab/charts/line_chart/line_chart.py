# Copyright 2025 Softwell S.r.l. - Licensed under Apache License 2.0
# See LICENSE file for details
"""Example: Line Charts in ReportLab Builder.

Demonstrates line charts (line plots) with:
- Single line
- Multiple lines
- Custom colors and stroke width
"""

from pathlib import Path

from genro_print.print_app import PrintApp


class LineChartDemo(PrintApp):
    """Demonstration of line chart element."""

    def recipe(self, root):
        doc = root.document(width=210.0, height=297.0)

        # Title
        doc.setfont(psfontname="Helvetica-Bold", size=18)
        doc.drawstring(x=20, y=20, text="Line Chart Examples")

        # --- Example 1: Single line ---
        doc.setfont(psfontname="Helvetica-Bold", size=12)
        doc.drawstring(x=20, y=45, text="1. Single Line (Time Series)")

        doc.line_chart(
            data=[
                [(0, 10), (1, 15), (2, 13), (3, 18), (4, 22), (5, 19), (6, 25)]
            ],
            x=20,
            y=55,
            width=170,
            height=55,
            colors=["#4472C4"],
            stroke_width=2,
        )

        # --- Example 2: Two lines comparison ---
        doc.setfont(psfontname="Helvetica-Bold", size=12)
        doc.drawstring(x=20, y=125, text="2. Two Lines Comparison")

        doc.line_chart(
            data=[
                [(0, 20), (1, 25), (2, 22), (3, 30), (4, 28), (5, 35)],  # Actual
                [(0, 18), (1, 22), (2, 26), (3, 30), (4, 34), (5, 38)],  # Target
            ],
            x=20,
            y=135,
            width=170,
            height=55,
            colors=["#4472C4", "#ED7D31"],
            stroke_width=2,
        )

        # Legend
        doc.setfont(psfontname="Helvetica", size=9)
        doc.setstrokecolor(color="#4472C4")
        doc.setlinewidth(width=0.5)
        doc.line(x1=70, y1=195, x2=80, y2=195)
        doc.setfillcolor(color="black")
        doc.drawstring(x=82, y=193, text="Actual")

        doc.setstrokecolor(color="#ED7D31")
        doc.line(x1=110, y1=195, x2=120, y2=195)
        doc.setfillcolor(color="black")
        doc.drawstring(x=122, y=193, text="Target")

        # --- Example 3: Three lines ---
        doc.setfont(psfontname="Helvetica-Bold", size=12)
        doc.drawstring(x=20, y=210, text="3. Three Products Performance")

        doc.line_chart(
            data=[
                [(0, 100), (1, 120), (2, 115), (3, 140), (4, 160)],  # Product A
                [(0, 80), (1, 95), (2, 110), (3, 105), (4, 130)],   # Product B
                [(0, 60), (1, 75), (2, 90), (3, 120), (4, 145)],    # Product C
            ],
            x=20,
            y=220,
            width=170,
            height=55,
            colors=["#70AD47", "#5B9BD5", "#FFC000"],
            stroke_width=1.5,
        )

        # Legend
        doc.setfont(psfontname="Helvetica", size=9)
        doc.setstrokecolor(color="#70AD47")
        doc.line(x1=60, y1=280, x2=70, y2=280)
        doc.setfillcolor(color="black")
        doc.drawstring(x=72, y=278, text="Product A")

        doc.setstrokecolor(color="#5B9BD5")
        doc.line(x1=110, y1=280, x2=120, y2=280)
        doc.drawstring(x=122, y=278, text="Product B")

        doc.setstrokecolor(color="#FFC000")
        doc.line(x1=160, y1=280, x2=170, y2=280)
        doc.drawstring(x=172, y=278, text="Product C")

        # Footer
        doc.setfont(psfontname="Helvetica", size=8)
        doc.setfillcolor(color="#666666")
        doc.drawstring(x=20, y=290, text="Generated with genro-print")


if __name__ == "__main__":
    report = LineChartDemo()
    output = Path(__file__).parent / "line_chart.pdf"
    report.save(str(output))
    print(f"PDF saved to {output}")
