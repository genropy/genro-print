# Copyright 2025 Softwell S.r.l. - Licensed under Apache License 2.0
# See LICENSE file for details

"""
ComputedLayout: Data structures with resolved dimensions.

These dataclasses represent the result of compiling a Layout/Row/Cell structure.
They contain all absolute coordinates (in mm) and calculated dimensions,
including resolution of elastic values.

They serve as the bridge between LRCPrintBuilder (which produces them) and
ReportLabBuilder (which consumes them to generate PDF).
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ComputedCell:
    """Cell with resolved dimensions and coordinates.

    Attributes:
        x: Absolute X coordinate (mm) - top-left corner
        y: Absolute Y coordinate (mm) - top-left corner
        computed_width: Calculated width (mm)
        computed_height: Calculated height (mm)
        border: Whether the cell has a border
        border_width: Border thickness (mm)
        border_color: Border color
        content: Text content (if present)
        nested_layout: Nested layout (if present)
    """

    x: float
    y: float
    computed_width: float
    computed_height: float
    border: bool = False
    border_width: float = 0.0
    border_color: str = "black"
    content: str | None = None
    nested_layout: ComputedLayout | None = None

    # Optional label attributes
    lbl: str | None = None
    lbl_height: float = 0.0
    lbl_class: str | None = None
    content_class: str | None = None


@dataclass
class ComputedRow:
    """Row with resolved dimensions.

    Attributes:
        y: Absolute Y coordinate (mm) - top of row
        computed_height: Calculated height (mm)
        cells: List of cells with resolved dimensions
    """

    y: float
    computed_height: float
    cells: list[ComputedCell] = field(default_factory=list)


@dataclass
class ComputedLayout:
    """Layout with all dimensions resolved.

    This is the intermediate structure between LRCPrintBuilder and ReportLabBuilder.
    It contains all absolute coordinates and calculated dimensions.

    Attributes:
        x: Absolute X coordinate (mm) - top-left corner
        y: Absolute Y coordinate (mm) - top-left corner
        width: Total width (mm)
        height: Total height (mm)
        top: Top margin (mm)
        bottom: Bottom margin (mm)
        left: Left margin (mm)
        right: Right margin (mm)
        border_width: Layout border thickness (mm)
        border_color: Layout border color
        rows: List of rows with resolved dimensions
    """

    x: float
    y: float
    width: float
    height: float
    top: float = 0.0
    bottom: float = 0.0
    left: float = 0.0
    right: float = 0.0
    border_width: float = 0.0
    border_color: str = "black"
    rows: list[ComputedRow] = field(default_factory=list)

    @property
    def useful_width(self) -> float:
        """Useful width (excluding margins)."""
        return self.width - self.left - self.right

    @property
    def useful_height(self) -> float:
        """Useful height (excluding margins)."""
        return self.height - self.top - self.bottom
