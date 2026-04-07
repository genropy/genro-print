# Copyright 2025 Softwell S.r.l. - Licensed under Apache License 2.0
# See LICENSE file for details

"""ChartsMixin — chart and QR code elements shared by all print builders."""

from __future__ import annotations

from genro_builders.builder import element


class ChartsMixin:
    """Chart and QR code elements: bar_chart, pie_chart, line_chart, qrcode."""

    @element(
        sub_tags="",
        _meta={"compile_type": "graphics"},
    )
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

    @element(
        sub_tags="",
        _meta={"compile_type": "graphics"},
    )
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

    @element(
        sub_tags="",
        _meta={"compile_type": "graphics"},
    )
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

    @element(
        sub_tags="",
        _meta={"compile_type": "graphics"},
    )
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
