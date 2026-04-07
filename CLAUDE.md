# Claude Code Instructions - genro-print

**Parent Document**: This project follows all policies from the central [meta-genro-modules CLAUDE.md](https://github.com/softwellsrl/meta-genro-modules/blob/main/CLAUDE.md)

## Project-Specific Context

### Current Status

- Development Status: Alpha
- Has Implementation: Yes

### Project Description

Print and PDF generation system for Genropy framework. Three builder types built on genro-builders v0.12.0 infrastructure:

- **PrintBuilder** (Platypus + Canvas) — classic PDF reports with flowables and canvas drawing
- **PrintLRCBuilder** (Layout/Row/Cell) — elastic grid layout with automatic dimension calculation
- **PrintStyledBuilder** (Styled elements) — declarative styled shapes with style inheritance

Key features:

- Pure declarative source (no preprocessing during construction)
- Clean separation between source and compiled output via BagCompilerBase
- ReportLab backend for PDF generation
- Data binding with `^pointer` syntax via BuilderManager
- Reusable components via `@component` with named slots

### Core Principles

1. **Source must remain pure**: The Bag contains only declarative data, never computed values
2. **No state mutation during construction**: All calculations happen in `compile()`
3. **No side effects in iterators**: Generators should only iterate, not modify state
4. **Callbacks are for customization, not state management**

### Key Documentation

- `docs/analysis/layout_row_cell_theory.md` - Theoretical analysis of the LRC model
- `docs/analysis/legacy_problems.md` - Problems identified in legacy implementation
- `docs/analysis/architecture.md` - Architecture overview

### Architecture Overview

```text
src/genro_print/
├── print_app.py                    # PrintApp, LRCPrintApp, StyledPrintApp (BuilderManager)
├── builders/
│   ├── print_builder.py            # PrintBuilder (Platypus + Canvas)
│   ├── print_lrc_builder.py        # PrintLRCBuilder (Layout/Row/Cell)
│   ├── print_styled_builder.py     # PrintStyledBuilder (Styled shapes)
│   └── mixins/                     # 6 shared mixin modules
├── compilers/
│   ├── print_compiler.py           # BagCompilerBase for Platypus + Canvas
│   ├── lrc_print_compiler.py       # BagCompilerBase for LRC
│   ├── styled_print_compiler.py    # BagCompilerBase for Styled
│   ├── lrc_resolver.py             # Elastic dimension algorithm
│   └── reportlab_backend.py        # Shared ReportLab engine
├── components/                     # @component mixins (labeledtext, page_template, etc.)
├── computed/                       # ComputedLayout dataclasses
└── utils/                          # coordinates.py, pdf_utils.py
```

### Design Decisions

1. **Mixin-composed builders**: Element definitions in reusable mixins (DocumentMixin, ChartsMixin shared)
2. **BagCompilerBase**: Proper genro-builders compiler infrastructure with `@compiler` dispatch
3. **BuilderManager**: App classes use BuilderManager for lifecycle (setup/build/compile)
4. **Pointer formali**: `^path` data binding resolved just-in-time during compile
5. **ReportLabBackend**: Single shared engine for all PDF rendering operations
6. **ComputedLayout**: Immutable intermediate structure between LRC resolve and render

---

**All general policies are inherited from the parent document.**
