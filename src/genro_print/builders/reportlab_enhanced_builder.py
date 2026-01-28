# Copyright 2025 Softwell S.r.l. - Licensed under Apache License 2.0
# See LICENSE file for details

"""
ReportLabEnhancedBuilder - Declarative builder for ReportLab PDF generation.

Purely declarative API with inherited styles via styledblock containers.
No state-setting elements (setfont, setfillcolor, etc.).

Key elements:
- styledblock: Container with inheritable style attributes
- statictext: Positioned text with inherited style
- styledline: Line with stroke style
- styledrect: Rectangle with fill and stroke style
- styledcircle: Circle with fill and stroke style

Style inheritance uses genro-bag's inherited attributes mechanism.
"""

from __future__ import annotations

import inspect
from io import BytesIO
from typing import TYPE_CHECKING, Any

from genro_bag import Bag
from genro_bag.builder import BagBuilderBase, element
from genro_bag.builders import component

try:
    from reportlab.graphics import renderPDF
    from reportlab.graphics.barcode import qr
    from reportlab.graphics.charts.barcharts import VerticalBarChart
    from reportlab.graphics.charts.lineplots import LinePlot
    from reportlab.graphics.charts.piecharts import Pie
    from reportlab.graphics.shapes import Drawing
    from reportlab.lib.colors import HexColor, toColor
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas
    from reportlab.platypus import (
        Image,
        PageBreak,
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
    )

    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    mm = 1  # fallback for type checking

if TYPE_CHECKING:
    from genro_bag.bagnode import BagNode


# Style attribute names that can be inherited
STYLE_ATTRS = frozenset({
    "fontname",
    "size",
    "color",
    "fill_color",
    "stroke_color",
    "stroke_width",
})


class ComputedEnhancedReportLab:
    """Intermediate structure produced by compile()."""

    def __init__(
        self,
        elements: list[dict[str, Any]],
        page_width: float = 210,
        page_height: float = 297,
        margins: tuple[float, float, float, float] = (10, 10, 10, 10),
    ) -> None:
        self.elements = elements
        self.page_width = page_width
        self.page_height = page_height
        self.margins = margins


