# Copyright 2025 Softwell S.r.l. - Licensed under Apache License 2.0
# See LICENSE file for details

"""LRCResolver — elastic dimension calculation for Layout/Row/Cell model.

Pure function: takes resolved node attributes (with ^pointer values already
resolved by the compiler) and produces ComputedLayout dataclass hierarchy.

Algorithm extracted from the original layout compile logic.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from genro_print.computed import (
    CellElementType,
    ComputedCell,
    ComputedCellElement,
    ComputedLayout,
    ComputedRow,
)

if TYPE_CHECKING:
    from genro_bag import BagNode


class LRCResolver:
    """Resolves elastic dimensions for Layout/Row/Cell structures.

    Takes a built Bag node (layout) and produces a ComputedLayout
    with all coordinates and dimensions calculated.
    """

    def resolve(self, layout_node: BagNode,
                origin_x: float = 0, origin_y: float = 0,
                available_width: float = 210, available_height: float = 297) -> ComputedLayout:
        """Resolve a layout node into ComputedLayout.

        Args:
            layout_node: The layout BagNode from built Bag
            origin_x: X origin for this layout (for nested layouts)
            origin_y: Y origin for this layout (for nested layouts)
            available_width: Available width from parent container
            available_height: Available height from parent container

        Returns:
            ComputedLayout with resolved dimensions
        """
        attr = layout_node.attr

        width = attr.get("width", 0) or available_width
        height = attr.get("height", 0) or available_height

        top = attr.get("top", 0)
        bottom = attr.get("bottom", 0)
        left = attr.get("left", 0)
        right = attr.get("right", 0)

        useful_width = width - left - right
        useful_height = height - top - bottom

        row_nodes = [n for n in (layout_node.value or []) if n.node_tag == "row"]

        fixed_height = sum(
            n.attr.get("height", 0) for n in row_nodes if n.attr.get("height", 0) > 0
        )
        elastic_rows = [n for n in row_nodes if n.attr.get("height", 0) == 0]
        elastic_height = (
            (useful_height - fixed_height) / len(elastic_rows) if elastic_rows else 0
        )

        computed_rows: list[ComputedRow] = []
        current_y = origin_y + top

        for row_node in row_nodes:
            row_height = row_node.attr.get("height", 0) or elastic_height

            computed_cells = self._resolve_row_cells(
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

    def _resolve_row_cells(
        self,
        row_node: BagNode,
        origin_x: float,
        origin_y: float,
        available_width: float,
        row_height: float,
        layout_border_width: float,
        layout_border_color: str,
    ) -> list[ComputedCell]:
        """Resolve cells of a row."""
        cell_nodes = [n for n in (row_node.value or []) if n.node_tag == "cell"]

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

            cell_border = attr.get("border")
            if cell_border is None:
                row_border = row_node.attr.get("border")
                cell_border = row_border if row_border is not None else False

            border_width = layout_border_width if cell_border else 0

            nested_layout = None
            nested_nodes = [n for n in (cell_node.value or []) if n.node_tag == "layout"]
            if nested_nodes:
                nested_layout = self.resolve(
                    nested_nodes[0],
                    origin_x=current_x,
                    origin_y=origin_y,
                    available_width=cell_width,
                    available_height=row_height,
                )

            elements = self._resolve_cell_elements(cell_node)

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
                    elements=elements,
                    lbl=attr.get("lbl"),
                    lbl_height=attr.get("lbl_height", 0),
                    lbl_class=attr.get("lbl_class"),
                    content_class=attr.get("content_class"),
                )
            )
            current_x += cell_width

        return computed_cells

    def _resolve_cell_elements(self, cell_node: BagNode) -> list[ComputedCellElement]:
        """Resolve child elements of a cell (image, paragraph, spacer)."""
        elements: list[ComputedCellElement] = []

        for child in cell_node.value or []:
            tag = child.node_tag
            if tag == "layout":
                continue

            if tag == "image":
                elements.append(ComputedCellElement(
                    element_type=CellElementType.IMAGE,
                    attrs={
                        "src": child.attr.get("src", ""),
                        "width": child.attr.get("width", 0),
                        "height": child.attr.get("height", 0),
                        "align": child.attr.get("align", "left"),
                        "valign": child.attr.get("valign", "top"),
                    },
                ))
            elif tag == "paragraph":
                elements.append(ComputedCellElement(
                    element_type=CellElementType.PARAGRAPH,
                    attrs={
                        "content": child.attr.get("content", ""),
                        "style": child.attr.get("style", "Normal"),
                        "font_name": child.attr.get("font_name", "Helvetica"),
                        "font_size": child.attr.get("font_size", 10),
                        "color": child.attr.get("color", "black"),
                        "align": child.attr.get("align", "left"),
                    },
                ))
            elif tag == "spacer":
                elements.append(ComputedCellElement(
                    element_type=CellElementType.SPACER,
                    attrs={"height": child.attr.get("height", 5)},
                ))

        return elements
