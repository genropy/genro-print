# Copyright 2025 Softwell S.r.l. - Licensed under Apache License 2.0
# See LICENSE file for details

"""Utility functions for genro-print."""

# PdfUtils is optional - only available if pymupdf is installed
try:
    from genro_print.utils.pdf_utils import PdfUtils

    __all__ = ["PdfUtils"]
except ImportError:
    __all__ = []
