# Copyright 2025 Softwell S.r.l. - Licensed under Apache License 2.0
# See LICENSE file for details

"""Coordinate transformation utilities for genro-print.

genro-print uses a top-left origin coordinate system in millimeters.
ReportLab uses a bottom-left origin coordinate system in points.

This module provides conversion functions between the two systems.
"""

from __future__ import annotations

# ReportLab's mm constant (points per mm)
MM_TO_POINTS = 2.834645669291339


def mm_to_pt(value: float) -> float:
    """Convert millimeters to points."""
    return value * MM_TO_POINTS


def pt_to_mm(value: float) -> float:
    """Convert points to millimeters."""
    return value / MM_TO_POINTS


def flip_y(y: float, page_height: float) -> float:
    """Flip Y coordinate from top-left to bottom-left origin.

    Args:
        y: Y coordinate in top-left system (mm from top)
        page_height: Total page height in mm

    Returns:
        Y coordinate in bottom-left system (mm from bottom)
    """
    return page_height - y


def transform_x(x: float) -> float:
    """Transform X coordinate from mm to points (no flip needed)."""
    return x * MM_TO_POINTS


def transform_y(y: float, page_height: float) -> float:
    """Transform Y coordinate from mm (top-left) to points (bottom-left).

    Args:
        y: Y coordinate in mm from top
        page_height: Total page height in mm

    Returns:
        Y coordinate in points from bottom
    """
    return (page_height - y) * MM_TO_POINTS


def transform_rect_y(y: float, height: float, page_height: float) -> float:
    """Transform rectangle Y from mm (top-left) to points (bottom-left).

    ReportLab draws rectangles from bottom-left corner, so we need to
    subtract the rectangle height as well.

    Args:
        y: Top-left Y coordinate in mm
        height: Rectangle height in mm
        page_height: Total page height in mm

    Returns:
        Bottom-left Y coordinate in points
    """
    return (page_height - y) * MM_TO_POINTS - height * MM_TO_POINTS
