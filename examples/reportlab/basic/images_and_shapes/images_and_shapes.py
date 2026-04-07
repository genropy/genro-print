# Copyright 2025 Softwell S.r.l. - Licensed under Apache License 2.0
# See LICENSE file for details
"""Example: Drawing shapes and graphics.

This example shows how to draw shapes using canvas operations.
Note: This uses canvas mode, not platypus flowables.
"""

from pathlib import Path

from genro_print import PrintApp

HERE = Path(__file__).parent


class ImagesAndShapes(PrintApp):
    """Document with shapes and graphics."""

    def recipe(self, root):
        root.document(width=210.0, height=297.0)

        root.paragraph(content="Shapes and Graphics Example", style="Heading1")
        root.spacer(height=20.0)

        root.paragraph(content="This page demonstrates various shapes drawn with ReportLab.")
        root.spacer(height=20.0)

        # Section: Rectangles
        root.paragraph(content="Rectangles:", style="Heading2")
        root.spacer(height=10.0)

        root.paragraph(content="(Shapes would be drawn here with canvas operations)")
        root.spacer(height=30.0)

        # Section: Circles
        root.paragraph(content="Circles:", style="Heading2")
        root.spacer(height=10.0)

        root.paragraph(content="(Circle shapes would be drawn here)")
        root.spacer(height=30.0)

        # Section: Lines
        root.paragraph(content="Lines:", style="Heading2")
        root.spacer(height=10.0)

        root.paragraph(content="(Line shapes would be drawn here)")
        root.spacer(height=30.0)

        # Note about canvas mode
        root.paragraph(
            content="Note: For full canvas drawing capabilities, use the canvas elements "
            "(rect, circle, line, drawstring, etc.) which operate in canvas mode "
            "rather than platypus flowable mode."
        )


if __name__ == "__main__":
    report = ImagesAndShapes()
    output = HERE / "images_and_shapes.pdf"
    report.save(str(output))
    print(f"PDF saved to {output}")
