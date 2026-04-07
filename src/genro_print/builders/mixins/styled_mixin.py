# Copyright 2025 Softwell S.r.l. - Licensed under Apache License 2.0
# See LICENSE file for details

"""StyledMixin — declarative styled elements with style inheritance."""

from __future__ import annotations

from genro_builders.builder import element

# Style attribute names that can be inherited via styledblock
STYLE_ATTRS = frozenset({
    "fontname",
    "size",
    "color",
    "fill_color",
    "stroke_color",
    "stroke_width",
})


class StyledMixin:
    """Styled elements: styledblock, statictext, styledrect, etc."""

    @element(
        sub_tags="*",
        _meta={"compile_type": "container"},
    )
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
        """
        ...

    @element(
        sub_tags="",
        _meta={"compile_type": "styled_canvas"},
    )
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
        """Positioned text with style (inherited or direct)."""
        ...

    @element(
        sub_tags="",
        _meta={"compile_type": "styled_canvas"},
    )
    def styledline(
        self,
        x1: float = 0.0,
        y1: float = 0.0,
        x2: float = 10.0,
        y2: float = 10.0,
        stroke_color: str | None = None,
        stroke_width: float | None = None,
    ) -> None:
        """Line with style (inherited or direct)."""
        ...

    @element(
        sub_tags="",
        _meta={"compile_type": "styled_canvas"},
    )
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
        """Rectangle with style (inherited or direct)."""
        ...

    @element(
        sub_tags="",
        _meta={"compile_type": "styled_canvas"},
    )
    def styledcircle(
        self,
        x_cen: float = 0.0,
        y_cen: float = 0.0,
        radius: float = 5.0,
        fill_color: str | None = None,
        stroke_color: str | None = None,
        stroke_width: float | None = None,
    ) -> None:
        """Circle with style (inherited or direct)."""
        ...

    @element(
        sub_tags="",
        _meta={"compile_type": "styled_canvas"},
    )
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
        """Ellipse with style (inherited or direct)."""
        ...

    @element(
        sub_tags="",
        _meta={"compile_type": "styled_canvas"},
    )
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
        """Image at position."""
        ...
