# Copyright 2025 Softwell S.r.l. - Licensed under Apache License 2.0
# See LICENSE file for details

"""PrintStyledBuilder — declarative styled shapes builder for PDF reports."""

from __future__ import annotations

from typing import ClassVar

from genro_builders import BagBuilderBase

from genro_print.builders.mixins.charts_mixin import ChartsMixin
from genro_print.builders.mixins.document_mixin import DocumentMixin
from genro_print.builders.mixins.styled_mixin import StyledMixin
from genro_print.compilers.styled_print_compiler import StyledPrintCompiler
from genro_print.components.styled_components import StyledComponentsMixin


class PrintStyledBuilder(
    StyledComponentsMixin,
    ChartsMixin,
    StyledMixin,
    DocumentMixin,
    BagBuilderBase,
):
    """Builder for PDF reports using declarative styled elements.

    Combines document, styled elements (styledblock, statictext, styledrect,
    styledcircle, etc.) with style inheritance, and chart elements.

    Example:
        builder = PrintStyledBuilder()
        src = builder.source
        doc = src.document(width=210, height=297)
        block = doc.styledblock(fontname="Helvetica-Bold", size=14, color="navy")
        block.statictext(x=20, y=50, text="Title")
        builder.build()
        pdf_bytes = builder.compile(name="reportlab")
    """

    _compilers: ClassVar[dict[str, type]] = {"reportlab": StyledPrintCompiler}
