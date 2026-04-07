# Copyright 2025 Softwell S.r.l. - Licensed under Apache License 2.0
# See LICENSE file for details

"""StyledPrintCompiler — compiler for styled elements PDF generation.

Transforms built Bag (from PrintStyledBuilder) into PDF bytes.
Handles style inheritance through styledblock containers.
"""

from __future__ import annotations

from typing import Any

from genro_bag import Bag, BagNode
from genro_builders.compiler import BagCompilerBase, compiler

from genro_print.builders.mixins.styled_mixin import STYLE_ATTRS
from genro_print.compilers.reportlab_backend import ReportLabBackend


class StyledPrintCompiler(BagCompilerBase):
    """Compiler for PrintStyledBuilder — declarative styled shapes.

    Handles style inheritance: styledblock attributes propagate
    to child elements unless overridden.
    """

    def compile(self, built_bag: Bag, target: Any = None) -> bytes:  # noqa: ARG002
        """Compile built Bag to PDF bytes."""
        self._backend = ReportLabBackend()
        self._compile_with_styles(built_bag, inherited_style={})
        return self._backend.finalize()

    def _compile_with_styles(self, bag: Bag, inherited_style: dict[str, Any]) -> None:
        """Walk bag and compile elements with style inheritance."""
        for node in bag:
            tag = node.node_tag or node.label
            ctx = self._build_context(node)

            handler = self._compile_handlers.get(tag)
            if handler and not getattr(handler, "_compiler_empty", False):
                handler(self, node, ctx, inherited_style)
            else:
                self._compile_styled_element(tag, ctx, inherited_style)

    def _get_style_attrs(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Extract style attributes from node attributes."""
        return {k: v for k, v in attrs.items() if k in STYLE_ATTRS and v is not None}

    def _merge_style(self, inherited: dict[str, Any], node_attrs: dict[str, Any]) -> dict[str, Any]:
        """Merge inherited styles with node's own styles."""
        result = dict(inherited)
        result.update(self._get_style_attrs(node_attrs))
        return result

    def _compile_styled_element(self, tag: str, ctx: dict[str, Any],
                                inherited_style: dict[str, Any]) -> None:
        """Compile a styled canvas element."""
        style = self._merge_style(inherited_style, ctx)

        if tag == "statictext":
            self._backend.draw_statictext(
                x=ctx.get("x", 0), y=ctx.get("y", 0),
                text=ctx.get("text", ""), align=ctx.get("align", "left"),
                style=style,
            )
        elif tag == "styledline":
            line_style = dict(style)
            if "color" in style and "stroke_color" not in style:
                line_style["stroke_color"] = style["color"]
            self._backend.draw_styledline(
                x1=ctx.get("x1", 0), y1=ctx.get("y1", 0),
                x2=ctx.get("x2", 10), y2=ctx.get("y2", 10),
                style=line_style,
            )
        elif tag == "styledrect":
            self._backend.draw_styledrect(
                x=ctx.get("x", 0), y=ctx.get("y", 0),
                width=ctx.get("width", 10), height=ctx.get("height", 10),
                radius=ctx.get("radius", 0),
                style=style,
            )
        elif tag == "styledcircle":
            self._backend.draw_styledcircle(
                x_cen=ctx.get("x_cen", 0), y_cen=ctx.get("y_cen", 0),
                radius=ctx.get("radius", 5),
                style=style,
            )
        elif tag == "styledellipse":
            self._backend.draw_styledellipse(
                x1=ctx.get("x1", 0), y1=ctx.get("y1", 0),
                x2=ctx.get("x2", 10), y2=ctx.get("y2", 5),
                style=style,
            )
        elif tag == "styledimage":
            self._backend.draw_styledimage(
                image_path=ctx.get("image", ""),
                x=ctx.get("x", 0), y=ctx.get("y", 0),
                width=ctx.get("width"), height=ctx.get("height"),
                mask=ctx.get("mask"),
                preserve_aspect_ratio=ctx.get("preserve_aspect_ratio", False),
            )

    # --- Special handlers ---

    @compiler()
    def document(self, node: BagNode, ctx: dict[str, Any],
                 inherited_style: dict[str, Any] | None = None) -> None:  # noqa: ARG002
        """Compile document: set page and compile children."""
        self._backend.set_page(
            width=ctx.get("width", 210.0),
            height=ctx.get("height", 297.0),
            left_margin=ctx.get("left_margin", 10.0),
            right_margin=ctx.get("right_margin", 10.0),
            top_margin=ctx.get("top_margin", 10.0),
            bottom_margin=ctx.get("bottom_margin", 10.0),
        )
        style = self._get_style_attrs(ctx)
        if isinstance(node.value, Bag):
            self._compile_with_styles(node.value, style)

    @compiler()
    def styledblock(self, node: BagNode, ctx: dict[str, Any],
                    inherited_style: dict[str, Any] | None = None) -> None:
        """Compile styledblock: merge styles and compile children."""
        merged = self._merge_style(inherited_style or {}, ctx)
        if isinstance(node.value, Bag):
            self._compile_with_styles(node.value, merged)

    @compiler()
    def bar_chart(self, node: BagNode, ctx: dict[str, Any],  # noqa: ARG002
                  inherited_style: dict[str, Any] | None = None) -> None:  # noqa: ARG002
        """Compile bar chart."""
        self._backend.draw_bar_chart(
            x=ctx.get("x", 0), y=ctx.get("y", 0),
            width=ctx.get("width", 100), height=ctx.get("height", 80),
            data=ctx.get("data"), categories=ctx.get("categories"),
            colors=ctx.get("colors"),
            bar_width=ctx.get("bar_width", 10),
            group_spacing=ctx.get("group_spacing", 5),
        )

    @compiler()
    def pie_chart(self, node: BagNode, ctx: dict[str, Any],  # noqa: ARG002
                  inherited_style: dict[str, Any] | None = None) -> None:  # noqa: ARG002
        """Compile pie chart."""
        self._backend.draw_pie_chart(
            x=ctx.get("x", 0), y=ctx.get("y", 0),
            width=ctx.get("width", 100), height=ctx.get("height", 100),
            data=ctx.get("data"), labels=ctx.get("labels"),
            colors=ctx.get("colors"),
            start_angle=ctx.get("start_angle", 90),
        )

    @compiler()
    def line_chart(self, node: BagNode, ctx: dict[str, Any],  # noqa: ARG002
                   inherited_style: dict[str, Any] | None = None) -> None:  # noqa: ARG002
        """Compile line chart."""
        self._backend.draw_line_chart(
            x=ctx.get("x", 0), y=ctx.get("y", 0),
            width=ctx.get("width", 100), height=ctx.get("height", 80),
            data=ctx.get("data"), colors=ctx.get("colors"),
            stroke_width=ctx.get("stroke_width", 1),
        )

    @compiler()
    def qrcode(self, node: BagNode, ctx: dict[str, Any],  # noqa: ARG002
               inherited_style: dict[str, Any] | None = None) -> None:  # noqa: ARG002
        """Compile QR code."""
        self._backend.draw_qrcode(
            x=ctx.get("x", 0), y=ctx.get("y", 0),
            value=ctx.get("value", ""), size=ctx.get("size", 40),
            bar_width=ctx.get("bar_width", 1),
            bar_height=ctx.get("bar_height", 1),
        )
