# Copyright 2025 Softwell S.r.l. - Licensed under Apache License 2.0
# See LICENSE file for details
"""Example: Multiple paragraphs with different styles.

This example shows how to create a document with multiple paragraphs
and spacers for layout control.
"""

from pathlib import Path

from genro_print import PrintApp

HERE = Path(__file__).parent


class MultiParagraph(PrintApp):
    """Document with multiple paragraphs."""

    def recipe(self, root):
        root.document(width=210.0, height=297.0)

        # Title
        root.paragraph(content="Document Title", style="Heading1")
        root.spacer(height=10.0)

        # Introduction
        root.paragraph(content="This is the introduction paragraph.")
        root.spacer(height=5.0)

        # Body paragraphs
        root.paragraph(content="First body paragraph with some content.")
        root.spacer(height=5.0)
        root.paragraph(content="Second body paragraph with more content.")
        root.spacer(height=5.0)
        root.paragraph(content="Third body paragraph to complete the document.")


if __name__ == "__main__":
    report = MultiParagraph()
    output = HERE / "multi_paragraph.pdf"
    report.save(str(output))
    print(f"PDF saved to {output}")
