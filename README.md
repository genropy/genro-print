# genro-print

Print and PDF generation system for the Genropy framework.

## Status

🟡 **Alpha** - Core functionality implemented, API may change

## Overview

`genro-print` provides three approaches for PDF generation, all built on genro-builders v0.12.0 infrastructure:

### 1. PrintApp (Platypus + Canvas)

Use ReportLab elements directly (paragraphs, tables, images, shapes, charts).

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

### 2. LRCPrintApp (Layout/Row/Cell)

Define layouts with elastic dimensions that auto-calculate.

```python
from genro_print import LRCPrintApp

class MyReport(LRCPrintApp):
    def recipe(self, root):
        layout = root.layout(width=210.0, height=297.0, top=10.0, bottom=10.0)

        header = layout.row(height=25.0, border=True)
        header.cell(width=50.0, content="Logo")
        header.cell(content="Title")  # elastic width

        row = layout.row(height=0, border=True)  # elastic height
        row.cell(content="Content")

MyReport().save("report.pdf")
```

### 3. StyledPrintApp (Declarative Styled Elements)

Position shapes and text with inherited styles via styledblock containers.

```python
from genro_print import StyledPrintApp

class MyReport(StyledPrintApp):
    def recipe(self, root):
        doc = root.document(width=210.0, height=297.0)
        block = doc.styledblock(fontname="Helvetica-Bold", size=14.0, color="navy")
        block.statictext(x=20.0, y=50.0, text="Title")
        block.styledrect(x=20.0, y=70.0, width=100.0, height=40.0,
                         fill_color="lightblue")

MyReport().save("report.pdf")
```

### Data Binding

All app classes support `^pointer` data binding via `store()`:

```python
from genro_print import PrintApp

class InvoiceReport(PrintApp):
    def store(self, data):
        data['company'] = 'Acme Corp'
        data['invoice_no'] = 'INV-2025-001'

    def recipe(self, root):
        root.document(width=210.0, height=297.0)
        root.paragraph(content="^company", style="Title")
        root.paragraph(content="^invoice_no")

InvoiceReport().save("invoice.pdf")
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

### PrintApp (Platypus + Canvas)

- **Platypus**: paragraph, spacer, pagebreak, table/row/cell, image
- **Canvas**: drawString, rect, circle, line, ellipse, roundRect, etc.
- **Charts**: bar_chart, pie_chart, line_chart
- **QR Code**: qrcode element

### LRCPrintApp (Layout/Row/Cell)

- **Elastic dimensions**: `width=0` or `height=0` auto-calculates
- **Nested layouts**: Cells can contain sub-layouts (fractal)
- **Border inheritance**: Borders propagate from layout to row to cell
- **Cell content**: image, paragraph, spacer inside cells
- **Components**: page_template (with slot), two_column_row, label_value_row

### StyledPrintApp (Styled Elements)

- **Style inheritance**: styledblock attributes propagate to children
- **Styled shapes**: styledrect, styledcircle, styledellipse, styledline
- **Positioned text**: statictext with alignment
- **Components**: labeledtext, titled_box

## Examples

See the `examples/` directory:

```text
examples/
├── reportlab/
│   ├── basic/           # hello_world, table, invoice, shapes, multi_page
│   ├── platypus/        # flowables, long_document, with_images
│   └── charts/          # bar_chart, pie_chart, line_chart, qrcode
├── lrc/
│   ├── basic/           # simple_layout, nested_elastic
│   └── with_elements/   # image, paragraph, spacer in cells
└── enhanced/
    ├── basic/           # styled_elements with inheritance
    ├── components/      # labeledtext demo
    └── styledblocks/    # nested style override
```

## Architecture

```text
PrintApp              LRCPrintApp           StyledPrintApp
    │                      │                      │
    ▼                      ▼                      ▼
PrintBuilder         PrintLRCBuilder       PrintStyledBuilder
(mixin-composed)     (mixin-composed)      (mixin-composed)
    │                      │                      │
    ▼ build()              ▼ build()              ▼ build()
Built Bag             Built Bag              Built Bag
    │                      │                      │
    ▼ compile()            ▼ compile()            ▼ compile()
PrintCompiler        LRCPrintCompiler      StyledPrintCompiler
(BagCompilerBase)    (BagCompilerBase)     (BagCompilerBase)
    │                      │                      │
    └──────────────────────┼──────────────────────┘
                           ▼
                    ReportLabBackend
                           │
                           ▼
                       PDF bytes
```

### Key Principles

- **BuilderManager lifecycle**: `store()` -> `recipe()` -> `build()` -> `compile()`
- **Mixin composition**: Element definitions in reusable mixins
- **BagCompilerBase**: Proper compiler infrastructure with `@compiler` dispatch
- **Pointer formali**: `^path` data binding resolved just-in-time during compile
- **Pure declarative source**: Bag contains only what user declared
- **No side effects**: All computation happens in `compile()`

## License

Copyright 2025 Softwell S.r.l.

Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE) for details.
