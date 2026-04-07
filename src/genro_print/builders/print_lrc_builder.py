# Copyright 2025 Softwell S.r.l. - Licensed under Apache License 2.0
# See LICENSE file for details

"""PrintLRCBuilder — Layout/Row/Cell builder for elastic grid PDF reports."""

from __future__ import annotations

from typing import ClassVar

from genro_builders import BagBuilderBase

from genro_print.builders.mixins.charts_mixin import ChartsMixin
from genro_print.builders.mixins.document_mixin import DocumentMixin
from genro_print.builders.mixins.lrc_mixin import LRCMixin
from genro_print.compilers.lrc_print_compiler import LRCPrintCompiler
from genro_print.components.lrc_components import LRCComponentsMixin


class PrintLRCBuilder(
    LRCComponentsMixin,
    ChartsMixin,
    LRCMixin,
    DocumentMixin,
    BagBuilderBase,
):
    """Builder for PDF reports using the Layout/Row/Cell elastic grid model.

    Combines document, LRC (layout, row, cell with elastic dimensions),
    and chart elements.

    Example:
        builder = PrintLRCBuilder()
        src = builder.source
        layout = src.layout(width=210, height=297, top=10, bottom=10)
        row = layout.row(height=30)
        row.cell(width=60, content="Logo")
        row.cell(content="Title")  # elastic width
        builder.build()
        pdf_bytes = builder.compile(name="reportlab")
    """

    _compilers: ClassVar[dict[str, type]] = {"reportlab": LRCPrintCompiler}
