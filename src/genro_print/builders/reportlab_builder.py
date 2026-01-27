# Copyright 2025 Softwell S.r.l. - Licensed under Apache License 2.0
# See LICENSE file for details

"""
ReportLabBuilder - Builder for ReportLab PDF generation.

Element methods for ReportLab Canvas and Platypus.
Each method is decorated with @element and has proper sub_tags and typed parameters.

Two-phase workflow:
1. compile(bag) - produces ComputedReportLab intermediate structure
2. render(computed) - produces PDF bytes

Canvas elements: low-level drawing (drawString, rect, line, circle, etc.)
Platypus elements: high-level flowables (paragraph, table, image, spacer, etc.)
"""

from __future__ import annotations

import inspect
from io import BytesIO
from typing import TYPE_CHECKING, Any

from genro_bag import Bag
from genro_bag.builder import BagBuilderBase, element

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


class ComputedReportLab:
    """Intermediate structure produced by compile().

    Contains all elements ready for rendering, with resolved parameters.
    """

    def __init__(
        self,
        elements: list[dict[str, Any]],
        page_width: float = 210,
        page_height: float = 297,
        margins: tuple[float, float, float, float] = (10, 10, 10, 10),
    ) -> None:
        """Initialize computed structure.

        Args:
            elements: List of compiled element dictionaries
            page_width: Page width in mm (default A4)
            page_height: Page height in mm (default A4)
            margins: (left, right, top, bottom) margins in mm
        """
        self.elements = elements
        self.page_width = page_width
        self.page_height = page_height
        self.margins = margins


