genro-print Documentation
=========================

Print and PDF generation system for the Genropy framework.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   getting_started
   analysis/index
   api/index

Status
------

🟡 **Alpha** - Core functionality implemented, API may change

Overview
--------

``genro-print`` provides two approaches for PDF generation:

**PrintApp (ReportLab Builder)**

- Paragraphs, tables, images with automatic page breaks (Platypus)
- Canvas operations (drawString, rect, circle, line)
- Charts (bar, pie, line) and QR codes
- Direct ReportLab element access

**LRCPrintApp (Layout/Row/Cell)**

- Elastic grid layouts with auto-calculated dimensions
- Nested layouts with border inheritance
- Cell content elements (images, paragraphs, spacers)
- Pure declarative source using ``genro-bag``

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
