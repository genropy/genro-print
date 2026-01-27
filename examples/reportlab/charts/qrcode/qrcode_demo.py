# Copyright 2025 Softwell S.r.l. - Licensed under Apache License 2.0
# See LICENSE file for details
"""Example: QR Codes in ReportLab Builder.

Demonstrates QR codes with:
- URLs
- Plain text
- Different sizes
- Contact info (vCard format)
"""

from pathlib import Path

from genro_print.print_app import PrintApp


class QRCodeDemo(PrintApp):
    """Demonstration of QR code element."""

    def recipe(self, root):
        doc = root.document(width=210.0, height=297.0)

        # Title
        doc.setfont(psfontname="Helvetica-Bold", size=18)
        doc.drawstring(x=20, y=20, text="QR Code Examples")

        # --- Example 1: URL ---
        doc.setfont(psfontname="Helvetica-Bold", size=12)
        doc.drawstring(x=20, y=45, text="1. Website URL")

        doc.qrcode(
            value="https://github.com/genropy/genro-print",
            x=20,
            y=55,
            size=40,
        )

        doc.setfont(psfontname="Helvetica", size=9)
        doc.drawstring(x=20, y=100, text="Scan to visit project repository")

        # --- Example 2: Email ---
        doc.setfont(psfontname="Helvetica-Bold", size=12)
        doc.drawstring(x=90, y=45, text="2. Email Address")

        doc.qrcode(
            value="mailto:info@example.com",
            x=90,
            y=55,
            size=40,
        )

        doc.setfont(psfontname="Helvetica", size=9)
        doc.drawstring(x=90, y=100, text="Scan to send email")

        # --- Example 3: Phone ---
        doc.setfont(psfontname="Helvetica-Bold", size=12)
        doc.drawstring(x=150, y=45, text="3. Phone")

        doc.qrcode(
            value="tel:+391234567890",
            x=150,
            y=55,
            size=40,
        )

        doc.setfont(psfontname="Helvetica", size=9)
        doc.drawstring(x=150, y=100, text="Scan to call")

        # --- Example 4: Plain text ---
        doc.setfont(psfontname="Helvetica-Bold", size=12)
        doc.drawstring(x=20, y=120, text="4. Plain Text Message")

        doc.qrcode(
            value="Welcome to genro-print! This is a PDF generation library.",
            x=20,
            y=130,
            size=50,
        )

        doc.setfont(psfontname="Helvetica", size=9)
        doc.drawstring(x=20, y=185, text="Contains a text message")

        # --- Example 5: WiFi credentials ---
        doc.setfont(psfontname="Helvetica-Bold", size=12)
        doc.drawstring(x=100, y=120, text="5. WiFi Network")

        # WiFi QR format: WIFI:T:WPA;S:NetworkName;P:Password;;
        doc.qrcode(
            value="WIFI:T:WPA;S:MyNetwork;P:SecretPassword;;",
            x=100,
            y=130,
            size=50,
        )

        doc.setfont(psfontname="Helvetica", size=9)
        doc.drawstring(x=100, y=185, text="Scan to connect to WiFi")

        # --- Example 6: Different sizes ---
        doc.setfont(psfontname="Helvetica-Bold", size=12)
        doc.drawstring(x=20, y=205, text="6. Different Sizes")

        # Small
        doc.qrcode(value="Small", x=20, y=215, size=20)
        doc.setfont(psfontname="Helvetica", size=8)
        doc.drawstring(x=20, y=238, text="20mm")

        # Medium
        doc.qrcode(value="Medium", x=50, y=215, size=30)
        doc.drawstring(x=55, y=248, text="30mm")

        # Large
        doc.qrcode(value="Large", x=90, y=215, size=40)
        doc.drawstring(x=100, y=258, text="40mm")

        # Extra large
        doc.qrcode(value="Extra Large", x=140, y=215, size=50)
        doc.drawstring(x=155, y=268, text="50mm")

        # Footer
        doc.setfont(psfontname="Helvetica", size=8)
        doc.setfillcolor(color="#666666")
        doc.drawstring(x=20, y=290, text="Generated with genro-print")


if __name__ == "__main__":
    report = QRCodeDemo()
    output = Path(__file__).parent / "qrcode_demo.pdf"
    report.save(str(output))
    print(f"PDF saved to {output}")
