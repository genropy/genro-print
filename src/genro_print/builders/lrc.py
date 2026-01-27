# Copyright 2025 Softwell S.r.l. - Licensed under Apache License 2.0
# See LICENSE file for details

"""
LRCPrintBuilder: Layout/Row/Cell Print Builder.

Builder that defines layout(), row(), cell() elements and calculates
elastic dimensions producing a ComputedLayout.

Responsibilities:
- Define user API (same rules as Genropy)
- Handle fractal nesting (Cell can contain Layout)
- Calculate elastic dimensions (height=0, width=0)
- Propagate borders (inheritance)
- Produce ComputedLayout with absolute coordinates

NOT responsible for:
- Generating output (PDF, HTML, etc.) - that's the renderers' job
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from genro_bag import BagBuilderBase
from genro_bag.builder import element

from genro_print.computed import ComputedCell, ComputedLayout, ComputedRow

if TYPE_CHECKING:
    from genro_bag import Bag, BagNode


class LRCPrintBuilder(BagBuilderBase):
    """Builder for Layout/Row/Cell with dimension calculation.

    Example usage:
        ```python
        from genro_bag import Bag
        from genro_print.builders import LRCPrintBuilder

        doc = Bag(builder=LRCPrintBuilder)

        layout = doc.layout(width=210, height=297, top=10, bottom=10, left=10, right=10)
        row = layout.row(height=30)
        row.cell(width=60, content="Logo")
        row.cell(content="Title")  # elastic

        # Compile to ComputedLayout
        computed = LRCPrintBuilder.compile(doc)
        ```
    """

    @element(sub_tags="row")
    def layout(
        self,
        width: float = 0,
        height: float = 0,
        top: float = 0,
        bottom: float = 0,
        left: float = 0,
        right: float = 0,
        um: str = "mm",
        border_width: float = 0,
        border_color: str = "black",
    ) -> None:
        """Layout container - can only contain Row.

        Args:
            width: Total width (0 = inherit from parent)
            height: Total height (0 = inherit from parent)
            top: Top margin
            bottom: Bottom margin
            left: Left margin
            right: Right margin
            um: Unit of measure (default: mm)
            border_width: Border thickness
            border_color: Border color
        """

    @element(sub_tags="cell")
    def row(
        self,
        height: float = 0,
        border: bool | None = None,
    ) -> None:
        """Row - can only contain Cell.

        Args:
            height: Row height (0 = elastic, expands to fill)
            border: Whether it has border (None = inherit from layout)
        """

    @element(sub_tags="layout")
    def cell(
        self,
        width: float = 0,
        border: bool | None = None,
        content: str | None = None,
        lbl: str | None = None,
        lbl_height: float = 0,
        lbl_class: str | None = None,
        content_class: str | None = None,
    ) -> None:
        """Cell - can contain nested Layout or content.

        Args:
            width: Cell width (0 = elastic, expands to fill)
            border: Whether it has border (None = inherit from row)
            content: Text content
            lbl: Label above content
            lbl_height: Label height
            lbl_class: CSS class for label
            content_class: CSS class for content
        """

    @classmethod
    def compile(cls, bag: Bag) -> ComputedLayout:
        """Compile the Bag to ComputedLayout with resolved dimensions.

        Args:
            bag: Bag containing Layout/Row/Cell structure

        Returns:
            ComputedLayout with all coordinates and dimensions calculated
        """
        # Find root layout node
        layout_node = cls._find_layout_node(bag)
        if layout_node is None:
            msg = "No layout element found in Bag"
            raise ValueError(msg)

        return cls._compile_layout(
            layout_node,
            origin_x=0,
            origin_y=0,
            available_width=layout_node.attr.get("width", 210),
            available_height=layout_node.attr.get("height", 297),
        )

    @classmethod
    def _find_layout_node(cls, bag: Bag) -> BagNode | None:
        """Find the first layout node in the Bag."""
        node: BagNode
        for node in bag:
            if node.attr.get("tag") == "layout":
                return node
        return None

    @classmethod
    def _compile_layout(
        cls,
        node: BagNode,
        origin_x: float,
        origin_y: float,
        available_width: float,
        available_height: float,
    ) -> ComputedLayout:
        """Recursively compile a layout node."""
        attr = node.attr

        # Layout dimensions (use available if not specified)
        width = attr.get("width", 0) or available_width
        height = attr.get("height", 0) or available_height

        # Margins
        top = attr.get("top", 0)
        bottom = attr.get("bottom", 0)
        left = attr.get("left", 0)
        right = attr.get("right", 0)

        # Useful area
        useful_width = width - left - right
        useful_height = height - top - bottom

        # Collect row info
        row_nodes = [n for n in (node.value or []) if n.attr.get("tag") == "row"]

        fixed_height = sum(
            n.attr.get("height", 0) for n in row_nodes if n.attr.get("height", 0) > 0
        )
        elastic_rows = [n for n in row_nodes if n.attr.get("height", 0) == 0]
        elastic_height = (
            (useful_height - fixed_height) / len(elastic_rows) if elastic_rows else 0
        )

        # Compile each row
        computed_rows: list[ComputedRow] = []
        current_y = origin_y + top

        for row_node in row_nodes:
            row_height = row_node.attr.get("height", 0) or elastic_height

            computed_cells = cls._compile_row_cells(
                row_node,
                origin_x=origin_x + left,
                origin_y=current_y,
                available_width=useful_width,
                row_height=row_height,
                layout_border_width=attr.get("border_width", 0),
                layout_border_color=attr.get("border_color", "black"),
            )

            computed_rows.append(
                ComputedRow(
                    y=current_y,
                    computed_height=row_height,
                    cells=computed_cells,
                )
            )

            current_y += row_height

        return ComputedLayout(
            x=origin_x,
            y=origin_y,
            width=width,
            height=height,
            top=top,
            bottom=bottom,
            left=left,
            right=right,
            border_width=attr.get("border_width", 0),
            border_color=attr.get("border_color", "black"),
            rows=computed_rows,
        )

    @classmethod
    def _compile_row_cells(
        cls,
        row_node: BagNode,
        origin_x: float,
        origin_y: float,
        available_width: float,
        row_height: float,
        layout_border_width: float,
        layout_border_color: str,
    ) -> list[ComputedCell]:
        """Compile the cells of a row."""
        cell_nodes = [
            n for n in (row_node.value or []) if n.attr.get("tag") == "cell"
        ]

        fixed_width = sum(
            n.attr.get("width", 0) for n in cell_nodes if n.attr.get("width", 0) > 0
        )
        elastic_cells = [n for n in cell_nodes if n.attr.get("width", 0) == 0]
        elastic_width = (
            (available_width - fixed_width) / len(elastic_cells) if elastic_cells else 0
        )

        computed_cells: list[ComputedCell] = []
        current_x = origin_x

        for cell_node in cell_nodes:
            attr = cell_node.attr
            cell_width = attr.get("width", 0) or elastic_width

            # Border: inherit from row/layout if None
            cell_border = attr.get("border")
            if cell_border is None:
                row_border = row_node.attr.get("border")
                cell_border = row_border if row_border is not None else False

            border_width = layout_border_width if cell_border else 0

            # Nested layout?
            nested_layout = None
            nested_nodes = [
                n for n in (cell_node.value or []) if n.attr.get("tag") == "layout"
            ]
            if nested_nodes:
                nested_layout = cls._compile_layout(
                    nested_nodes[0],
                    origin_x=current_x,
                    origin_y=origin_y,
                    available_width=cell_width,
                    available_height=row_height,
                )

            computed_cells.append(
                ComputedCell(
                    x=current_x,
                    y=origin_y,
                    computed_width=cell_width,
                    computed_height=row_height,
                    border=cell_border,
                    border_width=border_width,
                    border_color=layout_border_color,
                    content=attr.get("content"),
                    nested_layout=nested_layout,
                    lbl=attr.get("lbl"),
                    lbl_height=attr.get("lbl_height", 0),
                    lbl_class=attr.get("lbl_class"),
                    content_class=attr.get("content_class"),
                )
            )

            current_x += cell_width

        return computed_cells
