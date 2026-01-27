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

from genro_print.computed import (
    CellElementType,
    ComputedCell,
    ComputedCellElement,
    ComputedLayout,
    ComputedRow,
)

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
        computed = doc.builder.compile(doc)
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
        ...

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
        ...

    @element(sub_tags="layout,image,paragraph,spacer")
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
        """Cell - can contain nested Layout, content elements, or simple text.

        Args:
            width: Cell width (0 = elastic, expands to fill)
            border: Whether it has border (None = inherit from row)
            content: Text content (simple text, for backward compatibility)
            lbl: Label above content
            lbl_height: Label height
            lbl_class: CSS class for label
            content_class: CSS class for content
        """
        ...

    @element()
    def image(
        self,
        src: str = "",
        width: float = 0,
        height: float = 0,
        align: str = "left",
        valign: str = "top",
    ) -> None:
        """Image element inside a cell.

        Args:
            src: Path to image file
            width: Image width in mm (0 = auto from aspect ratio)
            height: Image height in mm (0 = auto from aspect ratio)
            align: Horizontal alignment (left, center, right)
            valign: Vertical alignment (top, middle, bottom)
        """
        ...

    @element()
    def paragraph(
        self,
        content: str = "",
        style: str = "Normal",
        font_name: str = "Helvetica",
        font_size: float = 10,
        color: str = "black",
        align: str = "left",
    ) -> None:
        """Paragraph element inside a cell.

        Args:
            content: Text content
            style: Paragraph style name
            font_name: Font name
            font_size: Font size in points
            color: Text color
            align: Text alignment (left, center, right, justify)
        """
        ...

    @element()
    def spacer(
        self,
        height: float = 5,
    ) -> None:
        """Vertical spacer inside a cell.

        Args:
            height: Spacer height in mm
        """
        ...

    def compile(self, bag: Bag) -> ComputedLayout:
        """Compile the Bag to ComputedLayout with resolved dimensions.

        Args:
            bag: Bag containing Layout/Row/Cell structure

        Returns:
            ComputedLayout with all coordinates and dimensions calculated
        """
        # Find root layout node
        layout_node = self._find_layout_node(bag)
        if layout_node is None:
            msg = "No layout element found in Bag"
            raise ValueError(msg)

        return self._compile_layout(
            layout_node,
            origin_x=0,
            origin_y=0,
            available_width=layout_node.attr.get("width", 210),
            available_height=layout_node.attr.get("height", 297),
        )

    def _find_layout_node(self, bag: Bag) -> BagNode | None:
        """Find the first layout node in the Bag."""
        node: BagNode
        for node in bag:
            if node.tag == "layout":
                return node
        return None

    def _compile_layout(
        self,
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
        row_nodes = [n for n in (node.value or []) if n.tag == "row"]

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

            computed_cells = self._compile_row_cells(
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

    def _compile_row_cells(
        self,
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
            n for n in (row_node.value or []) if n.tag == "cell"
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
                n for n in (cell_node.value or []) if n.tag == "layout"
            ]
            if nested_nodes:
                nested_layout = self._compile_layout(
                    nested_nodes[0],
                    origin_x=current_x,
                    origin_y=origin_y,
                    available_width=cell_width,
                    available_height=row_height,
                )

            # Compile cell elements (image, paragraph, spacer)
            elements = self._compile_cell_elements(cell_node)

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

    def _compile_cell_elements(self, cell_node: BagNode) -> list[ComputedCellElement]:
        """Compile child elements of a cell (image, paragraph, spacer)."""
        elements: list[ComputedCellElement] = []

        for child in cell_node.value or []:
            tag = child.tag
            if tag == "layout":
                continue  # handled separately as nested_layout

            if tag == "image":
                elements.append(
                    ComputedCellElement(
                        element_type=CellElementType.IMAGE,
                        attrs={
                            "src": child.attr.get("src", ""),
                            "width": child.attr.get("width", 0),
                            "height": child.attr.get("height", 0),
                            "align": child.attr.get("align", "left"),
                            "valign": child.attr.get("valign", "top"),
                        },
                    )
                )
            elif tag == "paragraph":
                elements.append(
                    ComputedCellElement(
                        element_type=CellElementType.PARAGRAPH,
                        attrs={
                            "content": child.attr.get("content", ""),
                            "style": child.attr.get("style", "Normal"),
                            "font_name": child.attr.get("font_name", "Helvetica"),
                            "font_size": child.attr.get("font_size", 10),
                            "color": child.attr.get("color", "black"),
                            "align": child.attr.get("align", "left"),
                        },
                    )
                )
            elif tag == "spacer":
                elements.append(
                    ComputedCellElement(
                        element_type=CellElementType.SPACER,
                        attrs={
                            "height": child.attr.get("height", 5),
                        },
                    )
                )

        return elements
