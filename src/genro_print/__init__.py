# Copyright 2025 Softwell S.r.l. - Licensed under Apache License 2.0
# See LICENSE file for details

"""
genro-print: Print and PDF generation system for Genropy.

Two approaches for PDF generation:

1. PrintApp (ReportLab Builder) - Direct ReportLab elements:
    ```python
    from genro_print import PrintApp

    class MyReport(PrintApp):
        def recipe(self, root):
            root.document(width=210.0, height=297.0)
            root.paragraph(content="Hello World!")

    MyReport().save("report.pdf")
    ```

2. LRCPrintApp (Layout/Row/Cell) - Elastic grid layout:
    ```python
    from genro_print import LRCPrintApp

    class MyReport(LRCPrintApp):
        def recipe(self, root):
            layout = root.layout(width=210.0, height=297.0)
            row = layout.row(height=30.0)
            row.cell(width=50.0, content="Fixed")
            row.cell(content="Elastic")  # width=0 auto-calculates

    MyReport().save("report.pdf")
    ```
"""

__version__ = "0.1.0"

from genro_print.builders import LRCPrintBuilder
from genro_print.computed import ComputedCell, ComputedLayout, ComputedRow

__all__ = [
    "ComputedCell",
    "ComputedLayout",
    "ComputedRow",
    "LRCPrintBuilder",
    "__version__",
]

# Optional: ReportLabBuilder (requires reportlab)
try:
    from genro_print.builders import ReportLabBuilder as ReportLabBuilder

    __all__.append("ReportLabBuilder")
except ImportError:
    pass

# Optional: PrintApp (requires reportlab)
try:
    from genro_print.print_app import PrintApp as PrintApp

    __all__.append("PrintApp")
except ImportError:
    pass

# Optional: LRCPrintApp (requires reportlab)
try:
    from genro_print.lrc_app import LRCPrintApp as LRCPrintApp

    __all__.append("LRCPrintApp")
except ImportError:
    pass

# Optional: EnhancedPrintApp (requires reportlab)
try:
    from genro_print.enhanced_print_app import EnhancedPrintApp as EnhancedPrintApp

    __all__.append("EnhancedPrintApp")
except ImportError:
    pass

# Optional: ReportLabEnhancedBuilder (requires reportlab)
try:
    from genro_print.builders.reportlab_enhanced_builder import (
        ReportLabEnhancedBuilder as ReportLabEnhancedBuilder,
    )

    __all__.append("ReportLabEnhancedBuilder")
except ImportError:
    pass

# Optional: LRCReportLabRenderer (requires reportlab)
try:
    from genro_print.renderers import LRCReportLabRenderer as LRCReportLabRenderer

    __all__.append("LRCReportLabRenderer")
except ImportError:
    pass

# Optional: PdfUtils (requires pymupdf)
try:
    from genro_print.utils import PdfUtils as PdfUtils

    __all__.append("PdfUtils")
except ImportError:
    pass
