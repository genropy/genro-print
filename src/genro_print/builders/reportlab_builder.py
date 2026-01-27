# Copyright 2025 Softwell S.r.l. - Licensed under Apache License 2.0
# See LICENSE file for details

"""
ReportLabBuilder - Builder for ReportLab PDF generation.

Auto-generated element methods for ReportLab Canvas and Platypus.
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

from genro_bag import Bag, BagBuilderBase
from genro_bag.builder import element

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
        doc.document(width=210, height=297)
        doc.paragraph(content="Hello World", style="Normal")
        doc.spacer(height=10)
        doc.paragraph(content="Another paragraph")

        # Compile and render
        computed = ReportLabBuilder.compile(doc)
        pdf_bytes = ReportLabBuilder.render(computed)
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
        width: float = 210,
        height: float = 297,
        left_margin: float = 10,
        right_margin: float = 10,
        top_margin: float = 10,
        bottom_margin: float = 10,
        title: str | None = None,
        author: str | None = None,
    ) -> None:
        """Document root element with page size and margins.

        Args:
            width: Page width in mm (default A4)
            height: Page height in mm (default A4)
            left_margin: Left margin in mm
            right_margin: Right margin in mm
            top_margin: Top margin in mm
            bottom_margin: Bottom margin in mm
            title: Document title (metadata)
            author: Document author (metadata)
        """

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
        """A paragraph of text.

        Args:
            content: Text content (can include basic HTML markup)
            style: Style name from stylesheet (Normal, Heading1, etc.)
            bullet_text: Optional bullet prefix
        """

    @element(sub_tags="", compile_type="platypus", compile_class="Spacer")
    def spacer(
        self,
        width: float = 0,
        height: float = 10,
    ) -> None:
        """Vertical space between elements.

        Args:
            width: Width in mm (usually 0)
            height: Height in mm
        """

    @element(sub_tags="", compile_type="platypus", compile_class="PageBreak")
    def pagebreak(self) -> None:
        """Force a page break."""

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
        """An image flowable.

        Args:
            src: Image file path or URL
            width: Width in mm (None = auto)
            height: Height in mm (None = auto)
            kind: 'direct', 'percentage', or 'absolute'
            mask: Color mask
            lazy: Lazy loading (1 = enabled)
        """

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
        """A table flowable.

        Args:
            col_widths: Column widths in mm (None = auto)
            row_heights: Row heights in mm (None = auto)
            repeat_rows: Number of header rows to repeat on each page
            repeat_cols: Number of columns to repeat on each page
            split_by_row: Allow splitting between rows
            h_align: Horizontal alignment (LEFT, CENTER, RIGHT)
        """

    @element(sub_tags="cell", parent_tags="table")
    def row(self) -> None:
        """A table row. Contains cell elements."""

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
        """A table cell.

        Args:
            content: Cell content
            colspan: Number of columns to span
            rowspan: Number of rows to span
            align: Horizontal alignment (LEFT, CENTER, RIGHT)
            valign: Vertical alignment (TOP, MIDDLE, BOTTOM)
            background: Background color
        """

    # -------------------------------------------------------------------------
    # Canvas elements (low-level drawing)
    # -------------------------------------------------------------------------

    @element(sub_tags="", compile_type="canvas", compile_method="drawString")
    def drawstring(
        self,
        x: float = 0,
        y: float = 0,
        text: str = "",
        mode: int | None = None,
    ) -> None:
        """Draw a string at position (x, y).

        Args:
            x: X coordinate in mm
            y: Y coordinate in mm
            text: Text to draw
            mode: Text rendering mode
        """

    @element(sub_tags="", compile_type="canvas", compile_method="drawCentredString")
    def drawcentredstring(
        self,
        x: float = 0,
        y: float = 0,
        text: str = "",
    ) -> None:
        """Draw a centered string at position (x, y).

        Args:
            x: X coordinate (center point) in mm
            y: Y coordinate in mm
            text: Text to draw
        """

    @element(sub_tags="", compile_type="canvas", compile_method="drawRightString")
    def drawrightstring(
        self,
        x: float = 0,
        y: float = 0,
        text: str = "",
    ) -> None:
        """Draw a right-aligned string ending at position (x, y).

        Args:
            x: X coordinate (right edge) in mm
            y: Y coordinate in mm
            text: Text to draw
        """

    @element(sub_tags="", compile_type="canvas", compile_method="rect")
    def rect(
        self,
        x: float = 0,
        y: float = 0,
        width: float = 10,
        height: float = 10,
        stroke: int = 1,
        fill: int = 0,
    ) -> None:
        """Draw a rectangle.

        Args:
            x: X coordinate in mm
            y: Y coordinate in mm
            width: Width in mm
            height: Height in mm
            stroke: Draw outline (1 = yes)
            fill: Fill interior (1 = yes)
        """

    @element(sub_tags="", compile_type="canvas", compile_method="roundRect")
    def roundrect(
        self,
        x: float = 0,
        y: float = 0,
        width: float = 10,
        height: float = 10,
        radius: float = 2,
        stroke: int = 1,
        fill: int = 0,
    ) -> None:
        """Draw a rounded rectangle.

        Args:
            x: X coordinate in mm
            y: Y coordinate in mm
            width: Width in mm
            height: Height in mm
            radius: Corner radius in mm
            stroke: Draw outline (1 = yes)
            fill: Fill interior (1 = yes)
        """

    @element(sub_tags="", compile_type="canvas", compile_method="circle")
    def circle(
        self,
        x_cen: float = 0,
        y_cen: float = 0,
        r: float = 5,
        stroke: int = 1,
        fill: int = 0,
    ) -> None:
        """Draw a circle.

        Args:
            x_cen: Center X coordinate in mm
            y_cen: Center Y coordinate in mm
            r: Radius in mm
            stroke: Draw outline (1 = yes)
            fill: Fill interior (1 = yes)
        """

    @element(sub_tags="", compile_type="canvas", compile_method="ellipse")
    def ellipse(
        self,
        x1: float = 0,
        y1: float = 0,
        x2: float = 10,
        y2: float = 5,
        stroke: int = 1,
        fill: int = 0,
    ) -> None:
        """Draw an ellipse.

        Args:
            x1: Left X coordinate in mm
            y1: Bottom Y coordinate in mm
            x2: Right X coordinate in mm
            y2: Top Y coordinate in mm
            stroke: Draw outline (1 = yes)
            fill: Fill interior (1 = yes)
        """

    @element(sub_tags="", compile_type="canvas", compile_method="line")
    def line(
        self,
        x1: float = 0,
        y1: float = 0,
        x2: float = 10,
        y2: float = 10,
    ) -> None:
        """Draw a line.

        Args:
            x1: Start X coordinate in mm
            y1: Start Y coordinate in mm
            x2: End X coordinate in mm
            y2: End Y coordinate in mm
        """

    @element(sub_tags="", compile_type="canvas", compile_method="drawImage")
    def drawimage(
        self,
        image: str = "",
        x: float = 0,
        y: float = 0,
        width: float | None = None,
        height: float | None = None,
        mask: str | None = None,
        preserve_aspect_ratio: bool = False,
    ) -> None:
        """Draw an image at position (x, y).

        Args:
            image: Image file path
            x: X coordinate in mm
            y: Y coordinate in mm
            width: Width in mm (None = original)
            height: Height in mm (None = original)
            mask: Color mask
            preserve_aspect_ratio: Maintain aspect ratio
        """

    @element(sub_tags="", compile_type="canvas", compile_method="setFont")
    def setfont(
        self,
        psfontname: str = "Helvetica",
        size: float = 12,
    ) -> None:
        """Set the current font.

        Args:
            psfontname: Font name (Helvetica, Times-Roman, Courier, etc.)
            size: Font size in points
        """

    @element(sub_tags="", compile_type="canvas", compile_method="setFillColor")
    def setfillcolor(
        self,
        color: str = "black",
    ) -> None:
        """Set the fill color.

        Args:
            color: Color name or hex value
        """

    @element(sub_tags="", compile_type="canvas", compile_method="setStrokeColor")
    def setstrokecolor(
        self,
        color: str = "black",
    ) -> None:
        """Set the stroke color.

        Args:
            color: Color name or hex value
        """

    @element(sub_tags="", compile_type="canvas", compile_method="setLineWidth")
    def setlinewidth(
        self,
        width: float = 1,
    ) -> None:
        """Set the line width.

        Args:
            width: Line width in points
        """

    @element(sub_tags="", compile_type="canvas", compile_method="saveState")
    def savestate(self) -> None:
        """Save the current graphics state."""

    @element(sub_tags="", compile_type="canvas", compile_method="restoreState")
    def restorestate(self) -> None:
        """Restore the previously saved graphics state."""

    @element(sub_tags="", compile_type="canvas", compile_method="showPage")
    def showpage(self) -> None:
        """End current page and start a new one (Canvas mode)."""

    # -------------------------------------------------------------------------
    # Compile: transform Bag to ComputedReportLab
    # -------------------------------------------------------------------------

    @classmethod
    def compile(cls, bag: Bag) -> ComputedReportLab:
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
            tag = node.attr.get("tag", "")

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
                        compiled = cls._compile_node(child)
                        if compiled:
                            elements.append(compiled)
            else:
                compiled = cls._compile_node(node)
                if compiled:
                    elements.append(compiled)

        return ComputedReportLab(
            elements=elements,
            page_width=page_width,
            page_height=page_height,
            margins=margins,
        )

    @classmethod
    def _compile_node(cls, node: BagNode) -> dict[str, Any] | None:
        """Compile a single node to element dictionary.

        Args:
            node: BagNode to compile

        Returns:
            Dictionary with element data, or None if not compilable
        """
        tag = node.attr.get("tag", "")
        if not tag:
            return None

        # Check for dedicated compile method
        compile_method = getattr(cls, f"_compile_{tag}", None)
        if compile_method:
            result: dict[str, Any] | None = compile_method(node)
            return result

        # Generic compilation based on schema info
        attr = dict(node.attr)

        # Get compile info from element decorator
        compile_type = attr.pop("compile_type", None)
        compile_class = attr.pop("compile_class", None)
        compile_method_name = attr.pop("compile_method", None)

        # Remove internal attributes
        attr.pop("tag", None)

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
            "children": cls._compile_children(node) if isinstance(node.value, Bag) else [],
        }

    @classmethod
    def _compile_children(cls, node: BagNode) -> list[dict[str, Any]]:
        """Compile child nodes."""
        children: list[dict[str, Any]] = []
        if isinstance(node.value, Bag):
            for child in node.value:
                compiled = cls._compile_node(child)
                if compiled:
                    children.append(compiled)
        return children

    # -------------------------------------------------------------------------
    # Dedicated compile methods for elements needing special handling
    # -------------------------------------------------------------------------

    @classmethod
    def _compile_table(cls, node: BagNode) -> dict[str, Any]:
        """Compile table with rows and cells."""
        attr = dict(node.attr)
        attr.pop("tag", None)

        rows_data: list[list[str]] = []
        if isinstance(node.value, Bag):
            for row_node in node.value:
                if row_node.attr.get("tag") == "row":
                    row_cells: list[str] = []
                    if isinstance(row_node.value, Bag):
                        for cell_node in row_node.value:
                            if cell_node.attr.get("tag") == "cell":
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

    @classmethod
    def render(cls, computed: ComputedReportLab) -> bytes:
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
            return cls._render_canvas(computed)
        return cls._render_platypus(computed)

    @classmethod
    def _render_platypus(cls, computed: ComputedReportLab) -> bytes:
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
            flowable = cls._create_flowable(elem, styles)
            if flowable:
                flowables.append(flowable)

        doc.build(flowables)
        buffer.seek(0)
        return buffer.read()

    @classmethod
    def _create_flowable(cls, elem: dict[str, Any], styles: Any) -> Any:
        """Create a Platypus flowable from element dict."""
        tag = elem.get("tag", "")
        attr = elem.get("attr", {})

        # Dispatch to specific factory method
        factory = getattr(cls, f"_create_{tag}_flowable", None)
        if factory:
            return factory(elem, attr, styles)
        return None

    @classmethod
    def _create_paragraph_flowable(
        cls,
        elem: dict[str, Any],  # noqa: ARG003
        attr: dict[str, Any],
        styles: Any,
    ) -> Any:
        """Create a Paragraph flowable."""
        content = attr.get("content", "")
        style_name = attr.get("style", "Normal")
        style = styles.get(style_name, styles["Normal"])
        return Paragraph(content, style)

    @classmethod
    def _create_spacer_flowable(
        cls,
        elem: dict[str, Any],  # noqa: ARG003
        attr: dict[str, Any],
        styles: Any,  # noqa: ARG003
    ) -> Any:
        """Create a Spacer flowable."""
        width = attr.get("width", 0) * mm
        height = attr.get("height", 10) * mm
        return Spacer(width, height)

    @classmethod
    def _create_pagebreak_flowable(
        cls,
        elem: dict[str, Any],  # noqa: ARG003
        attr: dict[str, Any],  # noqa: ARG003
        styles: Any,  # noqa: ARG003
    ) -> Any:
        """Create a PageBreak flowable."""
        return PageBreak()

    @classmethod
    def _create_image_flowable(
        cls,
        elem: dict[str, Any],  # noqa: ARG003
        attr: dict[str, Any],
        styles: Any,  # noqa: ARG003
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

    @classmethod
    def _create_table_flowable(
        cls,
        elem: dict[str, Any],
        attr: dict[str, Any],
        styles: Any,  # noqa: ARG003
    ) -> Any:
        """Create a Table flowable."""
        data = elem.get("data", [])
        if not data:
            return None
        col_widths = attr.get("col_widths")
        if col_widths:
            col_widths = [w * mm for w in col_widths]
        return Table(data, colWidths=col_widths)

    @classmethod
    def _render_canvas(cls, computed: ComputedReportLab) -> bytes:
        """Render using Canvas (low-level drawing)."""
        buffer = BytesIO()

        c = canvas.Canvas(
            buffer,
            pagesize=(computed.page_width * mm, computed.page_height * mm),
        )

        page_height = computed.page_height

        for elem in computed.elements:
            cls._draw_canvas_element(c, elem, page_height)

        c.save()
        buffer.seek(0)
        return buffer.read()

    @classmethod
    def _draw_canvas_element(
        cls, c: Any, elem: dict[str, Any], page_height: float
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
