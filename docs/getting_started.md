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

### PrintApp (Platypus + Canvas)

The simplest way to create a PDF:

```python
from genro_print import PrintApp

class HelloWorld(PrintApp):
    def recipe(self, root):
        root.document(width=210.0, height=297.0)
        root.paragraph(content="Hello, World!", style="Heading1")

HelloWorld().save("hello.pdf")
```

### LRCPrintApp (Layout/Row/Cell)

For complex layouts with elastic dimensions:

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
        content = layout.row(height=0, border=True)
        content.cell(content="Main content goes here")

MyReport().save("report.pdf")
```

### StyledPrintApp (Declarative Styled Elements)

For positioned shapes and text with style inheritance:

```python
from genro_print import StyledPrintApp

class MyReport(StyledPrintApp):
    def recipe(self, root):
        doc = root.document(width=210.0, height=297.0)

        # Style block — children inherit fontname, size, color
        block = doc.styledblock(fontname="Helvetica-Bold", size=14.0, color="navy")
        block.statictext(x=20.0, y=50.0, text="Title")
        block.statictext(x=20.0, y=70.0, text="Subtitle", size=10.0, color="gray")

        # Shapes with inherited styles
        shapes = doc.styledblock(fill_color="lightblue", stroke_color="navy")
        shapes.styledrect(x=20.0, y=90.0, width=100.0, height=40.0)
        shapes.styledcircle(x_cen=150.0, y_cen=110.0, radius=20.0)

MyReport().save("styled.pdf")
```

## Data Binding

All app classes support `^pointer` data binding. Use `store()` to populate data, and `^path` in element attributes to reference it:

```python
from genro_print import PrintApp

class InvoiceReport(PrintApp):
    def store(self, data):
        data['company'] = 'Acme Corp'
        data['date'] = '2025-01-27'

    def recipe(self, root):
        root.document(width=210.0, height=297.0)
        root.paragraph(content="^company", style="Title")
        root.paragraph(content="^date")

InvoiceReport().save("invoice.pdf")
```

## Three Approaches

### 1. PrintApp (Platypus + Canvas)

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
- **Border inheritance**: Borders propagate from layout to row to cell
- **Cell content**: Images, paragraphs, spacers inside cells
- **Components**: page_template, two_column_row, label_value_row

### 3. StyledPrintApp (Styled Elements)

Declarative positioned elements with style inheritance. Best for:

- Documents with precise visual design
- Shapes and text with consistent styling
- Templates where style blocks simplify repetition

Key features:

- **Style inheritance**: styledblock attributes propagate to all children
- **Styled shapes**: styledrect, styledcircle, styledellipse, styledline
- **Positioned text**: statictext with alignment
- **Components**: labeledtext, titled_box

## Examples

See the `examples/` directory for complete working examples:

```text
examples/
├── reportlab/
│   ├── basic/           # Simple documents
│   ├── platypus/        # Auto page breaks
│   └── charts/          # Charts and QR codes
├── lrc/
│   ├── basic/           # Simple layouts
│   └── with_elements/   # Cells with content
└── enhanced/
    ├── basic/           # Styled elements
    ├── components/      # labeledtext demo
    └── styledblocks/    # Nested style override
```

## Next Steps

- Read the {doc}`analysis/architecture` for design details
- Read the {doc}`analysis/layout_row_cell_theory` for LRC model theory
- Explore the {doc}`api/index` for full API reference
- Check example code in the repository
