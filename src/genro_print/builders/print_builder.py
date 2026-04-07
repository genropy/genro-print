# Copyright 2025 Softwell S.r.l. - Licensed under Apache License 2.0
# See LICENSE file for details

"""PrintBuilder — Platypus + Canvas builder for classic PDF reports."""

from __future__ import annotations

from typing import ClassVar

from genro_builders import BagBuilderBase

from genro_print.builders.mixins.canvas_mixin import CanvasMixin
from genro_print.builders.mixins.charts_mixin import ChartsMixin
from genro_print.builders.mixins.document_mixin import DocumentMixin
from genro_print.builders.mixins.platypus_mixin import PlatypusMixin
from genro_print.compilers.print_compiler import PrintCompiler


class PrintBuilder(
    ChartsMixin,
    CanvasMixin,
    PlatypusMixin,
    DocumentMixin,
    BagBuilderBase,
):
    """Builder for classic PDF reports using Platypus flowables and Canvas drawing.

    Combines document, platypus (paragraph, table, image, etc.),
    canvas (drawstring, rect, circle, line, etc.), and chart elements.

    Example:
        builder = PrintBuilder()
        builder.source.document(width=210, height=297)
        builder.source.paragraph(content="Hello World", style="Normal")
        builder.build()
        pdf_bytes = builder.compile(name="reportlab")
    """

    _compilers: ClassVar[dict[str, type]] = {"reportlab": PrintCompiler}
