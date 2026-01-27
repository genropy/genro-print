# Getting Started

## Installation

Install genro-print using pip:

```bash
pip install genro-print

# With ReportLab support (recommended)
pip install genro-print[reportlab]

# With all backends
pip install genro-print[all]
```

## Quick Start

### PrintApp (ReportLab Builder)

The simplest way to create a PDF:

```python
from genro_print import PrintApp

class HelloWorld(PrintApp):
    def recipe(self, root):
        doc = root.document(width=210.0, height=297.0)
        doc.paragraph(content="Hello, World!", style="Heading1")

HelloWorld().save("hello.pdf")
```

### LRCPrintApp (Layout/Row/Cell)

For more complex layouts with elastic dimensions:

```python
from genro_print import LRCPrintApp

class MyReport(LRCPrintApp):
    def recipe(self, root):
        layout = root.layout(width=210.0, height=297.0, top=10.0, bottom=10.0)

        # Header row (fixed height)
        header = layout.row(height=25.0, border=True)
        header.cell(width=50.0, content="Logo")
        header.cell(content="Document Title")  # elastic width

        # Content rows (elastic height)
        content = layout.row(height=0, border=True)  # elastic
        content.cell(content="Main content goes here")

LRCPrintApp().save("report.pdf")
```

## Two Approaches

genro-print provides two approaches for PDF generation:

### 1. PrintApp (Direct ReportLab)

Use ReportLab elements directly. Best for:

- Simple documents with paragraphs, tables, and images
- Documents that need automatic page breaks (Platypus)
- Charts and QR codes
- Canvas-level drawing operations

Available elements:

| Element | Description |
|---------|-------------|
| `document` | Page setup (width, height in mm) |
| `paragraph` | Text with ReportLab styles |
| `spacer` | Vertical space |
| `pagebreak` | Force new page |
| `table` | Tables with styling |
| `image` | Images |
| `bar_chart` | Vertical bar charts |
| `pie_chart` | Pie charts |
| `line_chart` | Line plots |
| `qrcode` | QR codes |
| Canvas ops | drawString, rect, circle, line, etc. |

### 2. LRCPrintApp (Layout/Row/Cell)

Define elastic grid layouts. Best for:

- Complex layouts with nested structures
- Documents requiring precise positioning
- Reports with repeating row patterns
- Forms and invoices

Key features:

- **Elastic dimensions**: `width=0` or `height=0` auto-calculates
- **Nested layouts**: Cells can contain sub-layouts
- **Border inheritance**: Borders propagate from layout → row → cell
- **Cell content**: Images, paragraphs, spacers inside cells

## Examples

See the `examples/` directory for complete working examples:

```text
examples/
├── reportlab/
│   ├── basic/           # Simple documents
│   ├── platypus/        # Auto page breaks
│   └── charts/          # Charts and QR codes
└── lrc/
    ├── basic/           # Simple layouts
    └── with_elements/   # Cells with content
```

## Next Steps

- Read the {doc}`analysis/architecture` for design details
- Explore the {doc}`api/index` for full API reference
- Check example code in the repository