class ReportLabBuilder(BagBuilderBase):
    """Builder for ReportLab PDF elements.

    Supports both Canvas (low-level) and Platypus (high-level) elements.
    Use compile() to produce ComputedReportLab, then render() to produce PDF.

    Example usage:
        ```python
        from genro_bag import Bag
        from genro_print.builders import ReportLabBuilder

        # Build document
        doc = Bag(builder=ReportLabBuilder)
        doc.document(width=210.0, height=297.0)
        doc.paragraph(content="Hello World", style="Normal")
        doc.spacer(height=10.0)
        doc.paragraph(content="Another paragraph")

        # Compile and render
        computed = doc.builder.compile(doc)
        pdf_bytes = doc.builder.render(computed)
        ```
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
    # Platypus elements (high-level flowables)
    # -------------------------------------------------------------------------

    @element(sub_tags="", compile_type="platypus", compile_class="Paragraph")
    def paragraph(
        self,
        content: str = "",
        style: str = "Normal",
        bullet_text: str | None = None,
    ) -> None:
        """A paragraph of text."""
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
    # Canvas elements (low-level drawing)
    # -------------------------------------------------------------------------

    @element(sub_tags="", compile_type="canvas", compile_method="drawString")
    def drawstring(
        self,
        x: float = 0.0,
        y: float = 0.0,
        text: str = "",
        mode: int | None = None,
    ) -> None:
        """Draw a string at position (x, y)."""
        ...

    @element(sub_tags="", compile_type="canvas", compile_method="drawCentredString")
    def drawcentredstring(
        self,
        x: float = 0.0,
        y: float = 0.0,
        text: str = "",
    ) -> None:
        """Draw a centered string at position (x, y)."""
        ...

    @element(sub_tags="", compile_type="canvas", compile_method="drawRightString")
    def drawrightstring(
        self,
        x: float = 0.0,
        y: float = 0.0,
        text: str = "",
    ) -> None:
        """Draw a right-aligned string ending at position (x, y)."""
        ...

    @element(sub_tags="", compile_type="canvas", compile_method="rect")
    def rect(
        self,
        x: float = 0.0,
        y: float = 0.0,
        width: float = 10.0,
        height: float = 10.0,
        stroke: int = 1,
        fill: int = 0,
    ) -> None:
        """Draw a rectangle."""
        ...

    @element(sub_tags="", compile_type="canvas", compile_method="roundRect")
    def roundrect(
        self,
        x: float = 0.0,
        y: float = 0.0,
        width: float = 10.0,
        height: float = 10.0,
        radius: float = 2.0,
        stroke: int = 1,
        fill: int = 0,
    ) -> None:
        """Draw a rounded rectangle."""
        ...

    @element(sub_tags="", compile_type="canvas", compile_method="circle")
    def circle(
        self,
        x_cen: float = 0.0,
        y_cen: float = 0.0,
        r: float = 5.0,
        stroke: int = 1,
        fill: int = 0,
    ) -> None:
        """Draw a circle."""
        ...

    @element(sub_tags="", compile_type="canvas", compile_method="ellipse")
    def ellipse(
        self,
        x1: float = 0.0,
        y1: float = 0.0,
        x2: float = 10.0,
        y2: float = 5.0,
        stroke: int = 1,
        fill: int = 0,
    ) -> None:
        """Draw an ellipse."""
        ...

    @element(sub_tags="", compile_type="canvas", compile_method="line")
    def line(
        self,
        x1: float = 0.0,
        y1: float = 0.0,
        x2: float = 10.0,
        y2: float = 10.0,
    ) -> None:
        """Draw a line."""
        ...

    @element(sub_tags="", compile_type="canvas", compile_method="drawImage")
    def drawimage(
        self,
        image: str = "",
        x: float = 0.0,
        y: float = 0.0,
        width: float | None = None,
        height: float | None = None,
        mask: str | None = None,
        preserve_aspect_ratio: bool = False,
    ) -> None:
        """Draw an image at position (x, y)."""
        ...

    @element(sub_tags="", compile_type="canvas", compile_method="setFont")
    def setfont(
        self,
        psfontname: str = "Helvetica",
        size: float = 12.0,
    ) -> None:
        """Set the current font."""
        ...

    @element(sub_tags="", compile_type="canvas", compile_method="setFillColor")
    def setfillcolor(
        self,
        color: str = "black",
    ) -> None:
        """Set the fill color."""
        ...

    @element(sub_tags="", compile_type="canvas", compile_method="setStrokeColor")
    def setstrokecolor(
        self,
        color: str = "black",
    ) -> None:
        """Set the stroke color."""
        ...

    @element(sub_tags="", compile_type="canvas", compile_method="setLineWidth")
    def setlinewidth(
        self,
        width: float = 1.0,
    ) -> None:
        """Set the line width."""
        ...

    @element(sub_tags="", compile_type="canvas", compile_method="saveState")
    def savestate(self) -> None:
        """Save the current graphics state."""
        ...

    @element(sub_tags="", compile_type="canvas", compile_method="restoreState")
    def restorestate(self) -> None:
        """Restore the previously saved graphics state."""
        ...

    @element(sub_tags="", compile_type="canvas", compile_method="showPage")
    def showpage(self) -> None:
        """End current page and start a new one (Canvas mode)."""
        ...

    # -------------------------------------------------------------------------
    # Graphics elements (charts, drawings)
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
        """A vertical bar chart.

        Args:
            data: List of data series (e.g., [[10, 20, 30], [15, 25, 35]])
            categories: Category labels for X axis
            x: X position in mm
            y: Y position in mm (from top)
            width: Chart width in mm
            height: Chart height in mm
            colors: List of colors for each series (hex or names)
            bar_width: Width of each bar in points
            group_spacing: Spacing between bar groups in points
        """
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
        """A pie chart.

        Args:
            data: List of values
            labels: Labels for each slice
            x: X position in mm
            y: Y position in mm (from top)
            width: Chart width in mm
            height: Chart height in mm
            colors: List of colors for each slice (hex or names)
            start_angle: Starting angle in degrees (default 90 = top)
        """
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
        """A line chart (line plot).

        Args:
            data: List of series, each series is list of (x, y) tuples
            x: X position in mm
            y: Y position in mm (from top)
            width: Chart width in mm
            height: Chart height in mm
            colors: List of colors for each line (hex or names)
            stroke_width: Line width in points
        """
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
        """A QR code.

        Args:
            value: The data to encode in the QR code
            x: X position in mm
            y: Y position in mm (from top)
            size: QR code size in mm
            bar_width: Width of each module (default 1)
            bar_height: Height of each module (default 1)
        """
        ...

    # -------------------------------------------------------------------------
    # Compile: transform Bag to ComputedReportLab
    # -------------------------------------------------------------------------

    def compile(self, bag: Bag) -> ComputedReportLab:
        """Compile a Bag to ComputedReportLab structure.

        Args:
            bag: Bag containing ReportLab elements

        Returns:
            ComputedReportLab with all elements ready for rendering
        """
        elements: list[dict[str, Any]] = []
        page_width = 210.0
        page_height = 297.0
        margins = (10.0, 10.0, 10.0, 10.0)

        for node in bag:
            tag = node.tag or ""

            # Document node sets page properties
            if tag == "document":
                page_width = node.attr.get("width", 210.0)
                page_height = node.attr.get("height", 297.0)
                margins = (
                    node.attr.get("left_margin", 10.0),
                    node.attr.get("right_margin", 10.0),
                    node.attr.get("top_margin", 10.0),
                    node.attr.get("bottom_margin", 10.0),
                )
                # Compile children of document
                if isinstance(node.value, Bag):
                    for child in node.value:
                        compiled = self._compile_node(child)
                        if compiled:
                            elements.append(compiled)
            else:
                compiled = self._compile_node(node)
                if compiled:
                    elements.append(compiled)

        return ComputedReportLab(
            elements=elements,
            page_width=page_width,
            page_height=page_height,
            margins=margins,
        )

    def _compile_node(self, node: BagNode) -> dict[str, Any] | None:
        """Compile a single node to element dictionary."""
        tag = node.tag or ""
        if not tag:
            return None

        # Check for dedicated compile method
        compile_method = getattr(self, f"_compile_{tag}", None)
        if compile_method:
            result: dict[str, Any] | None = compile_method(node)
            return result

        # Get compile info from schema
        schema_info = self.get_schema_info(tag)
        compile_kwargs = schema_info.get("compile_kwargs", {})

        compile_type = compile_kwargs.get("type")
        compile_class = compile_kwargs.get("class")
        compile_method_name = compile_kwargs.get("method")

        # Get node attributes (excluding internal ones)
        attr = {k: v for k, v in node.attr.items() if not k.startswith("_")}

        # Get content from node value if present
        content = ""
        if node.value and not isinstance(node.value, Bag):
            content = str(node.value)
        if not attr.get("content") and content:
            attr["content"] = content

        return {
            "tag": tag,
            "type": compile_type or "platypus",
            "class": compile_class,
            "method": compile_method_name,
            "attr": attr,
            "children": self._compile_children(node) if isinstance(node.value, Bag) else [],
        }

    def _compile_children(self, node: BagNode) -> list[dict[str, Any]]:
        """Compile child nodes."""
        children: list[dict[str, Any]] = []
        if isinstance(node.value, Bag):
            for child in node.value:
                compiled = self._compile_node(child)
                if compiled:
                    children.append(compiled)
        return children

    # -------------------------------------------------------------------------
    # Dedicated compile methods for elements needing special handling
    # -------------------------------------------------------------------------

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
            "data": rows_data,
            "children": [],
        }

    # -------------------------------------------------------------------------
    # Render: transform ComputedReportLab to PDF
    # -------------------------------------------------------------------------

    def render(self, computed: ComputedReportLab) -> bytes:
        """Render ComputedReportLab to PDF bytes.

        Args:
            computed: ComputedReportLab structure

        Returns:
            PDF bytes
        """
        if not REPORTLAB_AVAILABLE:
            msg = "ReportLab required: pip install reportlab"
            raise ImportError(msg)

        # Check what types of elements we have
        has_canvas = any(e.get("type") == "canvas" for e in computed.elements)
        has_platypus = any(e.get("type") == "platypus" for e in computed.elements)
        has_graphics = any(e.get("type") == "graphics" for e in computed.elements)

        # Graphics elements require canvas rendering
        if has_graphics or (has_canvas and not has_platypus):
            return self._render_canvas(computed)
        return self._render_platypus(computed)

    def _render_platypus(self, computed: ComputedReportLab) -> bytes:
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

        for elem in computed.elements:
            flowable = self._create_flowable(elem, styles)
            if flowable:
                flowables.append(flowable)

        doc.build(flowables)
        buffer.seek(0)
        return buffer.read()

    def _create_flowable(self, elem: dict[str, Any], styles: Any) -> Any:
        """Create a Platypus flowable from element dict."""
        tag = elem.get("tag", "")
        attr = elem.get("attr", {})

        # Dispatch to specific factory method
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

    def _render_canvas(self, computed: ComputedReportLab) -> bytes:
        """Render using Canvas (low-level drawing) and Graphics."""
        buffer = BytesIO()

        c = canvas.Canvas(
            buffer,
            pagesize=(computed.page_width * mm, computed.page_height * mm),
        )

        page_height = computed.page_height

        for elem in computed.elements:
            elem_type = elem.get("type")
            if elem_type == "graphics":
                self._draw_graphics_element(c, elem, page_height)
            elif elem_type == "canvas":
                self._draw_canvas_element(c, elem, page_height)

        c.save()
        buffer.seek(0)
        return buffer.read()

    def _draw_canvas_element(
        self, c: Any, elem: dict[str, Any], page_height: float
    ) -> None:
        """Draw a canvas element."""
        attr = dict(elem.get("attr", {}))
        method_name = elem.get("method")

        if not method_name:
            return

        # Transform coordinates and dimensions
        self._transform_canvas_coords(attr, page_height)

        # Handle special parameter mappings for ReportLab methods
        # setFillColor and setStrokeColor expect 'aColor' not 'color'
        if method_name in ("setFillColor", "setStrokeColor") and "color" in attr:
            attr["aColor"] = self._parse_color(attr.pop("color"))

        # Get canvas method
        canvas_method = getattr(c, method_name, None)
        if canvas_method:
            # Filter kwargs by method signature
            sig = inspect.signature(canvas_method)
            valid_params = set(sig.parameters.keys())
            filtered_attr = {k: v for k, v in attr.items() if k in valid_params}
            canvas_method(**filtered_attr)

    def _transform_canvas_coords(
        self, attr: dict[str, Any], page_height: float
    ) -> None:
        """Transform coordinates from top-left to bottom-left and mm to points."""
        # X coordinates: just convert mm to points
        x_keys = ("x", "x1", "x2", "x_cen")
        for key in x_keys:
            if key in attr:
                attr[key] = attr[key] * mm

        # Y coordinates: flip and convert mm to points
        y_keys = ("y", "y1", "y2", "y_cen")
        for key in y_keys:
            if key in attr:
                attr[key] = (page_height - attr[key]) * mm

        # Convert dimensions to points
        dim_keys = ("width", "height", "r", "radius")
        for key in dim_keys:
            if key in attr:
                attr[key] = attr[key] * mm

    def _draw_graphics_element(
        self, c: Any, elem: dict[str, Any], page_height: float
    ) -> None:
        """Draw a graphics element (charts, etc.)."""
        tag = elem.get("tag", "")
        attr = elem.get("attr", {})

        # Dispatch to specific drawing method
        draw_method = getattr(self, f"_draw_{tag}", None)
        if draw_method:
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

        # Create Drawing
        drawing = Drawing(width, height)

        # Create chart
        chart = VerticalBarChart()
        chart.x = 30  # leave space for labels
        chart.y = 20
        chart.width = width - 50
        chart.height = height - 40
        chart.data = data
        chart.barWidth = bar_width
        chart.groupSpacing = group_spacing

        # Set categories if provided
        if categories:
            chart.categoryAxis.categoryNames = categories

        # Set colors if provided
        if colors:
            for i, color in enumerate(colors):
                if i < len(chart.bars):
                    chart.bars[i].fillColor = self._parse_color(color)

        drawing.add(chart)

        # Convert Y coordinate (top-left to bottom-left)
        y_pt = (page_height - y_top) * mm - height

        # Render drawing to canvas
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

        # Create Drawing
        drawing = Drawing(width, height)

        # Create pie chart
        pie = Pie()
        pie.x = 10
        pie.y = 10
        pie.width = width - 20
        pie.height = height - 20
        pie.data = data
        pie.startAngle = start_angle

        # Set labels if provided
        if labels:
            pie.labels = labels

        # Set colors if provided
        if colors:
            for i, color in enumerate(colors):
                if i < len(pie.slices):
                    pie.slices[i].fillColor = self._parse_color(color)

        drawing.add(pie)

        # Convert Y coordinate (top-left to bottom-left)
        y_pt = (page_height - y_top) * mm - height

        # Render drawing to canvas
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

        # Create Drawing
        drawing = Drawing(width, height)

        # Create line plot
        lp = LinePlot()
        lp.x = 30  # leave space for labels
        lp.y = 20
        lp.width = width - 50
        lp.height = height - 40
        lp.data = data

        # Set line properties
        for i in range(len(data)):
            lp.lines[i].strokeWidth = stroke_width
            if colors and i < len(colors):
                lp.lines[i].strokeColor = self._parse_color(colors[i])

        drawing.add(lp)

        # Convert Y coordinate (top-left to bottom-left)
        y_pt = (page_height - y_top) * mm - height

        # Render drawing to canvas
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

        # Create QR code
        qr_code = qr.QrCodeWidget(value)
        qr_code.barWidth = bar_width
        qr_code.barHeight = bar_height

        # Get the bounds of the QR code
        bounds = qr_code.getBounds()
        qr_width = bounds[2] - bounds[0]
        qr_height = bounds[3] - bounds[1]

        # Create drawing with scaled size
        drawing = Drawing(size, size, transform=[size / qr_width, 0, 0, size / qr_height, 0, 0])
        drawing.add(qr_code)

        # Convert Y coordinate (top-left to bottom-left)
        y_pt = (page_height - y_top) * mm - size

        # Render drawing to canvas
        renderPDF.draw(drawing, c, x, y_pt)
