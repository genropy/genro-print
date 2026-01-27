# Copyright 2025 Softwell S.r.l. - Licensed under Apache License 2.0
# See LICENSE file for details
"""Example: Long document with automatic pagination.

This example demonstrates:
- Multi-page documents with automatic page breaks
- Mixed content types across pages
- Tables that span multiple pages
- Consistent styling throughout
"""

from pathlib import Path

from genro_print.print_app import PrintApp

HERE = Path(__file__).parent


class LongDocumentDemo(PrintApp):
    """Demonstration of long document handling with Platypus."""

    def recipe(self, root):
        root.document(width=210.0, height=297.0)

        # Title page content
        root.paragraph(content="Long Document Demo", style="Title")
        root.spacer(height=5.0)
        root.paragraph(
            content="This document demonstrates automatic pagination "
            "across multiple pages with mixed content."
        )
        root.spacer(height=15.0)

        # Chapter 1: Introduction
        root.paragraph(content="Chapter 1: Introduction", style="Heading1")
        root.spacer(height=5.0)

        for i in range(5):
            root.paragraph(
                content=f"Introduction paragraph {i + 1}: Lorem ipsum dolor sit amet, "
                "consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut "
                "labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud "
                "exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat."
            )
            root.spacer(height=5.0)

        # Chapter 2: Data Tables
        root.paragraph(content="Chapter 2: Data Tables", style="Heading1")
        root.spacer(height=5.0)

        root.paragraph(
            content="The following table contains sample data that may span "
            "across multiple pages depending on its length."
        )
        root.spacer(height=5.0)

        # Large table
        table = root.table(col_widths=[20.0, 60.0, 40.0, 40.0, 30.0])

        # Header
        header = table.row()
        header.cell(content="#")
        header.cell(content="Description")
        header.cell(content="Category")
        header.cell(content="Date")
        header.cell(content="Amount")

        # Many data rows
        categories = ["Sales", "Marketing", "Operations", "Development", "Support"]
        for i in range(30):
            row = table.row()
            row.cell(content=str(i + 1))
            row.cell(content=f"Item description for row {i + 1}")
            row.cell(content=categories[i % len(categories)])
            row.cell(content=f"2025-01-{(i % 28) + 1:02d}")
            row.cell(content=f"{(i + 1) * 123.45:.2f}")

        root.spacer(height=10.0)

        # Chapter 3: Detailed Analysis
        root.paragraph(content="Chapter 3: Detailed Analysis", style="Heading1")
        root.spacer(height=5.0)

        sections = [
            ("3.1 Overview", 3),
            ("3.2 Methodology", 4),
            ("3.3 Results", 5),
            ("3.4 Discussion", 4),
            ("3.5 Conclusions", 3),
        ]

        for section_title, para_count in sections:
            root.paragraph(content=section_title, style="Heading2")
            root.spacer(height=3.0)

            for j in range(para_count):
                root.paragraph(
                    content=f"Paragraph {j + 1} of {section_title}: Duis aute irure dolor "
                    "in reprehenderit in voluptate velit esse cillum dolore eu fugiat "
                    "nulla pariatur. Excepteur sint occaecat cupidatat non proident, "
                    "sunt in culpa qui officia deserunt mollit anim id est laborum."
                )
                root.spacer(height=4.0)

        # Chapter 4: Appendix with more tables
        root.paragraph(content="Chapter 4: Appendix", style="Heading1")
        root.spacer(height=5.0)

        root.paragraph(content="A. Reference Data", style="Heading2")
        root.spacer(height=3.0)

        # Another table
        ref_table = root.table(col_widths=[40.0, 80.0, 70.0])

        ref_header = ref_table.row()
        ref_header.cell(content="Code")
        ref_header.cell(content="Name")
        ref_header.cell(content="Description")

        for i in range(15):
            ref_row = ref_table.row()
            ref_row.cell(content=f"REF-{i + 1:03d}")
            ref_row.cell(content=f"Reference Item {i + 1}")
            ref_row.cell(content=f"Description for reference item {i + 1}")

        root.spacer(height=10.0)

        root.paragraph(content="B. Summary Statistics", style="Heading2")
        root.spacer(height=3.0)

        stats = [
            ("Total Records", "45"),
            ("Categories", "5"),
            ("Date Range", "2025-01-01 to 2025-01-28"),
            ("Total Amount", "167,752.35"),
            ("Average Amount", "3,728.94"),
        ]

        stats_table = root.table(col_widths=[80.0, 100.0])
        for label, value in stats:
            stats_row = stats_table.row()
            stats_row.cell(content=label)
            stats_row.cell(content=value)

        root.spacer(height=10.0)

        # Final note
        root.paragraph(
            content="End of document. This demonstrates how Platypus automatically "
            "handles page breaks and maintains consistent formatting across a long "
            "document with mixed content types."
        )


if __name__ == "__main__":
    report = LongDocumentDemo()
    output = HERE / "long_document.pdf"
    report.save(str(output))
    print(f"PDF saved to {output}")
