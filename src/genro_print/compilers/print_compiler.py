# Copyright 2025 Softwell S.r.l. - Licensed under Apache License 2.0
# See LICENSE file for details

"""PrintCompiler — compiler for Platypus + Canvas PDF generation.

Transforms built Bag (from PrintBuilder) into PDF bytes using
BagCompilerBase infrastructure with @compiler dispatch.
"""

from __future__ import annotations

from typing import Any

from genro_bag import Bag, BagNode
from genro_builders.compiler import BagCompilerBase, compiler

from genro_print.compilers.reportlab_backend import ReportLabBackend


class PrintCompiler(BagCompilerBase):
    """Compiler for PrintBuilder — Platypus flowables and Canvas drawing.

    Walks the built Bag, resolves ^pointer values just-in-time,
    and dispatches to ReportLabBackend for PDF generation.
    """

    def compile(self, built_bag: Bag, target: Any = None) -> bytes:  # noqa: ARG002
        """Compile built Bag to PDF bytes."""
        self._backend = ReportLabBackend()
        self._compile_bag(built_bag)
        return self._backend.finalize()

    def _compile_bag(self, bag: Bag) -> None:
        """Walk bag and compile each node."""
        for node in bag:
            self._dispatch_node(node)

    def _dispatch_node(self, node: BagNode) -> None:
        """Dispatch a node to the appropriate handler."""
        tag = node.node_tag or node.label
        ctx = self._build_context(node)

        handler = self._compile_handlers.get(tag)
        if handler:
            if getattr(handler, "_compiler_empty", False):
                self._compile_by_meta(tag, ctx)
            else:
                handler(self, node, ctx)
        else:
            self._compile_by_meta(tag, ctx)

    def _compile_by_meta(self, tag: str, ctx: dict[str, Any]) -> None:
        """Compile using _meta information from element schema."""
        schema = self.builder._class_schema
        schema_node = schema.get_node(tag)
        if schema_node is None:
            return

        meta = schema_node.attr.get("_meta", {})
        compile_type = meta.get("compile_type", "")
        compile_method = meta.get("compile_method", "")

        if compile_type == "platypus":
            self._compile_platypus(tag, ctx)
        elif compile_type == "canvas":
            self._compile_canvas(compile_method, ctx)
        elif compile_type == "graphics":
            self._compile_graphics(tag, ctx)

    def _compile_platypus(self, tag: str, ctx: dict[str, Any]) -> None:
        """Compile a platypus element."""
        if tag == "paragraph":
            self._backend.add_paragraph(
                content=ctx.get("content", ""),
                style=ctx.get("style", "Normal"),
            )
        elif tag == "spacer":
            self._backend.add_spacer(
                width=ctx.get("width", 0.0),
                height=ctx.get("height", 10.0),
            )
        elif tag == "pagebreak":
            self._backend.add_pagebreak()
        elif tag == "image":
            self._backend.add_image(
                src=ctx.get("src", ""),
                width=ctx.get("width"),
                height=ctx.get("height"),
            )

    def _compile_canvas(self, method_name: str, ctx: dict[str, Any]) -> None:
        """Compile a canvas element."""
        attrs = {k: v for k, v in ctx.items()
                 if k not in ("node_value", "node_label", "_node", "children")}
        self._backend.canvas_op(method_name, attrs)

    def _compile_graphics(self, tag: str, ctx: dict[str, Any]) -> None:
        """Compile a graphics element (chart, qrcode)."""
        if tag == "bar_chart":
            self._backend.draw_bar_chart(
                x=ctx.get("x", 0), y=ctx.get("y", 0),
                width=ctx.get("width", 100), height=ctx.get("height", 80),
                data=ctx.get("data"), categories=ctx.get("categories"),
                colors=ctx.get("colors"),
                bar_width=ctx.get("bar_width", 10),
                group_spacing=ctx.get("group_spacing", 5),
            )
        elif tag == "pie_chart":
            self._backend.draw_pie_chart(
                x=ctx.get("x", 0), y=ctx.get("y", 0),
                width=ctx.get("width", 100), height=ctx.get("height", 100),
                data=ctx.get("data"), labels=ctx.get("labels"),
                colors=ctx.get("colors"),
                start_angle=ctx.get("start_angle", 90),
            )
        elif tag == "line_chart":
            self._backend.draw_line_chart(
                x=ctx.get("x", 0), y=ctx.get("y", 0),
                width=ctx.get("width", 100), height=ctx.get("height", 80),
                data=ctx.get("data"), colors=ctx.get("colors"),
                stroke_width=ctx.get("stroke_width", 1),
            )
        elif tag == "qrcode":
            self._backend.draw_qrcode(
                x=ctx.get("x", 0), y=ctx.get("y", 0),
                value=ctx.get("value", ""), size=ctx.get("size", 40),
                bar_width=ctx.get("bar_width", 1),
                bar_height=ctx.get("bar_height", 1),
            )

    # --- Special handlers ---

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
    def table(self, node: BagNode, ctx: dict[str, Any]) -> None:
        """Compile table with rows and cells."""
        rows_data: list[list[str]] = []
        if isinstance(node.value, Bag):
            for row_node in node.value:
                if row_node.node_tag == "row":
                    row_cells: list[str] = []
                    if isinstance(row_node.value, Bag):
                        for cell_node in row_node.value:
                            if cell_node.node_tag == "cell":
                                cell_content = cell_node.attr.get("content", "")
                                if not cell_content and cell_node.value:
                                    cell_content = str(cell_node.value)
                                row_cells.append(cell_content)
                    rows_data.append(row_cells)

        if rows_data:
            self._backend.add_table(
                data=rows_data,
                col_widths=ctx.get("col_widths"),
            )
