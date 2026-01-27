# Copyright 2025 Softwell S.r.l. - Licensed under Apache License 2.0
# See LICENSE file for details
"""Basic example: Hello World PDF.

This example shows the simplest usage of PrintApp to generate a PDF.
"""

from pathlib import Path

from genro_print.print_app import PrintApp

HERE = Path(__file__).parent


class HelloWorld(PrintApp):
    """Simple Hello World PDF document."""

    def recipe(self, root):
        root.document(width=210.0, height=297.0)
        root.paragraph(content="Hello World!")
        root.spacer(height=20.0)
        root.paragraph(content="This is my first PDF with genro-print.")


if __name__ == "__main__":
    report = HelloWorld()
    output = HERE / "hello_world.pdf"
    report.save(str(output))
    print(f"PDF saved to {output}")
