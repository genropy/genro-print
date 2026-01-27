# genro-print

Print and PDF generation system for the Genropy framework.

## Status

🔴 **Pre-Alpha** - Architecture and documentation phase

## Overview

`genro-print` implements a **Layout/Row/Cell** model for document generation with:

- Pure declarative source using `genro-bag`
- Clean separation between source and compiled output
- WeasyPrint backend for PDF generation
- Pagination calculation as pure function

## Installation

```bash
pip install genro-print

# With PDF support
pip install genro-print[pdf]
```

## Quick Example

```python
from genro_bag import Bag
from genro_print import PrintBuilder

# Create document
doc = Bag(builder=PrintBuilder)

# Define layout (declarative - no computation yet)
page = doc.page(width=210, height=297, margin=10)
layout = page.layout()

header = layout.row(height=20)
header.cell("Invoice", width=100)
header.cell(field="invoice_number")  # Resolved at compile time

body = layout.row()  # Elastic height
body.cell(width=50).layout()  # Nested layout

# Compile with data
html = doc.builder.compile(
    data={'invoice_number': 'INV-001'},
    output_format='html'
)

# Or generate PDF
pdf_bytes = doc.builder.compile(
    data={'invoice_number': 'INV-001'},
    output_format='pdf'
)
```

## Architecture

### Two-Phase Compilation

1. **Pagination Phase** (pure function)
   - Calculate which rows fit on each page
   - Resolve elastic heights/widths
   - Output: immutable page structure

2. **Rendering Phase**
   - Generate HTML/PDF from page structure
   - No state mutation

### Key Principles

- **Source remains pure**: Bag contains only what user declared
- **All computation in compile()**: No preprocessing during construction
- **No side effects in iteration**: Generators only iterate
- **Testable in isolation**: Pagination logic can be unit tested

## Documentation

- [Layout/Row/Cell Theory](docs/analysis/layout_row_cell_theory.md)
- [Legacy Problems Analysis](docs/analysis/legacy_problems.md)

## License

Copyright 2025 Softwell S.r.l.

Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE) for details.
