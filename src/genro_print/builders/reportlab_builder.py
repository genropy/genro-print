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

        # Check if we have canvas elements (low-level) or platypus (high-level)
        has_canvas = any(e.get("type") == "canvas" for e in computed.elements)
        has_platypus = any(e.get("type") == "platypus" for e in computed.elements)

        if has_canvas and not has_platypus:
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
        """Render using Canvas (low-level drawing)."""
        buffer = BytesIO()

        c = canvas.Canvas(
            buffer,
            pagesize=(computed.page_width * mm, computed.page_height * mm),
        )

        page_height = computed.page_height

        for elem in computed.elements:
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

        # Transform coordinates (top-left to bottom-left)
        if "y" in attr:
            attr["y"] = (page_height - attr["y"]) * mm
        if "x" in attr:
            attr["x"] = attr["x"] * mm
        if "y1" in attr:
            attr["y1"] = (page_height - attr["y1"]) * mm
        if "y2" in attr:
            attr["y2"] = (page_height - attr["y2"]) * mm
        if "x1" in attr:
            attr["x1"] = attr["x1"] * mm
        if "x2" in attr:
            attr["x2"] = attr["x2"] * mm
        if "y_cen" in attr:
            attr["y_cen"] = (page_height - attr["y_cen"]) * mm
        if "x_cen" in attr:
            attr["x_cen"] = attr["x_cen"] * mm

        # Convert dimensions to points
        for key in ["width", "height", "r", "radius"]:
            if key in attr:
                attr[key] = attr[key] * mm

        # Get canvas method
        canvas_method = getattr(c, method_name, None)
        if canvas_method:
            # Filter kwargs by method signature
            sig = inspect.signature(canvas_method)
            valid_params = set(sig.parameters.keys())
            filtered_attr = {k: v for k, v in attr.items() if k in valid_params}
            canvas_method(**filtered_attr)
