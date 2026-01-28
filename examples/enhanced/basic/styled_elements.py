# Copyright 2025 Softwell S.r.l. - Licensed under Apache License 2.0
# See LICENSE file for details
"""Example: Styled elements with inheritance and override.

Demonstrates styledblock with multiple elements where some override
the inherited style attributes.
"""

from pathlib import Path

from genro_print.enhanced_print_app import EnhancedPrintApp


class StyledElementsDemo(EnhancedPrintApp):
    """Demonstration of styled elements with inheritance and override."""

    def recipe(self, root):
        doc = root.document(width=210.0, height=297.0)

        # Title
        doc.statictext(
            x=105, y=25, text="Styled Elements Demo",
            align="center", fontname="Helvetica-Bold", size=18, color="navy"
        )
        doc.statictext(
            x=105, y=38, text="styledblock with inheritance and override",
            align="center", fontname="Helvetica", size=10, color="gray"
        )

        # --- Section 1: Text block with overrides ---
        doc.statictext(x=20, y=55, text="1. Text Block (5 elements, 2 override)",
                       fontname="Helvetica-Bold", size=12)

        # One styledblock, multiple elements, some override
        text_block = doc.styledblock(fontname="Helvetica", size=11, color="black")
        text_block.statictext(x=20, y=70, text="Inherited: Helvetica 11pt black")
        text_block.statictext(x=20, y=82, text="Inherited: same style")
        text_block.statictext(x=20, y=94, text="Override color: RED", color="red")
        text_block.statictext(x=20, y=106, text="Inherited: back to black")
        text_block.statictext(x=20, y=118, text="Override size+color: 14pt blue",
                              size=14, color="blue")

        # --- Section 2: Rectangles block with overrides ---
        doc.statictext(x=20, y=140, text="2. Rectangles Block (4 shapes, 2 override)",
                       fontname="Helvetica-Bold", size=12)

        # One styledblock for shapes
        shapes = doc.styledblock(fill_color="lightblue", stroke_color="navy", stroke_width=1)
        shapes.styledrect(x=20, y=150, width=40, height=25)  # inherited
        shapes.styledrect(x=70, y=150, width=40, height=25)  # inherited
        shapes.styledrect(x=120, y=150, width=40, height=25,
                          fill_color="lightgreen", stroke_color="darkgreen")  # override
        shapes.styledrect(x=170, y=150, width=20, height=25)  # inherited

        # Labels
        doc.statictext(x=30, y=180, text="inherited", fontname="Helvetica", size=8, color="gray")
        doc.statictext(x=80, y=180, text="inherited", fontname="Helvetica", size=8, color="gray")
        doc.statictext(x=125, y=180, text="override", fontname="Helvetica", size=8, color="darkgreen")
        doc.statictext(x=172, y=180, text="inh.", fontname="Helvetica", size=8, color="gray")

        # --- Section 3: Circles block with overrides ---
        doc.statictext(x=20, y=200, text="3. Circles Block (5 circles, 1 override)",
                       fontname="Helvetica-Bold", size=12)

        circles = doc.styledblock(fill_color="pink", stroke_color="red", stroke_width=1)
        circles.styledcircle(x_cen=35, y_cen=225, radius=12)   # inherited
        circles.styledcircle(x_cen=70, y_cen=225, radius=12)   # inherited
        circles.styledcircle(x_cen=105, y_cen=225, radius=12,
                             fill_color="gold", stroke_color="orange", stroke_width=2)  # override
        circles.styledcircle(x_cen=140, y_cen=225, radius=12)  # inherited
        circles.styledcircle(x_cen=175, y_cen=225, radius=12)  # inherited

        # --- Section 4: Lines block with override ---
        doc.statictext(x=20, y=250, text="4. Lines Block (3 lines, 1 override)",
                       fontname="Helvetica-Bold", size=12)

        lines = doc.styledblock(stroke_color="gray", stroke_width=1)
        lines.styledline(x1=20, y1=260, x2=190, y2=260)  # inherited
        lines.styledline(x1=20, y1=268, x2=190, y2=268,
                         stroke_color="red", stroke_width=3)  # override: thick red
        lines.styledline(x1=20, y1=276, x2=190, y2=276)  # inherited

        # Footer
        doc.statictext(
            x=105, y=290, text="Generated with genro-print",
            align="center", fontname="Helvetica", size=8, color="#666666"
        )


if __name__ == "__main__":
    report = StyledElementsDemo()
    output = Path(__file__).parent / "styled_elements.pdf"
    report.save(str(output))
    print(f"PDF saved to {output}")
