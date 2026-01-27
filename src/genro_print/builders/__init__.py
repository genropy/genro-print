# Copyright 2025 Softwell S.r.l. - Licensed under Apache License 2.0
# See LICENSE file for details

"""Print builders for genro-print."""

from genro_print.builders.lrc_builder import LRCPrintBuilder

__all__ = [
    "LRCPrintBuilder",
]

# ReportLabBuilder is optional - only available if reportlab is installed
try:
    from genro_print.builders.reportlab import ReportLabBuilder as ReportLabBuilder

    __all__.append("ReportLabBuilder")
except ImportError:
    pass
