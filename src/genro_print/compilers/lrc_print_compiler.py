# Copyright 2025 Softwell S.r.l. - Licensed under Apache License 2.0
# See LICENSE file for details

"""LRCPrintCompiler — compiler for Layout/Row/Cell PDF generation.

Transforms built Bag (from PrintLRCBuilder) into PDF bytes.
Uses LRCResolver for elastic dimension calculation, then
ReportLabBackend for rendering to PDF.
"""

from __future__ import annotations

from typing import Any

from genro_bag import Bag, BagNode
from genro_builders.compiler import BagCompilerBase, compiler

from genro_print.compilers.lrc_resolver import LRCResolver
from genro_print.compilers.reportlab_backend import ReportLabBackend


class LRCPrintCompiler(BagCompilerBase):
    """Compiler for PrintLRCBuilder — Layout/Row/Cell elastic grid.

    Two-stage process:
    1. LRCResolver resolves elastic dimensions -> ComputedLayout
    2. ReportLabBackend renders ComputedLayout -> PDF bytes
    """

    def compile(self, built_bag: Bag, target: Any = None) -> bytes:  # noqa: ARG002
        """Compile built Bag to PDF bytes."""
        self._backend = ReportLabBackend()
        self._resolver = LRCResolver()
        self._compile_bag(built_bag)
        return self._backend.finalize()

    def _compile_bag(self, bag: Bag) -> None:
        """Walk bag and compile each node."""
        for node in bag:
            self._dispatch_node(node)

    def _dispatch_node(self, node: BagNode) -> None:
        """Dispatch a node to the appropriate handler."""
        tag = node.node_tag or node.label
        handler = self._compile_handlers.get(tag)
        if handler and not getattr(handler, "_compiler_empty", False):
            ctx = self._build_context(node)
            handler(self, node, ctx)

    @compiler()
    def document(self, node: BagNode, ctx: dict[str, Any]) -> None:
        """Compile document: set page and compile children."""
        self._backend.set_page(
            width=ctx.get("width", 210.0),
            height=ctx.get("height", 297.0),
            left_margin=ctx.get("left_margin", 10.0),
            right_margin=ctx.get("right_margin", 10.0),
            top_margin=ctx.get("top_margin", 10.0),
            bottom_margin=ctx.get("bottom_margin", 10.0),
        )
        if isinstance(node.value, Bag):
            self._compile_bag(node.value)

    @compiler()
    def layout(self, node: BagNode, ctx: dict[str, Any]) -> None:
        """Compile layout: resolve elastic dimensions and render."""
        width = ctx.get("width", 0) or 210
        height = ctx.get("height", 0) or 297
        computed = self._resolver.resolve(
            node,
            origin_x=0,
            origin_y=0,
            available_width=width,
            available_height=height,
        )
        self._backend.render_layout(computed)

    @compiler()
    def bar_chart(self, node: BagNode, ctx: dict[str, Any]) -> None:  # noqa: ARG002
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
    def pie_chart(self, node: BagNode, ctx: dict[str, Any]) -> None:  # noqa: ARG002
        """Compile pie chart."""
        self._backend.draw_pie_chart(
            x=ctx.get("x", 0), y=ctx.get("y", 0),
            width=ctx.get("width", 100), height=ctx.get("height", 100),
            data=ctx.get("data"), labels=ctx.get("labels"),
            colors=ctx.get("colors"),
            start_angle=ctx.get("start_angle", 90),
        )

    @compiler()
    def line_chart(self, node: BagNode, ctx: dict[str, Any]) -> None:  # noqa: ARG002
        """Compile line chart."""
        self._backend.draw_line_chart(
            x=ctx.get("x", 0), y=ctx.get("y", 0),
            width=ctx.get("width", 100), height=ctx.get("height", 80),
            data=ctx.get("data"), colors=ctx.get("colors"),
            stroke_width=ctx.get("stroke_width", 1),
        )

    @compiler()
    def qrcode(self, node: BagNode, ctx: dict[str, Any]) -> None:  # noqa: ARG002
        """Compile QR code."""
        self._backend.draw_qrcode(
            x=ctx.get("x", 0), y=ctx.get("y", 0),
            value=ctx.get("value", ""), size=ctx.get("size", 40),
            bar_width=ctx.get("bar_width", 1),
            bar_height=ctx.get("bar_height", 1),
        )
