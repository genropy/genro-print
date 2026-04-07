# Copyright 2025 Softwell S.r.l. - Licensed under Apache License 2.0
# See LICENSE file for details

"""CanvasMixin — low-level ReportLab Canvas drawing elements."""

from __future__ import annotations

from genro_builders.builder import element


class CanvasMixin:
    """Canvas drawing elements: drawstring, rect, circle, line, etc."""

    @element(
        sub_tags="",
        _meta={"compile_type": "canvas", "compile_method": "drawString"},
    )
    def drawstring(
        self,
        x: float = 0.0,
        y: float = 0.0,
        text: str = "",
        mode: int | None = None,
    ) -> None:
        """Draw a string at position (x, y)."""
        ...

    @element(
        sub_tags="",
        _meta={"compile_type": "canvas", "compile_method": "drawCentredString"},
    )
    def drawcentredstring(
        self,
        x: float = 0.0,
        y: float = 0.0,
        text: str = "",
    ) -> None:
        """Draw a centered string at position (x, y)."""
        ...

    @element(
        sub_tags="",
        _meta={"compile_type": "canvas", "compile_method": "drawRightString"},
    )
    def drawrightstring(
        self,
        x: float = 0.0,
        y: float = 0.0,
        text: str = "",
    ) -> None:
        """Draw a right-aligned string ending at position (x, y)."""
        ...

    @element(
        sub_tags="",
        _meta={"compile_type": "canvas", "compile_method": "rect"},
    )
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

    @element(
        sub_tags="",
        _meta={"compile_type": "canvas", "compile_method": "roundRect"},
    )
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

    @element(
        sub_tags="",
        _meta={"compile_type": "canvas", "compile_method": "circle"},
    )
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

    @element(
        sub_tags="",
        _meta={"compile_type": "canvas", "compile_method": "ellipse"},
    )
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

    @element(
        sub_tags="",
        _meta={"compile_type": "canvas", "compile_method": "line"},
    )
    def line(
        self,
        x1: float = 0.0,
        y1: float = 0.0,
        x2: float = 10.0,
        y2: float = 10.0,
    ) -> None:
        """Draw a line."""
        ...

    @element(
        sub_tags="",
        _meta={"compile_type": "canvas", "compile_method": "drawImage"},
    )
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

    @element(
        sub_tags="",
        _meta={"compile_type": "canvas", "compile_method": "setFont"},
    )
    def setfont(
        self,
        psfontname: str = "Helvetica",
        size: float = 12.0,
    ) -> None:
        """Set the current font."""
        ...

    @element(
        sub_tags="",
        _meta={"compile_type": "canvas", "compile_method": "setFillColor"},
    )
    def setfillcolor(
        self,
        color: str = "black",
    ) -> None:
        """Set the fill color."""
        ...

    @element(
        sub_tags="",
        _meta={"compile_type": "canvas", "compile_method": "setStrokeColor"},
    )
    def setstrokecolor(
        self,
        color: str = "black",
    ) -> None:
        """Set the stroke color."""
        ...

    @element(
        sub_tags="",
        _meta={"compile_type": "canvas", "compile_method": "setLineWidth"},
    )
    def setlinewidth(
        self,
        width: float = 1.0,
    ) -> None:
        """Set the line width."""
        ...

    @element(
        sub_tags="",
        _meta={"compile_type": "canvas", "compile_method": "saveState"},
    )
    def savestate(self) -> None:
        """Save the current graphics state."""
        ...

    @element(
        sub_tags="",
        _meta={"compile_type": "canvas", "compile_method": "restoreState"},
    )
    def restorestate(self) -> None:
        """Restore the previously saved graphics state."""
        ...

    @element(
        sub_tags="",
        _meta={"compile_type": "canvas", "compile_method": "showPage"},
    )
    def showpage(self) -> None:
        """End current page and start a new one (Canvas mode)."""
        ...
