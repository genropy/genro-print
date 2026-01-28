# Copyright 2025 Softwell S.r.l. - Licensed under Apache License 2.0
# See LICENSE file for details
"""Example: labeledtext component demo.

Demonstrates the labeledtext component for labeled fields.
"""

from pathlib import Path

from genro_print.enhanced_print_app import EnhancedPrintApp


class LabeledTextDemo(EnhancedPrintApp):
    """Demonstration of labeledtext component."""

    def recipe(self, root):
        doc = root.document(width=210.0, height=297.0)

        # Title
        doc.statictext(
            x=105, y=20, text="Labeled Text Component Demo",
            align="center", fontname="Helvetica-Bold", size=16, color="navy"
        )

        # --- Section 1: Basic labeled text ---
        doc.statictext(x=20, y=45, text="1. Basic Labeled Text",
                       fontname="Helvetica-Bold", size=12)

        doc.labeledtext(x=20, y=60, label="Nome:", value="Mario Rossi")
        doc.labeledtext(x=20, y=75, label="Email:", value="mario.rossi@example.com")
        doc.labeledtext(x=20, y=90, label="Telefono:", value="+39 02 1234567")

        # --- Section 2: With border bottom (underline) ---
        doc.statictext(x=20, y=115, text="2. With Underline",
                       fontname="Helvetica-Bold", size=12)

        doc.labeledtext(x=20, y=130, label="Fattura N°:", value="2025/001",
                        border_bottom=True)
        doc.labeledtext(x=20, y=150, label="Data:", value="27/01/2025",
                        border_bottom=True)
        doc.labeledtext(x=20, y=170, label="Importo:", value="€ 1.220,00",
                        border_bottom=True, border_color="navy", border_width=1)

        # --- Section 3: Custom styling ---
        doc.statictext(x=20, y=195, text="3. Custom Styling",
                       fontname="Helvetica-Bold", size=12)

        # Label not bold
        doc.labeledtext(x=20, y=210, label="Campo:", value="valore",
                        label_bold=False)

        # Fixed label width for alignment
        doc.labeledtext(x=20, y=225, label="Nome:", value="Mario",
                        label_width=30)
        doc.labeledtext(x=20, y=240, label="Cognome:", value="Rossi",
                        label_width=30)
        doc.labeledtext(x=20, y=255, label="CF:", value="RSSMRA80A01H501X",
                        label_width=30)

        # Footer
        doc.statictext(
            x=105, y=290, text="Generated with genro-print",
            align="center", fontname="Helvetica", size=8, color="#666666"
        )


if __name__ == "__main__":
    report = LabeledTextDemo()
    output = Path(__file__).parent / "labeled_text_demo.pdf"
    report.save(str(output))
    print(f"PDF saved to {output}")
