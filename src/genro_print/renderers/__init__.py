# Copyright 2025 Softwell S.r.l. - Licensed under Apache License 2.0
# See LICENSE file for details

"""Renderers for genro-print."""

__all__: list[str] = []

# LRCReportLabRenderer is optional - only available if reportlab is installed
try:
    from genro_print.renderers.lrc_reportlab import LRCReportLabRenderer as LRCReportLabRenderer

    __all__.append("LRCReportLabRenderer")
except ImportError:
    pass
