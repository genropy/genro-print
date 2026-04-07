# Copyright 2025 Softwell S.r.l. - Licensed under Apache License 2.0
# See LICENSE file for details

"""ReportLabBackend — shared ReportLab rendering engine for all compilers.

Encapsulates all ReportLab interaction: coordinate conversion,
color parsing, flowable creation, canvas drawing, chart rendering.
Used by PrintCompiler, LRCPrintCompiler, and StyledPrintCompiler.
"""

from __future__ import annotations

import inspect
from io import BytesIO
from typing import TYPE_CHECKING, Any

from genro_print.utils.coordinates import MM_TO_POINTS

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
    from reportlab.lib.utils import ImageReader
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
    mm = MM_TO_POINTS

if TYPE_CHECKING:
    from genro_print.computed import (
        ComputedCell,
        ComputedCellElement,
        ComputedLayout,
    )


class ReportLabBackend:
    """Shared ReportLab rendering engine.

    Handles two rendering modes:
    - Platypus mode: high-level flowables (paragraph, table, etc.)
    - Canvas mode: low-level drawing + styled elements + charts + LRC layouts
    """

    def __init__(self) -> None:
        if not REPORTLAB_AVAILABLE:
            msg = "ReportLab required: pip install reportlab"
            raise ImportError(msg)
        self._page_width: float = 210.0
        self._page_height: float = 297.0
        self._margins: tuple[float, float, float, float] = (10.0, 10.0, 10.0, 10.0)
        self._canvas: Any = None
        self._buffer: BytesIO = BytesIO()
        self._flowables: list[Any] = []
        self._mode: str | None = None  # "platypus" or "canvas"

    # -------------------------------------------------------------------------
    # Page setup
    # -------------------------------------------------------------------------

    def set_page(
        self,
        width: float = 210.0,
        height: float = 297.0,
        left_margin: float = 10.0,
        right_margin: float = 10.0,
        top_margin: float = 10.0,
        bottom_margin: float = 10.0,
    ) -> None:
        """Configure page dimensions."""
        self._page_width = width
        self._page_height = height
        self._margins = (left_margin, right_margin, top_margin, bottom_margin)

    def ensure_canvas(self) -> Any:
        """Ensure canvas mode is active. Returns the canvas."""
        if self._mode == "platypus":
            msg = "Cannot mix platypus and canvas modes in same document"
            raise RuntimeError(msg)
        if self._canvas is None:
            self._mode = "canvas"
            self._canvas = canvas.Canvas(
                self._buffer,
                pagesize=(self._page_width * mm, self._page_height * mm),
            )
        return self._canvas

    def ensure_platypus(self) -> None:
        """Ensure platypus mode is active."""
        if self._mode == "canvas":
            msg = "Cannot mix platypus and canvas modes in same document"
            raise RuntimeError(msg)
        self._mode = "platypus"

    # -------------------------------------------------------------------------
    # Finalize
    # -------------------------------------------------------------------------

    def finalize(self) -> bytes:
        """Produce final PDF bytes."""
        if self._mode == "canvas" and self._canvas is not None:
            self._canvas.save()
            self._buffer.seek(0)
            return self._buffer.read()

        if self._mode == "platypus":
            buffer = BytesIO()
            left, right, top, bottom = self._margins
            doc = SimpleDocTemplate(
                buffer,
                pagesize=(self._page_width * mm, self._page_height * mm),
                leftMargin=left * mm,
                rightMargin=right * mm,
                topMargin=top * mm,
                bottomMargin=bottom * mm,
            )
            doc.build(self._flowables)
            buffer.seek(0)
            return buffer.read()

        # Empty document — return empty canvas
        c = self.ensure_canvas()
        c.save()
        self._buffer.seek(0)
        return self._buffer.read()

    # -------------------------------------------------------------------------
    # Platypus flowables
    # -------------------------------------------------------------------------

    def add_paragraph(self, content: str = "", style: str = "Normal", **kwargs: Any) -> None:  # noqa: ARG002
        """Add a paragraph flowable."""
        self.ensure_platypus()
        styles = getSampleStyleSheet()
        para_style = styles.get(style, styles["Normal"])
        self._flowables.append(Paragraph(content, para_style))

    def add_spacer(self, width: float = 0.0, height: float = 10.0) -> None:
        """Add a spacer flowable."""
        self.ensure_platypus()
        self._flowables.append(Spacer(width * mm, height * mm))

    def add_pagebreak(self) -> None:
        """Add a page break."""
        self.ensure_platypus()
        self._flowables.append(PageBreak())

    def add_image(self, src: str = "", width: float | None = None,
                  height: float | None = None, **kwargs: Any) -> None:  # noqa: ARG002
        """Add an image flowable."""
        self.ensure_platypus()
        w = width * mm if width else None
        h = height * mm if height else None
        self._flowables.append(Image(src, width=w, height=h))

    def add_table(self, data: list[list[str]], col_widths: list[float] | None = None,
                  **kwargs: Any) -> None:  # noqa: ARG002
        """Add a table flowable."""
        self.ensure_platypus()
        cw = [w * mm for w in col_widths] if col_widths else None
        self._flowables.append(Table(data, colWidths=cw))

    # -------------------------------------------------------------------------
    # Canvas operations
    # -------------------------------------------------------------------------

    def canvas_drawstring(self, x: float, y: float, text: str, **kwargs: Any) -> None:  # noqa: ARG002
        """Draw string on canvas (coords in mm, top-left origin)."""
        c = self.ensure_canvas()
        x_pt = x * mm
        y_pt = (self._page_height - y) * mm
        c.drawString(x_pt, y_pt, text)

    def canvas_drawcentredstring(self, x: float, y: float, text: str) -> None:
        """Draw centered string on canvas."""
        c = self.ensure_canvas()
        c.drawCentredString(x * mm, (self._page_height - y) * mm, text)

    def canvas_drawrightstring(self, x: float, y: float, text: str) -> None:
        """Draw right-aligned string on canvas."""
        c = self.ensure_canvas()
        c.drawRightString(x * mm, (self._page_height - y) * mm, text)

    def canvas_op(self, method_name: str, attrs: dict[str, Any]) -> None:
        """Execute arbitrary canvas method with coordinate transform."""
        c = self.ensure_canvas()
        transformed = dict(attrs)
        self._transform_canvas_coords(transformed)

        # Handle special parameter mappings
        if method_name in ("setFillColor", "setStrokeColor") and "color" in transformed:
            transformed["aColor"] = self._parse_color(transformed.pop("color"))

        canvas_method = getattr(c, method_name, None)
        if canvas_method:
            sig = inspect.signature(canvas_method)
            valid_params = set(sig.parameters.keys())
            filtered = {k: v for k, v in transformed.items() if k in valid_params}
            canvas_method(**filtered)

    def _transform_canvas_coords(self, attr: dict[str, Any]) -> None:
        """Transform coordinates from mm top-left to points bottom-left."""
        for key in ("x", "x1", "x2", "x_cen"):
            if key in attr:
                attr[key] = attr[key] * mm

        for key in ("y", "y1", "y2", "y_cen"):
            if key in attr:
                attr[key] = (self._page_height - attr[key]) * mm

        for key in ("width", "height", "r", "radius"):
            if key in attr:
                attr[key] = attr[key] * mm

    # -------------------------------------------------------------------------
    # Styled elements (with inherited styles)
    # -------------------------------------------------------------------------

    def draw_statictext(self, x: float, y: float, text: str, align: str = "left",
                        style: dict[str, Any] | None = None) -> None:
        """Draw styled text on canvas."""
        c = self.ensure_canvas()
        x_pt = x * mm
        y_pt = (self._page_height - y) * mm

        if style:
            self._apply_text_style(c, style)

        if align == "center":
            c.drawCentredString(x_pt, y_pt, text)
        elif align == "right":
            c.drawRightString(x_pt, y_pt, text)
        else:
            c.drawString(x_pt, y_pt, text)

    def draw_styledline(self, x1: float, y1: float, x2: float, y2: float,
                        style: dict[str, Any] | None = None) -> None:
        """Draw styled line on canvas."""
        c = self.ensure_canvas()
        if style:
            self._apply_shape_style(c, style)
        c.line(x1 * mm, (self._page_height - y1) * mm,
               x2 * mm, (self._page_height - y2) * mm)

    def draw_styledrect(self, x: float, y: float, width: float, height: float,
                        radius: float = 0, style: dict[str, Any] | None = None) -> None:
        """Draw styled rectangle on canvas."""
        c = self.ensure_canvas()
        if style:
            self._apply_shape_style(c, style)
        x_pt = x * mm
        y_pt = (self._page_height - y) * mm - height * mm
        w_pt = width * mm
        h_pt = height * mm
        fill = 1 if style and style.get("fill_color") else 0
        if radius > 0:
            c.roundRect(x_pt, y_pt, w_pt, h_pt, radius * mm, stroke=1, fill=fill)
        else:
            c.rect(x_pt, y_pt, w_pt, h_pt, stroke=1, fill=fill)

    def draw_styledcircle(self, x_cen: float, y_cen: float, radius: float,
                          style: dict[str, Any] | None = None) -> None:
        """Draw styled circle on canvas."""
        c = self.ensure_canvas()
        if style:
            self._apply_shape_style(c, style)
        fill = 1 if style and style.get("fill_color") else 0
        c.circle(x_cen * mm, (self._page_height - y_cen) * mm,
                 radius * mm, stroke=1, fill=fill)

    def draw_styledellipse(self, x1: float, y1: float, x2: float, y2: float,
                           style: dict[str, Any] | None = None) -> None:
        """Draw styled ellipse on canvas."""
        c = self.ensure_canvas()
        if style:
            self._apply_shape_style(c, style)
        fill = 1 if style and style.get("fill_color") else 0
        c.ellipse(x1 * mm, (self._page_height - y1) * mm,
                  x2 * mm, (self._page_height - y2) * mm,
                  stroke=1, fill=fill)

    def draw_styledimage(self, image_path: str, x: float, y: float,
                         width: float | None = None, height: float | None = None,
                         mask: str | None = None,
                         preserve_aspect_ratio: bool = False) -> None:
        """Draw image at position."""
        if not image_path:
            return
        c = self.ensure_canvas()
        w = width * mm if width else None
        h = height * mm if height else None
        y_pt = (self._page_height - y) * mm - (h if h else 0)
        c.drawImage(image_path, x * mm, y_pt, width=w, height=h,
                    mask=mask, preserveAspectRatio=preserve_aspect_ratio)

    def _apply_text_style(self, c: Any, style: dict[str, Any]) -> None:
        """Apply text style attributes to canvas."""
        fontname = style.get("fontname", "Helvetica")
        size = style.get("size", 12.0)
        color = style.get("color", "black")
        c.setFont(fontname, size)
        c.setFillColor(self._parse_color(color))

    def _apply_shape_style(self, c: Any, style: dict[str, Any]) -> None:
        """Apply shape style attributes to canvas."""
        stroke_color = style.get("stroke_color", "black")
        stroke_width = style.get("stroke_width", 1.0)
        fill_color = style.get("fill_color")
        c.setStrokeColor(self._parse_color(stroke_color))
        c.setLineWidth(stroke_width)
        if fill_color:
            c.setFillColor(self._parse_color(fill_color))

    # -------------------------------------------------------------------------
    # Charts and QR code
    # -------------------------------------------------------------------------

    def draw_bar_chart(self, x: float, y: float, width: float, height: float,
                       data: list[list[float]] | None = None,
                       categories: list[str] | None = None,
                       colors: list[str] | None = None,
                       bar_width: float = 10, group_spacing: float = 5) -> None:
        """Draw a vertical bar chart."""
        c = self.ensure_canvas()
        data = data or [[10, 20, 30, 40]]
        w_pt = width * mm
        h_pt = height * mm

        drawing = Drawing(w_pt, h_pt)
        chart = VerticalBarChart()
        chart.x = 30
        chart.y = 20
        chart.width = w_pt - 50
        chart.height = h_pt - 40
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

        y_pt = (self._page_height - y) * mm - h_pt
        renderPDF.draw(drawing, c, x * mm, y_pt)

    def draw_pie_chart(self, x: float, y: float, width: float, height: float,
                       data: list[float] | None = None,
                       labels: list[str] | None = None,
                       colors: list[str] | None = None,
                       start_angle: float = 90) -> None:
        """Draw a pie chart."""
        c = self.ensure_canvas()
        data = data or [10, 20, 30, 40]
        w_pt = width * mm
        h_pt = height * mm

        drawing = Drawing(w_pt, h_pt)
        pie = Pie()
        pie.x = 10
        pie.y = 10
        pie.width = w_pt - 20
        pie.height = h_pt - 20
        pie.data = data
        pie.startAngle = start_angle
        if labels:
            pie.labels = labels
        if colors:
            for i, color in enumerate(colors):
                if i < len(pie.slices):
                    pie.slices[i].fillColor = self._parse_color(color)
        drawing.add(pie)

        y_pt = (self._page_height - y) * mm - h_pt
        renderPDF.draw(drawing, c, x * mm, y_pt)

    def draw_line_chart(self, x: float, y: float, width: float, height: float,
                        data: list[list[tuple[float, float]]] | None = None,
                        colors: list[str] | None = None,
                        stroke_width: float = 1) -> None:
        """Draw a line chart."""
        c = self.ensure_canvas()
        data = data or [[(0, 10), (1, 20), (2, 30), (3, 25)]]
        w_pt = width * mm
        h_pt = height * mm

        drawing = Drawing(w_pt, h_pt)
        lp = LinePlot()
        lp.x = 30
        lp.y = 20
        lp.width = w_pt - 50
        lp.height = h_pt - 40
        lp.data = data
        for i in range(len(data)):
            lp.lines[i].strokeWidth = stroke_width
            if colors and i < len(colors):
                lp.lines[i].strokeColor = self._parse_color(colors[i])
        drawing.add(lp)

        y_pt = (self._page_height - y) * mm - h_pt
        renderPDF.draw(drawing, c, x * mm, y_pt)

    def draw_qrcode(self, x: float, y: float, value: str = "", size: float = 40,
                    bar_width: float = 1, bar_height: float = 1) -> None:
        """Draw a QR code."""
        if not value:
            return
        c = self.ensure_canvas()
        size_pt = size * mm

        qr_code = qr.QrCodeWidget(value)
        qr_code.barWidth = bar_width
        qr_code.barHeight = bar_height

        bounds = qr_code.getBounds()
        qr_width = bounds[2] - bounds[0]
        qr_height = bounds[3] - bounds[1]

        drawing = Drawing(size_pt, size_pt,
                          transform=[size_pt / qr_width, 0, 0, size_pt / qr_height, 0, 0])
        drawing.add(qr_code)

        y_pt = (self._page_height - y) * mm - size_pt
        renderPDF.draw(drawing, c, x * mm, y_pt)

    # -------------------------------------------------------------------------
    # LRC Layout rendering
    # -------------------------------------------------------------------------

    def render_layout(self, layout: ComputedLayout) -> None:
        """Render a ComputedLayout to the canvas."""
        c = self.ensure_canvas()
        page_height_pt = self._page_height * mm
        self._render_layout_recursive(c, layout, page_height_pt)

    def _render_layout_recursive(self, c: Any, layout: ComputedLayout,
                                 page_height_pt: float) -> None:
        """Recursively render a layout and its rows/cells."""
        if layout.border_width > 0:
            self._draw_lrc_rect(c, layout.x, layout.y, layout.width, layout.height,
                                layout.border_width, layout.border_color, page_height_pt)

        for row in layout.rows:
            for cell in row.cells:
                self._render_lrc_cell(c, cell, page_height_pt)

    def _render_lrc_cell(self, c: Any, cell: ComputedCell,
                         page_height_pt: float) -> None:
        """Render a single LRC cell."""
        if cell.border and cell.border_width > 0:
            self._draw_lrc_rect(c, cell.x, cell.y,
                                cell.computed_width, cell.computed_height,
                                cell.border_width, cell.border_color, page_height_pt)

        content_y = cell.y
        content_height = cell.computed_height

        if cell.lbl and cell.lbl_height > 0:
            x_pt = (cell.x + 1) * mm
            y_pt = page_height_pt - (cell.y + 1) * mm - 8
            c.setFont("Helvetica", 8)
            c.setFillColor(self._parse_color("#666666"))
            c.drawString(x_pt, y_pt, cell.lbl)
            content_y += cell.lbl_height
            content_height -= cell.lbl_height

        if cell.content:
            x_pt = (cell.x + 1) * mm
            y_pt = page_height_pt - (content_y + 1) * mm - 10
            c.setFont("Helvetica", 10)
            c.setFillColor(self._parse_color("black"))
            c.drawString(x_pt, y_pt, cell.content)

        if cell.elements:
            self._render_lrc_cell_elements(c, cell.elements,
                                           cell.x + 1, content_y + 1,
                                           cell.computed_width - 2,
                                           content_height - 2,
                                           page_height_pt)

        if cell.nested_layout:
            self._render_layout_recursive(c, cell.nested_layout, page_height_pt)

    def _draw_lrc_rect(self, c: Any, x: float, y: float, width: float, height: float,
                       stroke_width: float, stroke_color: str,
                       page_height_pt: float) -> None:
        """Draw an LRC rectangle (coordinates in mm, top-left origin)."""
        x_pt = x * mm
        y_pt = page_height_pt - y * mm - height * mm
        c.setStrokeColor(self._parse_color(stroke_color))
        c.setLineWidth(stroke_width * mm)
        c.rect(x_pt, y_pt, width * mm, height * mm, stroke=1, fill=0)

    def _render_lrc_cell_elements(self, c: Any, elements: list[ComputedCellElement],
                                  x: float, y: float, width: float, height: float,  # noqa: ARG002
                                  page_height_pt: float) -> None:
        """Render cell child elements (image, paragraph, spacer)."""
        from genro_print.computed import CellElementType  # noqa: PLC0415

        current_y = y
        for elem in elements:
            if elem.element_type == CellElementType.IMAGE:
                current_y = self._render_lrc_image(c, elem, x, current_y, width,
                                                   page_height_pt)
            elif elem.element_type == CellElementType.PARAGRAPH:
                current_y = self._render_lrc_paragraph(c, elem, x, current_y,
                                                       page_height_pt)
            elif elem.element_type == CellElementType.SPACER:
                current_y += elem.attrs.get("height", 5)

    def _render_lrc_image(self, c: Any, elem: ComputedCellElement,
                          x: float, y: float, available_width: float,
                          page_height_pt: float) -> float:
        """Render an LRC image element. Returns new Y position."""
        attrs = elem.attrs
        src = attrs.get("src", "")
        if not src:
            return y

        img_width = attrs.get("width", 0)
        img_height = attrs.get("height", 0)
        align = attrs.get("align", "left")

        try:
            img = ImageReader(src)
            native_w, native_h = img.getSize()

            if img_width == 0 and img_height == 0:
                img_width = native_w * 25.4 / 72
                img_height = native_h * 25.4 / 72
            elif img_width == 0:
                img_width = img_height * native_w / native_h
            elif img_height == 0:
                img_height = img_width * native_h / native_w

            if align == "center":
                img_x = x + (available_width - img_width) / 2
            elif align == "right":
                img_x = x + available_width - img_width
            else:
                img_x = x

            x_pt = img_x * mm
            y_pt = page_height_pt - y * mm - img_height * mm
            c.drawImage(img, x_pt, y_pt, width=img_width * mm,
                        height=img_height * mm, preserveAspectRatio=True)
            result: float = y + img_height
            return result
        except Exception:
            return y

    def _render_lrc_paragraph(self, c: Any, elem: ComputedCellElement,
                              x: float, y: float,
                              page_height_pt: float) -> float:
        """Render an LRC paragraph element. Returns new Y position."""
        attrs = elem.attrs
        content = attrs.get("content", "")
        if not content:
            return y
        font_name = attrs.get("font_name", "Helvetica")
        font_size = attrs.get("font_size", 10)
        color = attrs.get("color", "black")

        x_pt = x * mm
        y_pt = page_height_pt - y * mm - font_size
        c.setFont(font_name, font_size)
        c.setFillColor(self._parse_color(color))
        c.drawString(x_pt, y_pt, content)

        line_height: float = font_size * 1.2 / mm
        return y + line_height

    # -------------------------------------------------------------------------
    # Color utilities
    # -------------------------------------------------------------------------

    def _parse_color(self, color: str) -> Any:
        """Parse color string to ReportLab color."""
        if color.startswith("#"):
            return HexColor(color)
        return toColor(color)
