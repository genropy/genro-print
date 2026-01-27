# Claude Code Instructions - genro-print

**Parent Document**: This project follows all policies from the central [meta-genro-modules CLAUDE.md](https://github.com/softwellsrl/meta-genro-modules/blob/main/CLAUDE.md)

## Project-Specific Context

### Current Status

- Development Status: Pre-Alpha
- Has Implementation: No (only structure and documentation)

### Project Description

Print and PDF generation system for Genropy framework. Implements the **Layout/Row/Cell** model with:

- Pure declarative source (no preprocessing during construction)
- Clean separation between source and compiled output
- WeasyPrint backend for PDF generation
- Based on lessons learned from legacy `gnrhtml.py` and `gnrbaghtml.py`

### Core Principles

This project is designed to **avoid the mistakes** of the legacy Genropy print system:

1. **Source must remain pure**: The Bag contains only declarative data, never computed values
2. **No state mutation during construction**: All calculations happen in `compile()`
3. **No side effects in iterators**: Generators should only iterate, not modify state
4. **Callbacks are for customization, not state management**

### Key Documentation

- `docs/analysis/layout_row_cell_theory.md` - Theoretical analysis of the model
- `docs/analysis/legacy_problems.md` - Problems identified in legacy implementation

### Architecture Overview

```
genro-print/
├── src/genro_print/
│   ├── __init__.py
│   ├── builder.py         # PrintBuilder (extends BagBuilderBase)
│   ├── elements/          # Layout, Row, Cell elements
│   ├── pagination/        # Pure pagination calculation
│   └── renderers/         # HTML, PDF renderers
├── tests/
└── docs/
```

### Design Decisions

1. **Builder Pattern**: Uses `genro-bag` BagBuilderBase with `@element` decorators
2. **Two-Phase Compile**: First calculate pagination, then render
3. **Immutable Intermediate**: Pagination result is immutable data structure
4. **Pluggable Renderers**: HTML direct, PDF via WeasyPrint

---

**All general policies are inherited from the parent document.**
