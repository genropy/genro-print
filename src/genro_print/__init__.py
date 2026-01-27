# Copyright 2025 Softwell S.r.l. - Licensed under Apache License 2.0
# See LICENSE file for details

"""
genro-print: Print and PDF generation system for Genropy.

This module implements a Layout/Row/Cell model for document generation with:
- Pure declarative source using genro-bag
- Clean separation between source and compiled output
- ReportLab backend for PDF generation
- PyMuPDF utilities for watermark, merge, preview

Architecture:
    LRCPrintBuilder (Layout/Row/Cell)
        ↓ compile()
    ComputedLayout (resolved dimensions)
        ↓ render()
    ReportLabBuilder → PDF

Example:
    ```python
    from genro_bag import Bag
    from genro_print.builders import LRCPrintBuilder, ReportLabBuilder

    # Build document
    doc = Bag(builder=LRCPrintBuilder)
    layout = doc.layout(width=210, height=297)
    layout.row(height=30).cell(content="Hello World")

    # Compile and render
    computed = LRCPrintBuilder.compile(doc)
    pdf_bytes = ReportLabBuilder(computed).render()
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

# Optional: PdfUtils (requires pymupdf)
try:
    from genro_print.utils import PdfUtils as PdfUtils

    __all__.append("PdfUtils")
except ImportError:
    pass