class ReportLabEnhancedBuilder(BagBuilderBase):
    """Declarative builder for ReportLab with inherited styles.

    Example:
        doc = root.document(width=210, height=297)
        b = doc.styledblock(fontname="Helvetica-Bold", size=14, color="red")
        b.statictext(x=20, y=50, text="Title 1")
        b.statictext(x=20, y=70, text="Title 2")
    """

    def __init__(self, bag: Bag) -> None:
        if not REPORTLAB_AVAILABLE:
            msg = "ReportLab required: pip install reportlab"
            raise ImportError(msg)
        super().__init__(bag)

    # -------------------------------------------------------------------------
    # Document element (root)
    # -------------------------------------------------------------------------

    @element(sub_tags="*")
    def document(
        self,
        width: float = 210.0,
        height: float = 297.0,
        left_margin: float = 10.0,
        right_margin: float = 10.0,
        top_margin: float = 10.0,
        bottom_margin: float = 10.0,
        title: str | None = None,
        author: str | None = None,
    ) -> None:
        """Document root element with page size and margins."""
        ...

    # -------------------------------------------------------------------------
    # Styled block container (inheritable styles)
    # -------------------------------------------------------------------------

    @element(sub_tags="*", compile_type="container")
    def styledblock(
        self,
        fontname: str | None = None,
        size: float | None = None,
        color: str | None = None,
        fill_color: str | None = None,
        stroke_color: str | None = None,
        stroke_width: float | None = None,
    ) -> None:
        """Container with inheritable style attributes.

        Child elements inherit these styles. Nested styledblocks can override.

        Args:
            fontname: Font name (e.g., "Helvetica", "Helvetica-Bold")
            size: Font size in points
            color: Text color (hex or name)
            fill_color: Fill color for shapes
            stroke_color: Stroke color for shapes and lines
            stroke_width: Stroke width in points
        """
        ...

    # -------------------------------------------------------------------------
    # Declarative canvas elements
    # -------------------------------------------------------------------------

    @element(sub_tags="", compile_type="styled_canvas")
    def statictext(
        self,
        x: float = 0.0,
        y: float = 0.0,
        text: str = "",
        align: str = "left",
        fontname: str | None = None,
        size: float | None = None,
        color: str | None = None,
    ) -> None:
        """Positioned text with style (inherited or direct).

        Args:
            x: X position in mm
            y: Y position in mm (from top)
            text: Text content
            align: Alignment (left, center, right)
            fontname: Font name (overrides inherited)
            size: Font size in points (overrides inherited)
            color: Text color (overrides inherited)
        """
        ...

    @element(sub_tags="", compile_type="styled_canvas")
    def styledline(
        self,
        x1: float = 0.0,
        y1: float = 0.0,
        x2: float = 10.0,
        y2: float = 10.0,
        stroke_color: str | None = None,
        stroke_width: float | None = None,
    ) -> None:
        """Line with style (inherited or direct).

        Args:
            x1, y1: Start position in mm
            x2, y2: End position in mm
            stroke_color: Line color (overrides inherited)
            stroke_width: Line width in points (overrides inherited)
        """
        ...

    @element(sub_tags="", compile_type="styled_canvas")
    def styledrect(
        self,
        x: float = 0.0,
        y: float = 0.0,
        width: float = 10.0,
        height: float = 10.0,
        radius: float = 0.0,
        fill_color: str | None = None,
        stroke_color: str | None = None,
        stroke_width: float | None = None,
    ) -> None:
        """Rectangle with style (inherited or direct).

        Args:
            x, y: Position in mm
            width, height: Dimensions in mm
            radius: Corner radius (0 for sharp corners)
            fill_color: Fill color (overrides inherited)
            stroke_color: Stroke color (overrides inherited)
            stroke_width: Stroke width in points (overrides inherited)
        """
        ...

    @element(sub_tags="", compile_type="styled_canvas")
    def styledcircle(
        self,
        x_cen: float = 0.0,
        y_cen: float = 0.0,
        radius: float = 5.0,
        fill_color: str | None = None,
        stroke_color: str | None = None,
        stroke_width: float | None = None,
    ) -> None:
        """Circle with style (inherited or direct).

        Args:
            x_cen, y_cen: Center position in mm
            radius: Radius in mm
            fill_color: Fill color (overrides inherited)
            stroke_color: Stroke color (overrides inherited)
            stroke_width: Stroke width in points (overrides inherited)
        """
        ...

    @element(sub_tags="", compile_type="styled_canvas")
    def styledellipse(
        self,
        x1: float = 0.0,
        y1: float = 0.0,
        x2: float = 10.0,
        y2: float = 5.0,
        fill_color: str | None = None,
        stroke_color: str | None = None,
        stroke_width: float | None = None,
    ) -> None:
        """Ellipse with style (inherited or direct).

        Args:
            x1, y1: Top-left corner in mm
            x2, y2: Bottom-right corner in mm
            fill_color: Fill color (overrides inherited)
            stroke_color: Stroke color (overrides inherited)
            stroke_width: Stroke width in points (overrides inherited)
        """
        ...

    @element(sub_tags="", compile_type="styled_canvas")
    def styledimage(
        self,
        image: str = "",
        x: float = 0.0,
        y: float = 0.0,
        width: float | None = None,
        height: float | None = None,
        mask: str | None = None,
        preserve_aspect_ratio: bool = False,
    ) -> None:
        """Image at position.

        Args:
            image: Path to image file
            x, y: Position in mm
            width, height: Optional dimensions in mm
            mask: Optional mask
            preserve_aspect_ratio: Preserve aspect ratio
        """
        ...

    # -------------------------------------------------------------------------
    # Components (composite elements)
    # -------------------------------------------------------------------------

    @component(sub_tags="")
    def labeledtext(
        self,
        comp: Bag,
        x: float = 0.0,
        y: float = 0.0,
        label: str = "",
        value: str = "",
        label_width: float | None = None,
        label_bold: bool = True,
        separator: str = " ",
        border_bottom: bool = False,
        **kwargs: Any,
    ) -> Bag:
        """Component: labeled text field (label + value).

        Args:
            comp: Component Bag (provided by decorator)
            x: X position in mm
            y: Y position in mm
            label: Label text
            value: Value text
            label_width: Fixed label width (None = auto)
            label_bold: Whether label is bold
            separator: Separator between label and value
            border_bottom: Draw underline
        """
        # Get inherited style
        fontname = kwargs.get("fontname", "Helvetica")
        size = kwargs.get("size", 11.0)
        color = kwargs.get("color", "black")

        # Label font
        label_fontname = "Helvetica-Bold" if label_bold else fontname

        # Add label
        comp.statictext(x=x, y=y, text=label + separator, fontname=label_fontname,
                        size=size, color=color)

        # Calculate value position (approximate if no label_width)
        # In real impl, would measure string width
        value_x = x + (label_width if label_width else len(label) * size * 0.6)

        # Add value
        comp.statictext(x=value_x, y=y, text=value, fontname=fontname,
                        size=size, color=color)

        # Border bottom
        if border_bottom:
            line_y = y + size * 0.4  # Below text baseline
            total_width = value_x + len(value) * size * 0.6 - x
            comp.styledline(x1=x, y1=line_y, x2=x + total_width, y2=line_y,
                            stroke_color=kwargs.get("border_color", "gray"),
                            stroke_width=kwargs.get("border_width", 0.5))

        return comp

    # -------------------------------------------------------------------------
    # Platypus elements (unchanged from base builder)
    # -------------------------------------------------------------------------

    @element(sub_tags="", compile_type="platypus", compile_class="Paragraph")
    def paragraph(
        self,
        content: str = "",
        style: str = "Normal",
        bullet_text: str | None = None,
    ) -> None:
        """A paragraph of text (Platypus flowable)."""
        ...

    @element(sub_tags="", compile_type="platypus", compile_class="Spacer")
    def spacer(
        self,
        width: float = 0.0,
        height: float = 10.0,
    ) -> None:
        """Vertical space between elements."""
        ...

    @element(sub_tags="", compile_type="platypus", compile_class="PageBreak")
    def pagebreak(self) -> None:
        """Force a page break."""
        ...

    @element(sub_tags="", compile_type="platypus", compile_class="Image")
    def image(
        self,
        src: str = "",
        width: float | None = None,
        height: float | None = None,
        kind: str = "direct",
        mask: str | None = None,
        lazy: int = 1,
    ) -> None:
        """An image flowable."""
        ...

    @element(sub_tags="row", compile_type="platypus", compile_class="Table")
    def table(
        self,
        col_widths: list[float] | None = None,
        row_heights: list[float] | None = None,
        repeat_rows: int = 0,
        repeat_cols: int = 0,
        split_by_row: int = 1,
        h_align: str = "CENTER",
    ) -> None:
        """A table flowable."""
        ...

    @element(sub_tags="cell", parent_tags="table")
    def row(self) -> None:
        """A table row. Contains cell elements."""
        ...

    @element(sub_tags="", parent_tags="row")
    def cell(
        self,
        content: str = "",
        colspan: int = 1,
        rowspan: int = 1,
        align: str | None = None,
        valign: str | None = None,
        background: str | None = None,
    ) -> None:
        """A table cell."""
        ...

    # -------------------------------------------------------------------------
    # Graphics elements (unchanged from base builder)
    # -------------------------------------------------------------------------

    @element(sub_tags="", compile_type="graphics")
    def bar_chart(
        self,
        data: list[list[float]] | None = None,
        categories: list[str] | None = None,
        x: float = 0.0,
        y: float = 0.0,
        width: float = 100.0,
        height: float = 80.0,
        colors: list[str] | None = None,
        bar_width: float = 10.0,
        group_spacing: float = 5.0,
    ) -> None:
        """A vertical bar chart."""
        ...

    @element(sub_tags="", compile_type="graphics")
    def pie_chart(
        self,
        data: list[float] | None = None,
        labels: list[str] | None = None,
        x: float = 0.0,
        y: float = 0.0,
        width: float = 100.0,
        height: float = 100.0,
        colors: list[str] | None = None,
        start_angle: float = 90.0,
    ) -> None:
        """A pie chart."""
        ...

    @element(sub_tags="", compile_type="graphics")
    def line_chart(
        self,
        data: list[list[tuple[float, float]]] | None = None,
        x: float = 0.0,
        y: float = 0.0,
        width: float = 100.0,
        height: float = 80.0,
        colors: list[str] | None = None,
        stroke_width: float = 1.0,
    ) -> None:
        """A line chart (line plot)."""
        ...

    @element(sub_tags="", compile_type="graphics")
    def qrcode(
        self,
        value: str = "",
        x: float = 0.0,
        y: float = 0.0,
        size: float = 40.0,
        bar_width: float = 1.0,
        bar_height: float = 1.0,
    ) -> None:
        """A QR code."""
        ...

    # -------------------------------------------------------------------------
    # Compile: transform Bag to ComputedEnhancedReportLab
    # -------------------------------------------------------------------------

    def compile(self, bag: Bag) -> ComputedEnhancedReportLab:
        """Compile a Bag to ComputedEnhancedReportLab structure."""
        elements: list[dict[str, Any]] = []
        page_width = 210.0
        page_height = 297.0
        margins = (10.0, 10.0, 10.0, 10.0)

        for node in bag:
            tag = node.tag or ""

            if tag == "document":
                page_width = node.attr.get("width", 210.0)
                page_height = node.attr.get("height", 297.0)
                margins = (
                    node.attr.get("left_margin", 10.0),
                    node.attr.get("right_margin", 10.0),
                    node.attr.get("top_margin", 10.0),
                    node.attr.get("bottom_margin", 10.0),
                )
                if isinstance(node.value, Bag):
                    inherited = self._get_style_attrs(node.attr)
                    self._compile_children(node.value, elements, inherited)
            else:
                compiled = self._compile_node(node, {})
                if compiled:
                    elements.append(compiled)

        return ComputedEnhancedReportLab(
            elements=elements,
            page_width=page_width,
            page_height=page_height,
            margins=margins,
        )

    def _get_style_attrs(self, attr: dict[str, Any]) -> dict[str, Any]:
        """Extract style attributes from node attributes."""
        return {k: v for k, v in attr.items() if k in STYLE_ATTRS and v is not None}

    def _merge_inherited(
        self, inherited: dict[str, Any], node_attr: dict[str, Any]
    ) -> dict[str, Any]:
        """Merge inherited styles with node's own styles."""
        result = dict(inherited)
        result.update(self._get_style_attrs(node_attr))
        return result

    def _compile_children(
        self,
        bag: Bag,
        elements: list[dict[str, Any]],
        inherited: dict[str, Any],
    ) -> None:
        """Compile children with inherited styles."""
        for node in bag:
            compiled = self._compile_node(node, inherited)
            if compiled:
                elements.append(compiled)

    def _compile_node(
        self, node: BagNode, inherited: dict[str, Any]
    ) -> dict[str, Any] | None:
        """Compile a single node with inherited styles."""
        tag = node.tag or ""
        if not tag:
            return None

        # Get schema info
        schema_info = self.get_schema_info(tag)
        compile_kwargs = schema_info.get("compile_kwargs", {})
        compile_type = compile_kwargs.get("type")

        # Get node attributes
        attr = {k: v for k, v in node.attr.items() if not k.startswith("_")}

        # Handle styledblock as container
        if tag == "styledblock":
            merged = self._merge_inherited(inherited, attr)
            children: list[dict[str, Any]] = []
            if isinstance(node.value, Bag):
                self._compile_children(node.value, children, merged)
            return {
                "tag": tag,
                "type": "container",
                "attr": attr,
                "style": merged,
                "children": children,
            }

        # Handle table specially
        if tag == "table":
            return self._compile_table(node)

        # Get content from node value if present
        content = ""
        if node.value and not isinstance(node.value, Bag):
            content = str(node.value)
        if not attr.get("content") and content:
            attr["content"] = content

        # Merge inherited styles for styled_canvas elements
        resolved_style = dict(inherited)
        if compile_type == "styled_canvas":
            resolved_style.update(self._get_style_attrs(attr))

        return {
            "tag": tag,
            "type": compile_type or "platypus",
            "class": compile_kwargs.get("class"),
            "method": compile_kwargs.get("method"),
            "attr": attr,
            "style": resolved_style,
            "children": [],
        }

    def _compile_table(self, node: BagNode) -> dict[str, Any]:
        """Compile table with rows and cells."""
        attr = {k: v for k, v in node.attr.items() if not k.startswith("_")}

        rows_data: list[list[str]] = []
        if isinstance(node.value, Bag):
            for row_node in node.value:
                if row_node.tag == "row":
                    row_cells: list[str] = []
                    if isinstance(row_node.value, Bag):
                        for cell_node in row_node.value:
                            if cell_node.tag == "cell":
                                cell_content = cell_node.attr.get("content", "")
                                if not cell_content and cell_node.value:
                                    cell_content = str(cell_node.value)
                                row_cells.append(cell_content)
                    rows_data.append(row_cells)

        return {
            "tag": "table",
            "type": "platypus",
            "class": "Table",
            "method": None,
            "attr": attr,
            "style": {},
            "data": rows_data,
            "children": [],
        }

    # -------------------------------------------------------------------------
    # Render: transform ComputedEnhancedReportLab to PDF
    # -------------------------------------------------------------------------

    def render(self, computed: ComputedEnhancedReportLab) -> bytes:
        """Render ComputedEnhancedReportLab to PDF bytes."""
        if not REPORTLAB_AVAILABLE:
            msg = "ReportLab required: pip install reportlab"
            raise ImportError(msg)

        # Check what types of elements we have
        all_elements = self._flatten_elements(computed.elements)
        has_styled_canvas = any(e.get("type") == "styled_canvas" for e in all_elements)
        has_graphics = any(e.get("type") == "graphics" for e in all_elements)
        has_platypus = any(e.get("type") == "platypus" for e in all_elements)

        if has_styled_canvas or has_graphics:
            return self._render_canvas(computed)
        if has_platypus:
            return self._render_platypus(computed)
        # Default to canvas for empty documents
        return self._render_canvas(computed)

    def _flatten_elements(
        self, elements: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Flatten nested elements for type checking."""
        result: list[dict[str, Any]] = []
        for elem in elements:
            if elem.get("type") == "container":
                result.extend(self._flatten_elements(elem.get("children", [])))
            else:
                result.append(elem)
        return result

    def _render_platypus(self, computed: ComputedEnhancedReportLab) -> bytes:
        """Render using Platypus (flowables)."""
        buffer = BytesIO()

        left, right, top, bottom = computed.margins
        doc = SimpleDocTemplate(
            buffer,
            pagesize=(computed.page_width * mm, computed.page_height * mm),
            leftMargin=left * mm,
            rightMargin=right * mm,
            topMargin=top * mm,
            bottomMargin=bottom * mm,
        )

        styles = getSampleStyleSheet()
        flowables: list[Any] = []

        self._collect_flowables(computed.elements, flowables, styles)

        doc.build(flowables)
        buffer.seek(0)
        return buffer.read()

    def _collect_flowables(
        self,
        elements: list[dict[str, Any]],
        flowables: list[Any],
        styles: Any,
    ) -> None:
        """Recursively collect flowables from elements."""
        for elem in elements:
            if elem.get("type") == "container":
                self._collect_flowables(elem.get("children", []), flowables, styles)
            else:
                flowable = self._create_flowable(elem, styles)
                if flowable:
                    flowables.append(flowable)

    def _create_flowable(self, elem: dict[str, Any], styles: Any) -> Any:
        """Create a Platypus flowable from element dict."""
        tag = elem.get("tag", "")
        attr = elem.get("attr", {})

        factory = getattr(self, f"_create_{tag}_flowable", None)
        if factory:
            return factory(elem, attr, styles)
        return None

    def _create_paragraph_flowable(
        self,
        elem: dict[str, Any],  # noqa: ARG002
        attr: dict[str, Any],
        styles: Any,
    ) -> Any:
        """Create a Paragraph flowable."""
        content = attr.get("content", "")
        style_name = attr.get("style", "Normal")
        style = styles.get(style_name, styles["Normal"])
        return Paragraph(content, style)

    def _create_spacer_flowable(
        self,
        elem: dict[str, Any],  # noqa: ARG002
        attr: dict[str, Any],
        styles: Any,  # noqa: ARG002
    ) -> Any:
        """Create a Spacer flowable."""
        width = attr.get("width", 0) * mm
        height = attr.get("height", 10) * mm
        return Spacer(width, height)

    def _create_pagebreak_flowable(
        self,
        elem: dict[str, Any],  # noqa: ARG002
        attr: dict[str, Any],  # noqa: ARG002
        styles: Any,  # noqa: ARG002
    ) -> Any:
        """Create a PageBreak flowable."""
        return PageBreak()

    def _create_image_flowable(
        self,
        elem: dict[str, Any],  # noqa: ARG002
        attr: dict[str, Any],
        styles: Any,  # noqa: ARG002
    ) -> Any:
        """Create an Image flowable."""
        src = attr.get("src", "")
        width = attr.get("width")
        height = attr.get("height")
        if width:
            width = width * mm
        if height:
            height = height * mm
        return Image(src, width=width, height=height)

    def _create_table_flowable(
        self,
        elem: dict[str, Any],
        attr: dict[str, Any],
        styles: Any,  # noqa: ARG002
    ) -> Any:
        """Create a Table flowable."""
        data = elem.get("data", [])
        if not data:
            return None
        col_widths = attr.get("col_widths")
        if col_widths:
            col_widths = [w * mm for w in col_widths]
        return Table(data, colWidths=col_widths)

    def _render_canvas(self, computed: ComputedEnhancedReportLab) -> bytes:
        """Render using Canvas with styled elements."""
        buffer = BytesIO()

        c = canvas.Canvas(
            buffer,
            pagesize=(computed.page_width * mm, computed.page_height * mm),
        )

        page_height = computed.page_height

        self._render_elements(c, computed.elements, page_height)

        c.save()
        buffer.seek(0)
        return buffer.read()

    def _render_elements(
        self,
        c: Any,
        elements: list[dict[str, Any]],
        page_height: float,
    ) -> None:
        """Recursively render elements."""
        for elem in elements:
            elem_type = elem.get("type")

            if elem_type == "container":
                # Render children of container
                self._render_elements(c, elem.get("children", []), page_height)
            elif elem_type == "styled_canvas":
                self._draw_styled_element(c, elem, page_height)
            elif elem_type == "graphics":
                self._draw_graphics_element(c, elem, page_height)

    def _draw_styled_element(
        self, c: Any, elem: dict[str, Any], page_height: float
    ) -> None:
        """Draw a styled canvas element with inherited styles."""
        tag = elem.get("tag", "")
        attr = elem.get("attr", {})
        style = elem.get("style", {})

        draw_method = getattr(self, f"_draw_{tag}", None)
        if draw_method:
            draw_method(c, attr, style, page_height)

    def _apply_text_style(self, c: Any, style: dict[str, Any]) -> None:
        """Apply text style to canvas."""
        fontname = style.get("fontname", "Helvetica")
        size = style.get("size", 12.0)
        color = style.get("color", "black")

        c.setFont(fontname, size)
        c.setFillColor(self._parse_color(color))

    def _apply_shape_style(self, c: Any, style: dict[str, Any]) -> None:
        """Apply shape style to canvas."""
        stroke_color = style.get("stroke_color", "black")
        stroke_width = style.get("stroke_width", 1.0)
        fill_color = style.get("fill_color")

        c.setStrokeColor(self._parse_color(stroke_color))
        c.setLineWidth(stroke_width)
        if fill_color:
            c.setFillColor(self._parse_color(fill_color))

    def _draw_statictext(
        self,
        c: Any,
        attr: dict[str, Any],
        style: dict[str, Any],
        page_height: float,
    ) -> None:
        """Draw statictext element."""
        x = attr.get("x", 0) * mm
        y = (page_height - attr.get("y", 0)) * mm
        text = attr.get("text", "")
        align = attr.get("align", "left")

        self._apply_text_style(c, style)

        if align == "center":
            c.drawCentredString(x, y, text)
        elif align == "right":
            c.drawRightString(x, y, text)
        else:
            c.drawString(x, y, text)

    def _draw_styledline(
        self,
        c: Any,
        attr: dict[str, Any],
        style: dict[str, Any],
        page_height: float,
    ) -> None:
        """Draw styledline element."""
        x1 = attr.get("x1", 0) * mm
        y1 = (page_height - attr.get("y1", 0)) * mm
        x2 = attr.get("x2", 10) * mm
        y2 = (page_height - attr.get("y2", 10)) * mm

        # Use stroke_color for line color if not overridden
        line_style = dict(style)
        if "color" in style and "stroke_color" not in style:
            line_style["stroke_color"] = style["color"]

        self._apply_shape_style(c, line_style)
        c.line(x1, y1, x2, y2)

    def _draw_styledrect(
        self,
        c: Any,
        attr: dict[str, Any],
        style: dict[str, Any],
        page_height: float,
    ) -> None:
        """Draw styledrect element."""
        x = attr.get("x", 0) * mm
        y_top = attr.get("y", 0)
        width = attr.get("width", 10) * mm
        height = attr.get("height", 10) * mm
        radius = attr.get("radius", 0) * mm

        # Convert Y coordinate (top-left to bottom-left)
        y = (page_height - y_top) * mm - height

        self._apply_shape_style(c, style)

        fill = 1 if style.get("fill_color") else 0
        stroke = 1

        if radius > 0:
            c.roundRect(x, y, width, height, radius, stroke=stroke, fill=fill)
        else:
            c.rect(x, y, width, height, stroke=stroke, fill=fill)

    def _draw_styledcircle(
        self,
        c: Any,
        attr: dict[str, Any],
        style: dict[str, Any],
        page_height: float,
    ) -> None:
        """Draw styledcircle element."""
        x_cen = attr.get("x_cen", 0) * mm
        y_cen = (page_height - attr.get("y_cen", 0)) * mm
        radius = attr.get("radius", 5) * mm

        self._apply_shape_style(c, style)

        fill = 1 if style.get("fill_color") else 0
        c.circle(x_cen, y_cen, radius, stroke=1, fill=fill)

    def _draw_styledellipse(
        self,
        c: Any,
        attr: dict[str, Any],
        style: dict[str, Any],
        page_height: float,
    ) -> None:
        """Draw styledellipse element."""
        x1 = attr.get("x1", 0) * mm
        y1 = (page_height - attr.get("y1", 0)) * mm
        x2 = attr.get("x2", 10) * mm
        y2 = (page_height - attr.get("y2", 5)) * mm

        self._apply_shape_style(c, style)

        fill = 1 if style.get("fill_color") else 0
        c.ellipse(x1, y1, x2, y2, stroke=1, fill=fill)

    def _draw_styledimage(
        self,
        c: Any,
        attr: dict[str, Any],
        style: dict[str, Any],  # noqa: ARG002
        page_height: float,
    ) -> None:
        """Draw styledimage element."""
        image_path = attr.get("image", "")
        if not image_path:
            return

        x = attr.get("x", 0) * mm
        y_top = attr.get("y", 0)
        width = attr.get("width")
        height = attr.get("height")
        mask = attr.get("mask")
        preserve = attr.get("preserve_aspect_ratio", False)

        if width:
            width = width * mm
        if height:
            height = height * mm

        # Convert Y coordinate
        y = (page_height - y_top) * mm - height if height else (page_height - y_top) * mm

        c.drawImage(
            image_path,
            x,
            y,
            width=width,
            height=height,
            mask=mask,
            preserveAspectRatio=preserve,
        )

    # -------------------------------------------------------------------------
    # Graphics elements rendering (same as base builder)
    # -------------------------------------------------------------------------

    def _draw_graphics_element(
        self, c: Any, elem: dict[str, Any], page_height: float
    ) -> None:
        """Draw a graphics element (charts, etc.)."""
        tag = elem.get("tag", "")
        attr = elem.get("attr", {})

        draw_method = getattr(self, f"_draw_{tag}", None)
        if draw_method:
            # Graphics methods don't use style parameter
            sig = inspect.signature(draw_method)
            expected_params = 4
            if len(sig.parameters) == expected_params:
                draw_method(c, attr, {}, page_height)
            else:
                draw_method(c, attr, page_height)

    def _parse_color(self, color: str) -> Any:
        """Parse color string to ReportLab color."""
        if color.startswith("#"):
            return HexColor(color)
        return toColor(color)

    def _draw_bar_chart(
        self, c: Any, attr: dict[str, Any], page_height: float
    ) -> None:
        """Draw a vertical bar chart."""
        data = attr.get("data") or [[10, 20, 30, 40]]
        categories = attr.get("categories")
        x = attr.get("x", 0) * mm
        y_top = attr.get("y", 0)
        width = attr.get("width", 100) * mm
        height = attr.get("height", 80) * mm
        colors = attr.get("colors")
        bar_width = attr.get("bar_width", 10)
        group_spacing = attr.get("group_spacing", 5)

        drawing = Drawing(width, height)

        chart = VerticalBarChart()
        chart.x = 30
        chart.y = 20
        chart.width = width - 50
        chart.height = height - 40
        chart.data = data
        chart.barWidth = bar_width
        chart.groupSpacing = group_spacing

        if categories:
            chart.categoryAxis.categoryNames = categories

        if colors:
            for i, color in enumerate(colors):
                if i < len(chart.bars):
                    chart.bars[i].fillColor = self._parse_color(color)

        drawing.add(chart)

        y_pt = (page_height - y_top) * mm - height
        renderPDF.draw(drawing, c, x, y_pt)

    def _draw_pie_chart(
        self, c: Any, attr: dict[str, Any], page_height: float
    ) -> None:
        """Draw a pie chart."""
        data = attr.get("data") or [10, 20, 30, 40]
        labels = attr.get("labels")
        x = attr.get("x", 0) * mm
        y_top = attr.get("y", 0)
        width = attr.get("width", 100) * mm
        height = attr.get("height", 100) * mm
        colors = attr.get("colors")
        start_angle = attr.get("start_angle", 90)

        drawing = Drawing(width, height)

        pie = Pie()
        pie.x = 10
        pie.y = 10
        pie.width = width - 20
        pie.height = height - 20
        pie.data = data
        pie.startAngle = start_angle

        if labels:
            pie.labels = labels

        if colors:
            for i, color in enumerate(colors):
                if i < len(pie.slices):
                    pie.slices[i].fillColor = self._parse_color(color)

        drawing.add(pie)

        y_pt = (page_height - y_top) * mm - height
        renderPDF.draw(drawing, c, x, y_pt)

    def _draw_line_chart(
        self, c: Any, attr: dict[str, Any], page_height: float
    ) -> None:
        """Draw a line chart (line plot)."""
        data = attr.get("data") or [[(0, 10), (1, 20), (2, 30), (3, 25)]]
        x = attr.get("x", 0) * mm
        y_top = attr.get("y", 0)
        width = attr.get("width", 100) * mm
        height = attr.get("height", 80) * mm
        colors = attr.get("colors")
        stroke_width = attr.get("stroke_width", 1)

        drawing = Drawing(width, height)

        lp = LinePlot()
        lp.x = 30
        lp.y = 20
        lp.width = width - 50
        lp.height = height - 40
        lp.data = data

        for i in range(len(data)):
            lp.lines[i].strokeWidth = stroke_width
            if colors and i < len(colors):
                lp.lines[i].strokeColor = self._parse_color(colors[i])

        drawing.add(lp)

        y_pt = (page_height - y_top) * mm - height
        renderPDF.draw(drawing, c, x, y_pt)

    def _draw_qrcode(
        self, c: Any, attr: dict[str, Any], page_height: float
    ) -> None:
        """Draw a QR code."""
        value = attr.get("value", "")
        if not value:
            return

        x = attr.get("x", 0) * mm
        y_top = attr.get("y", 0)
        size = attr.get("size", 40) * mm
        bar_width = attr.get("bar_width", 1)
        bar_height = attr.get("bar_height", 1)

        qr_code = qr.QrCodeWidget(value)
        qr_code.barWidth = bar_width
        qr_code.barHeight = bar_height

        bounds = qr_code.getBounds()
        qr_width = bounds[2] - bounds[0]
        qr_height = bounds[3] - bounds[1]

        drawing = Drawing(
            size, size, transform=[size / qr_width, 0, 0, size / qr_height, 0, 0]
        )
        drawing.add(qr_code)

        y_pt = (page_height - y_top) * mm - size
        renderPDF.draw(drawing, c, x, y_pt)
