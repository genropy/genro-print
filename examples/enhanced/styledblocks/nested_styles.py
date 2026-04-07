# Copyright 2025 Softwell S.r.l. - Licensed under Apache License 2.0
# See LICENSE file for details
"""Example: Nested styledblocks with inherited styles.

Demonstrates style inheritance through nested styledblock containers.
Child blocks inherit parent styles and can override specific attributes.
"""

from pathlib import Path

from genro_print import StyledPrintApp


class NestedStylesDemo(StyledPrintApp):
    """Demonstration of nested styledblocks with style inheritance."""

    def recipe(self, root):
        doc = root.document(width=210.0, height=297.0)

        # Title
        title = doc.styledblock(fontname="Helvetica-Bold", size=20, color="navy")
        title.statictext(x=105, y=25, text="Nested Styles Demo", align="center")

        # --- Example 1: Font inheritance ---
        sec1_title = doc.styledblock(fontname="Helvetica-Bold", size=12)
        sec1_title.statictext(x=20, y=50, text="1. Font Inheritance")

        # Parent block sets base font
        parent1 = doc.styledblock(fontname="Helvetica", size=11, color="black")
        parent1.statictext(x=20, y=65, text="Parent: Helvetica 11pt black")

        # Child inherits fontname, overrides size
        child1a = parent1.styledblock(size=14)
        child1a.statictext(x=30, y=80, text="Child A: inherits font, size=14")

        # Another child overrides color
        child1b = parent1.styledblock(color="red")
        child1b.statictext(x=30, y=95, text="Child B: inherits font+size, color=red")

        # Nested child inherits all, overrides fontname
        child1c = child1b.styledblock(fontname="Helvetica-Bold")
        child1c.statictext(x=40, y=110, text="Grandchild: bold, red (inherited)")

        # --- Example 2: Shape style inheritance ---
        sec2_title = doc.styledblock(fontname="Helvetica-Bold", size=12)
        sec2_title.statictext(x=20, y=135, text="2. Shape Style Inheritance")

        # Parent sets base shape style
        parent2 = doc.styledblock(
            fill_color="lightblue", stroke_color="navy", stroke_width=1
        )
        parent2.styledrect(x=20, y=145, width=40, height=25)

        # Child overrides fill_color
        child2a = parent2.styledblock(fill_color="lightgreen")
        child2a.styledrect(x=70, y=145, width=40, height=25)

        # Another child overrides stroke
        child2b = parent2.styledblock(stroke_color="red", stroke_width=3)
        child2b.styledrect(x=120, y=145, width=40, height=25)

        # Circles inherit shape style too
        parent2.styledcircle(x_cen=45, y_cen=195, radius=12)
        child2a.styledcircle(x_cen=95, y_cen=195, radius=12)
        child2b.styledcircle(x_cen=145, y_cen=195, radius=12)

        # Labels
        labels = doc.styledblock(fontname="Helvetica", size=8, color="gray")
        labels.statictext(x=35, y=212, text="Parent")
        labels.statictext(x=80, y=212, text="Green fill")
        labels.statictext(x=125, y=212, text="Red stroke")

        # --- Example 3: Complex nesting ---
        sec3_title = doc.styledblock(fontname="Helvetica-Bold", size=12)
        sec3_title.statictext(x=20, y=230, text="3. Complex Nesting")

        # Base style
        base = doc.styledblock(
            fontname="Helvetica",
            size=10,
            color="darkblue",
            fill_color="aliceblue",
            stroke_color="steelblue",
        )
        base.statictext(x=20, y=245, text="Base: darkblue text on aliceblue")
        base.styledrect(x=130, y=238, width=60, height=15)

        # Level 1: override text color
        level1 = base.styledblock(color="darkgreen", fill_color="honeydew")
        level1.statictext(x=30, y=260, text="L1: green text on honeydew")
        level1.styledrect(x=140, y=253, width=50, height=15)

        # Level 2: override stroke
        level2 = level1.styledblock(stroke_color="darkred", stroke_width=2)
        level2.statictext(x=40, y=275, text="L2: red stroke (inherits rest)")
        level2.styledrect(x=150, y=268, width=40, height=15)

        # Footer
        footer = doc.styledblock(fontname="Helvetica", size=8, color="#666666")
        footer.statictext(x=105, y=290, text="Generated with genro-print", align="center")


if __name__ == "__main__":
    report = NestedStylesDemo()
    output = Path(__file__).parent / "nested_styles.pdf"
    report.save(str(output))
    print(f"PDF saved to {output}")
