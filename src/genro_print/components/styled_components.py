# Copyright 2025 Softwell S.r.l. - Licensed under Apache License 2.0
# See LICENSE file for details

"""Styled component mixin — reusable composite elements for Styled builder."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from genro_builders.builder import component

if TYPE_CHECKING:
    from genro_builders.builder_bag import Component


class StyledComponentsMixin:
    """Reusable components for styled PDF reports."""

    @component(sub_tags="")
    def labeledtext(
        self,
        comp: Component,
        x: float = 0.0,
        y: float = 0.0,
        label: str = "",
        value: str = "",
        label_width: float | None = None,
        label_bold: bool = True,
        separator: str = " ",
        border_bottom: bool = False,
        **kwargs: Any,
    ) -> Component:
        """Labeled text field: label + value on same line.

        Inherits fontname, size, color from parent styledblock.

        Args:
            comp: Component Bag (provided by decorator)
            x: X position in mm
            y: Y position in mm
            label: Label text
            value: Value text
            label_width: Fixed label width (None = auto from text length)
            label_bold: Whether label is bold
            separator: Separator between label and value
            border_bottom: Draw underline below the text
        """
        fontname = kwargs.get("fontname", "Helvetica")
        size = kwargs.get("size", 11.0)
        color = kwargs.get("color", "black")

        label_fontname = "Helvetica-Bold" if label_bold else fontname

        comp.statictext(
            x=x, y=y,
            text=label + separator,
            fontname=label_fontname,
            size=size, color=color,
        )

        value_x = x + (label_width if label_width else len(label) * size * 0.6)

        comp.statictext(
            x=value_x, y=y,
            text=value,
            fontname=fontname,
            size=size, color=color,
        )

        if border_bottom:
            line_y = y + size * 0.4
            total_width = value_x + len(value) * size * 0.6 - x
            comp.styledline(
                x1=x, y1=line_y,
                x2=x + total_width, y2=line_y,
                stroke_color=kwargs.get("border_color", "gray"),
                stroke_width=kwargs.get("border_width", 0.5),
            )

        return comp

    @component(sub_tags="")
    def titled_box(
        self,
        comp: Component,
        x: float = 0.0,
        y: float = 0.0,
        width: float = 100.0,
        height: float = 50.0,
        title: str = "",
        title_height: float = 8.0,
        **kwargs: Any,
    ) -> Component:
        """Rectangle with a title bar at the top.

        Args:
            comp: Component Bag (provided by decorator)
            x: X position in mm
            y: Y position in mm
            width: Box width in mm
            height: Box height in mm
            title: Title text
            title_height: Height of title bar in mm
        """
        fontname = kwargs.get("fontname", "Helvetica-Bold")
        size = kwargs.get("size", 10.0)
        color = kwargs.get("color", "black")
        fill_color = kwargs.get("fill_color")
        stroke_color = kwargs.get("stroke_color", "black")

        # Main rectangle
        comp.styledrect(
            x=x, y=y, width=width, height=height,
            stroke_color=stroke_color,
        )

        # Title bar background
        if fill_color:
            comp.styledrect(
                x=x, y=y, width=width, height=title_height,
                fill_color=fill_color, stroke_color=stroke_color,
            )

        # Title separator line
        comp.styledline(
            x1=x, y1=y + title_height,
            x2=x + width, y2=y + title_height,
            stroke_color=stroke_color,
        )

        # Title text
        comp.statictext(
            x=x + 2, y=y + 2,
            text=title,
            fontname=fontname,
            size=size, color=color,
        )

        return comp
