# Copyright 2025 Softwell S.r.l. - Licensed under Apache License 2.0
# See LICENSE file for details

"""
PDF utilities using PyMuPDF (fitz).

Post-processing functionality for PDFs:
- Watermark
- Merge documents
- PDF → image (preview)
- Append pages

Note: PyMuPDF is AGPL. Commercial closed-source use requires paid license.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

try:
    import fitz

    FITZ_AVAILABLE = True
except ImportError:
    FITZ_AVAILABLE = False

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path


class PdfUtils:
    """Utility for PDF manipulation using PyMuPDF."""

    @staticmethod
    def _check_fitz() -> None:
        """Check that PyMuPDF is available."""
        if not FITZ_AVAILABLE:
            msg = "PyMuPDF required: pip install pymupdf"
            raise ImportError(msg)

    @classmethod
    def add_watermark(
        cls,
        input_pdf: str | Path,
        output_pdf: str | Path,
        text: str,
        opacity: float = 0.3,
        angle: float = 45,
        fontsize: int = 72,
        color: tuple[float, float, float] = (0.8, 0.8, 0.8),
    ) -> None:
        """Add watermark to all pages of a PDF.

        Args:
            input_pdf: Input PDF path
            output_pdf: Output PDF path
            text: Watermark text
            opacity: Opacity (0.0 - 1.0)
            angle: Rotation angle in degrees
            fontsize: Font size
            color: RGB color (0.0 - 1.0 per channel)
        """
        cls._check_fitz()

        doc = fitz.open(str(input_pdf))
        for page in doc:
            rect = page.rect
            # Page center
            point = fitz.Point(rect.width / 2, rect.height / 2)
            page.insert_text(
                point,
                text,
                fontsize=fontsize,
                rotate=angle,
                opacity=opacity,
                color=color,
            )
        doc.save(str(output_pdf))
        doc.close()

    @classmethod
    def merge(
        cls,
        inputs: Sequence[str | Path],
        output: str | Path,
    ) -> None:
        """Merge multiple PDFs into one.

        Args:
            inputs: List of PDF paths to merge
            output: Output PDF path
        """
        cls._check_fitz()

        result = fitz.open()
        for pdf_path in inputs:
            doc = fitz.open(str(pdf_path))
            result.insert_pdf(doc)
            doc.close()
        result.save(str(output))
        result.close()

    @classmethod
    def to_image(
        cls,
        pdf_path: str | Path,
        page: int = 0,
        dpi: int = 150,
    ) -> bytes:
        """Convert a PDF page to PNG image.

        Args:
            pdf_path: PDF path
            page: Page number (0-indexed)
            dpi: Resolution in DPI

        Returns:
            PNG image bytes
        """
        cls._check_fitz()

        doc = fitz.open(str(pdf_path))
        if page >= len(doc):
            msg = f"Page {page} not found (document has {len(doc)} pages)"
            raise ValueError(msg)

        pix = doc[page].get_pixmap(dpi=dpi)
        png_bytes: bytes = pix.tobytes("png")
        doc.close()
        return png_bytes

    @classmethod
    def append_pages(
        cls,
        target: str | Path,
        source: str | Path,
        pages: Sequence[int] | None = None,
        output: str | Path | None = None,
    ) -> None:
        """Append pages from one PDF to another.

        Args:
            target: Target PDF
            source: Source PDF to take pages from
            pages: List of page indices to append (None = all)
            output: Output path (None = overwrite target)
        """
        cls._check_fitz()

        target_doc = fitz.open(str(target))
        source_doc = fitz.open(str(source))

        if pages is None:
            # All pages
            target_doc.insert_pdf(source_doc)
        else:
            # Only specified pages
            for page_num in pages:
                if page_num < len(source_doc):
                    target_doc.insert_pdf(source_doc, from_page=page_num, to_page=page_num)

        output_path = str(output) if output else str(target)
        target_doc.save(output_path)
        target_doc.close()
        source_doc.close()

    @classmethod
    def page_count(cls, pdf_path: str | Path) -> int:
        """Return the number of pages in a PDF.

        Args:
            pdf_path: PDF path

        Returns:
            Number of pages
        """
        cls._check_fitz()

        doc = fitz.open(str(pdf_path))
        count = len(doc)
        doc.close()
        return count
