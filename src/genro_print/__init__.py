# Copyright 2025 Softwell S.r.l. - Licensed under Apache License 2.0
# See LICENSE file for details

"""genro-print: Print and PDF generation system for Genropy.

Three builder types for different PDF generation approaches:

1. PrintBuilder (Platypus + Canvas) — classic PDF reports
2. PrintLRCBuilder (Layout/Row/Cell) — elastic grid layout
3. PrintStyledBuilder (Styled elements) — declarative styled shapes

Each builder has a corresponding app class and compiler:

    PrintApp / PrintBuilder / PrintCompiler
    LRCPrintApp / PrintLRCBuilder / LRCPrintCompiler
    StyledPrintApp / PrintStyledBuilder / StyledPrintCompiler
"""

__version__ = "0.2.0"

# Builders
from genro_print.builders import PrintBuilder, PrintLRCBuilder, PrintStyledBuilder

# Computed data structures
from genro_print.computed import ComputedCell, ComputedLayout, ComputedRow

# App classes
from genro_print.print_app import LRCPrintApp, PrintApp, StyledPrintApp

__all__ = [
    "ComputedCell",
    "ComputedLayout",
    "ComputedRow",
    "LRCPrintApp",
    "PrintApp",
    "PrintBuilder",
    "PrintLRCBuilder",
    "PrintStyledBuilder",
    "StyledPrintApp",
    "__version__",
]

# Optional: PdfUtils (requires pymupdf)
try:
    from genro_print.utils import PdfUtils as PdfUtils

    __all__.append("PdfUtils")
except ImportError:
    pass
