# Copyright 2025 Softwell S.r.l. - Licensed under Apache License 2.0
# See LICENSE file for details
"""Example: Images in Platypus documents.

This example demonstrates:
- Adding images from file paths
- Scaling images to fit
- Mixing images with text flowables
- Images in tables
"""

from pathlib import Path

from genro_print.print_app import PrintApp

HERE = Path(__file__).parent


class WithImagesDemo(PrintApp):
    """Demonstration of image handling in Platypus."""

    def recipe(self, root):
        root.document(width=210.0, height=297.0)

        # Title
        root.paragraph(content="Images in Platypus Demo", style="Title")
        root.spacer(height=10.0)

        # Section 1: Basic image
        root.paragraph(content="1. Basic Image from File", style="Heading1")
        root.spacer(height=5.0)

        root.paragraph(
            content="Images can be loaded from file paths and automatically "
            "scaled to fit within the page margins."
        )
        root.spacer(height=5.0)

        # Add image (using sample logo created earlier)
        logo_path = HERE / "sample_logo.png"
        if logo_path.exists():
            root.image(src=str(logo_path), width=50.0, height=50.0)
        else:
            root.paragraph(content="[Image: sample_logo.png not found]")

        root.spacer(height=10.0)

        # Section 2: Scaled images
        root.paragraph(content="2. Scaled Images", style="Heading1")
        root.spacer(height=5.0)

        root.paragraph(
            content="You can specify width and height to scale images. "
            "Aspect ratio can be preserved or modified."
        )
        root.spacer(height=5.0)

        # Same image at different sizes
        if logo_path.exists():
            root.paragraph(content="Small (25x25mm):")
            root.image(src=str(logo_path), width=25.0, height=25.0)
            root.spacer(height=5.0)

            root.paragraph(content="Medium (50x50mm):")
            root.image(src=str(logo_path), width=50.0, height=50.0)
            root.spacer(height=5.0)

            root.paragraph(content="Large (80x80mm):")
            root.image(src=str(logo_path), width=80.0, height=80.0)

        root.spacer(height=10.0)

        # Section 3: Images mixed with text
        root.paragraph(content="3. Images Mixed with Text", style="Heading1")
        root.spacer(height=5.0)

        root.paragraph(
            content="Platypus treats images as flowables, so they can be "
            "mixed naturally with paragraphs and other elements."
        )
        root.spacer(height=5.0)

        root.paragraph(
            content="Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
            "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."
        )
        root.spacer(height=5.0)

        if logo_path.exists():
            root.image(src=str(logo_path), width=40.0, height=40.0)

        root.spacer(height=5.0)
        root.paragraph(
            content="Ut enim ad minim veniam, quis nostrud exercitation ullamco "
            "laboris nisi ut aliquip ex ea commodo consequat."
        )

        root.spacer(height=10.0)

        # Section 4: Images in tables
        root.paragraph(content="4. Product Catalog (Images in Table)", style="Heading1")
        root.spacer(height=5.0)

        root.paragraph(
            content="Images can be placed inside table cells for catalogs, "
            "product listings, or reports with visual elements."
        )
        root.spacer(height=5.0)

        # Note: For actual table cell images, you'd need cell-level image support
        # This is a simplified example showing the concept
        table = root.table(col_widths=[30.0, 80.0, 40.0, 30.0])

        # Header
        header = table.row()
        header.cell(content="ID")
        header.cell(content="Product")
        header.cell(content="Category")
        header.cell(content="Price")

        # Data rows
        products = [
            ("001", "Widget Pro", "Tools", "29.99"),
            ("002", "Gadget Max", "Electronics", "49.99"),
            ("003", "Gizmo Plus", "Accessories", "19.99"),
            ("004", "Thing Ultra", "Hardware", "79.99"),
        ]

        for pid, name, category, price in products:
            row = table.row()
            row.cell(content=pid)
            row.cell(content=name)
            row.cell(content=category)
            row.cell(content=f"${price}")


if __name__ == "__main__":
    report = WithImagesDemo()
    output = HERE / "with_images.pdf"
    report.save(str(output))
    print(f"PDF saved to {output}")
