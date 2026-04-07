# Copyright 2025 Softwell S.r.l. - Licensed under Apache License 2.0
# See LICENSE file for details
"""Example: Invoice document.

This example shows how to create a complete invoice document
combining paragraphs, tables, and layout.
"""

from pathlib import Path

from genro_print import PrintApp

HERE = Path(__file__).parent


class Invoice(PrintApp):
    """Invoice document example."""

    def recipe(self, root):
        root.document(width=210.0, height=297.0)

        # Header
        root.paragraph(content="INVOICE", style="Title")
        root.spacer(height=5.0)

        # Invoice info table
        info_table = root.table(col_widths=[100.0, 100.0])
        row1 = info_table.row()
        row1.cell(content="Invoice Number:")
        row1.cell(content="INV-2025-001")
        row2 = info_table.row()
        row2.cell(content="Date:")
        row2.cell(content="January 27, 2025")
        row3 = info_table.row()
        row3.cell(content="Due Date:")
        row3.cell(content="February 27, 2025")

        root.spacer(height=20.0)

        # Customer info
        root.paragraph(content="Bill To:", style="Heading2")
        root.paragraph(content="Acme Corporation")
        root.paragraph(content="123 Business Street")
        root.paragraph(content="New York, NY 10001")
        root.paragraph(content="United States")

        root.spacer(height=20.0)

        # Items table
        root.paragraph(content="Items:", style="Heading2")
        root.spacer(height=5.0)

        items_table = root.table(col_widths=[30.0, 150.0, 40.0, 50.0, 60.0])

        # Header
        header = items_table.row()
        header.cell(content="#", align="CENTER", bgcolor="#333333")
        header.cell(content="Description", bgcolor="#333333")
        header.cell(content="Qty", align="CENTER", bgcolor="#333333")
        header.cell(content="Price", align="RIGHT", bgcolor="#333333")
        header.cell(content="Total", align="RIGHT", bgcolor="#333333")

        # Items
        row1 = items_table.row()
        row1.cell(content="1", align="CENTER")
        row1.cell(content="Web Development Services")
        row1.cell(content="40", align="CENTER")
        row1.cell(content="75.00", align="RIGHT")
        row1.cell(content="3,000.00", align="RIGHT")

        row2 = items_table.row()
        row2.cell(content="2", align="CENTER", bgcolor="#F5F5F5")
        row2.cell(content="Hosting (Annual)", bgcolor="#F5F5F5")
        row2.cell(content="1", align="CENTER", bgcolor="#F5F5F5")
        row2.cell(content="500.00", align="RIGHT", bgcolor="#F5F5F5")
        row2.cell(content="500.00", align="RIGHT", bgcolor="#F5F5F5")

        row3 = items_table.row()
        row3.cell(content="3", align="CENTER")
        row3.cell(content="SSL Certificate")
        row3.cell(content="1", align="CENTER")
        row3.cell(content="99.00", align="RIGHT")
        row3.cell(content="99.00", align="RIGHT")

        root.spacer(height=10.0)

        # Totals
        totals_table = root.table(col_widths=[220.0, 60.0, 60.0])

        subtotal = totals_table.row()
        subtotal.cell(content="")
        subtotal.cell(content="Subtotal:", align="RIGHT")
        subtotal.cell(content="3,599.00", align="RIGHT")

        tax = totals_table.row()
        tax.cell(content="")
        tax.cell(content="Tax (10%):", align="RIGHT")
        tax.cell(content="359.90", align="RIGHT")

        total = totals_table.row()
        total.cell(content="", bgcolor="#EEEEEE")
        total.cell(content="TOTAL:", align="RIGHT", bgcolor="#EEEEEE")
        total.cell(content="3,958.90", align="RIGHT", bgcolor="#EEEEEE")

        root.spacer(height=30.0)

        # Payment info
        root.paragraph(content="Payment Information:", style="Heading2")
        root.paragraph(content="Bank: First National Bank")
        root.paragraph(content="Account: 1234-5678-9012")
        root.paragraph(content="SWIFT: FNBKUS33")

        root.spacer(height=20.0)

        # Footer
        root.paragraph(content="Thank you for your business!")
        root.paragraph(content="Payment is due within 30 days.")


if __name__ == "__main__":
    report = Invoice()
    output = HERE / "invoice.pdf"
    report.save(str(output))
    print(f"PDF saved to {output}")
