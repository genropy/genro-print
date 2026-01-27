# genro-print

Print and PDF generation system for the Genropy framework.

## Status

🟡 **Alpha** - Core functionality implemented, API may change

## Overview

`genro-print` provides two approaches for PDF generation:

### 1. ReportLab Builder (Direct)

Use ReportLab elements directly (paragraphs, tables, images, shapes).

```python
from genro_print import PrintApp

class MyReport(PrintApp):
    def recipe(self, root):
        root.document(width=210.0, height=297.0)
        root.paragraph(content="Hello World!", style="Heading1")
        root.spacer(height=10.0)
        root.paragraph(content="This is a PDF document.")

MyReport().save("report.pdf")
```

### 2. Layout/Row/Cell Builder (Elastic Grid)

Define layouts with elastic dimensions that auto-calculate.

```python
from genro_print import LRCPrintApp

class MyReport(LRCPrintApp):
    def recipe(self, root):
        layout = root.layout(width=210.0, height=297.0, top=10.0, bottom=10.0)

        # Header row (fixed height)
        header = layout.row(height=25.0, border=True)
        header.cell(width=50.0, content="Logo")
        header.cell(content="Title")  # elastic width

        # Content rows (elastic height)
        row1 = layout.row(height=0, border=True)  # elastic
        row1.cell(content="Row 1")

        row2 = layout.row(height=0, border=True)  # elastic
        row2.cell(content="Row 2")

LRCPrintApp().save("report.pdf")
```

## Installation

```bash
pip install genro-print

# With ReportLab support (recommended)
pip install genro-print[reportlab]

# With all backends
pip install genro-print[all]
```

## Features

### PrintApp (ReportLab Builder)

- **document**: Page setup (width, height)
- **paragraph**: Text with styles
- **spacer**: Vertical space
- **pagebreak**: Force new page
- **table/row/cell**: Tables with styling
- **image**: Images
- **Canvas operations**: drawString, rect, circle, line, etc.
- **Charts**: bar_chart, pie_chart, line_chart
- **QR Code**: qrcode element

### LRCPrintApp (Layout/Row/Cell)

- **Elastic dimensions**: `width=0` or `height=0` auto-calculates
- **Nested layouts**: Cells can contain sub-layouts
- **Border inheritance**: Borders propagate from layout → row → cell
- **Margin support**: top, bottom, left, right margins
- **Cell content elements**: Cells can contain:
  - `image`: Images with alignment (left, center, right)
  - `paragraph`: Styled text with font, size, color
  - `spacer`: Vertical spacing

## Examples

See the `examples/` directory:

```text
examples/
├── reportlab/
│   ├── basic/
│   │   ├── hello_world/
│   │   ├── multi_paragraph/
│   │   ├── simple_table/
│   │   ├── styled_table/
│   │   ├── multi_page/
│   │   ├── images_and_shapes/
│   │   └── invoice/
│   ├── platypus/
│   │   ├── flowables/        # Paragraphs, spacers, tables with auto page breaks
│   │   ├── with_images/      # Images in documents
│   │   └── long_document/    # Multi-page document with mixed content
│   └── charts/
│       ├── bar_chart/        # Vertical bar charts
│       ├── pie_chart/        # Pie charts with labels
│       ├── line_chart/       # Line plots
│       └── qrcode/           # QR codes
└── lrc/
    ├── basic/
    │   ├── simple_layout/
    │   └── nested_elastic/
    └── with_elements/        # Images, paragraphs, spacers in cells
```

Each example folder contains a `.py` file and the generated `.pdf`.

## Architecture

```text
PrintApp                          LRCPrintApp
    │                                  │
    ▼                                  ▼
Bag(ReportLabBuilder)            Bag(LRCPrintBuilder)
    │                                  │
    ▼ compile()                        ▼ compile()
ComputedReportLab                ComputedLayout
    │                                  │
    ▼ render()                         ▼ LRCReportLabRenderer
PDF bytes                         PDF bytes
```

### Key Principles

- **Recipe pattern**: Define structure in `recipe()`, data in `_data` Bag
- **Two-phase compilation**: First calculate dimensions, then render
- **Pure declarative source**: Bag contains only what user declared
- **No side effects**: All computation happens in `compile()`

## License

Copyright 2025 Softwell S.r.l.

Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE) for details.
