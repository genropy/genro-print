# Architettura genro-print

**Status**: 🔴 DA REVISIONARE
**Data**: 2026-04-07

## Decisione Architetturale

genro-print adotta un'architettura basata su **genro-builders v0.12.0**:

1. **Tre builder separati** (Platypus+Canvas, Layout/Row/Cell, Styled) assemblati da mixin
2. **BagCompilerBase** per compilazione Bag -> PDF via ReportLabBackend condiviso
3. **BuilderManager** per app class con data binding `^pointer`
4. **PyMuPDF (fitz)** - Utilities opzionali (watermark, merge, preview)

---

## 1. Motivazione

### 1.1 Perché Mantenere Layout/Row/Cell

| Vantaggio | Spiegazione |
|-----------|-------------|
| **API provata** | 15+ anni di utilizzo in produzione |
| **Frattale** | Annidamento infinito con stessa sintassi |
| **Elasticità** | `height=0`, `width=0` risolti automaticamente |
| **Familiare** | Chi conosce Genropy non deve reimparare |
| **Dichiarativo** | L'utente descrive cosa vuole, non come farlo |

### 1.2 Perché ReportLab Diretto

| Vantaggio | Spiegazione |
|-----------|-------------|
| **Performance** | Nessun parsing HTML/CSS |
| **Controllo** | API diretta, pixel-perfect |
| **Dipendenze** | Solo ReportLab (no WeasyPrint + Cairo + Pango) |
| **Funzionalità** | Barcode, QR, grafica vettoriale nativi |

### 1.3 Cosa NON Fare

| Anti-pattern | Problema |
|--------------|----------|
| Usare Table di ReportLab per layout | Non frattale, annidamento difficile |
| Generare HTML poi convertire | Overhead inutile |
| Mescolare costruzione e calcolo | Errore del legacy (vedi [legacy_problems.md](legacy_problems.md)) |

---

## 2. Architettura

### 2.1 Tre Builder Separati

genro-print utilizza **tre builder separati**, ciascuno assemblato da mixin condivisi:

| Builder | Elementi | Compiler | Uso |
|---------|----------|----------|-----|
| **PrintBuilder** | Platypus + Canvas + Charts | PrintCompiler | Report classici |
| **PrintLRCBuilder** | Layout/Row/Cell + Charts | LRCPrintCompiler | Griglie elastiche |
| **PrintStyledBuilder** | Styled shapes + Charts | StyledPrintCompiler | Design posizionale |

Mixin condivisi: `DocumentMixin` e `ChartsMixin` sono gli stessi in tutti i builder.

### 2.2 Diagramma Architetturale

```text
PrintApp              LRCPrintApp           StyledPrintApp
(BuilderManager)      (BuilderManager)      (BuilderManager)
    │                      │                      │
    ▼                      ▼                      ▼
PrintBuilder         PrintLRCBuilder       PrintStyledBuilder
(mixin-composed)     (mixin-composed)      (mixin-composed)
    │                      │                      │
    ▼ build()              ▼ build()              ▼ build()
Built Bag             Built Bag              Built Bag
(^pointer formali)   (^pointer formali)     (^pointer formali)
    │                      │                      │
    ▼ compile()            ▼ compile()            ▼ compile()
PrintCompiler        LRCPrintCompiler      StyledPrintCompiler
(BagCompilerBase)    (BagCompilerBase)     (BagCompilerBase)
    │                      │                      │
    │                  LRCResolver                │
    │                  (elastic dims)             │
    │                      │                      │
    └──────────────────────┼──────────────────────┘
                           ▼
                    ReportLabBackend
                    (shared engine)
                           │
                           ▼
                       PDF bytes
```

---

## 3. Struttura del Codice

```text
src/genro_print/
├── __init__.py
├── print_app.py                    # PrintApp, LRCPrintApp, StyledPrintApp
├── builders/
│   ├── print_builder.py            # PrintBuilder (Platypus + Canvas)
│   ├── print_lrc_builder.py        # PrintLRCBuilder (Layout/Row/Cell)
│   ├── print_styled_builder.py     # PrintStyledBuilder (Styled shapes)
│   └── mixins/
│       ├── document_mixin.py       # document (condiviso)
│       ├── platypus_mixin.py       # paragraph, spacer, pagebreak, image, table
│       ├── canvas_mixin.py         # drawstring, rect, circle, line, etc.
│       ├── styled_mixin.py         # styledblock, statictext, styledrect, etc.
│       ├── lrc_mixin.py            # layout, row, cell
│       └── charts_mixin.py         # bar_chart, pie_chart, line_chart, qrcode (condiviso)
├── compilers/
│   ├── print_compiler.py           # PrintCompiler (BagCompilerBase)
│   ├── lrc_print_compiler.py       # LRCPrintCompiler (BagCompilerBase)
│   ├── styled_print_compiler.py    # StyledPrintCompiler (BagCompilerBase)
│   ├── lrc_resolver.py             # Algoritmo dimensioni elastiche
│   └── reportlab_backend.py        # Motore ReportLab condiviso
├── components/
│   ├── lrc_components.py           # page_template, two_column_row, label_value_row
│   └── styled_components.py        # labeledtext, titled_box
├── computed/
│   └── layout.py                   # ComputedLayout, ComputedRow, ComputedCell
└── utils/
    ├── coordinates.py              # mm-to-points, Y flip
    └── pdf_utils.py                # PyMuPDF utilities (opzionale)
```

---

## 4. Flusso di Esecuzione

### 4.1 Uso tramite App Class (raccomandato)

```python
from genro_print import LRCPrintApp

class InvoiceReport(LRCPrintApp):
    def store(self, data):
        data['company'] = 'Acme Corp'       # dati condivisi
        data['invoice_no'] = 'INV-2025-001'

    def recipe(self, root):
        layout = root.layout(width=210.0, height=297.0, top=10.0, bottom=10.0)

        header = layout.row(height=30.0)
        header.cell(width=60.0, content="Logo")
        header.cell(content="^company")  # data binding con ^pointer

        body = layout.row()  # elastica
        detail = body.cell()
        inner = detail.layout(border_width=0.3)  # layout annidato (frattale)
        inner.row(height=10.0).cell(content="Riga 1")
        inner.row().cell(content="Riga 2")

InvoiceReport().save("invoice.pdf")
```

### 4.2 Lifecycle interno (BuilderManager)

```python
# __init__ esegue automaticamente:
# 1. set_builder('page', PrintLRCBuilder)  → crea builder con compiler registrato
# 2. setup()  → chiama store(data) poi recipe(source)
# 3. build()  → materializza source → built Bag (^pointer restano formali)

# render() esegue:
# 4. page.compile(name='reportlab')  → LRCPrintCompiler.compile(built_bag)
#    4a. LRCResolver.resolve()  → ComputedLayout (dimensioni elastiche risolte)
#    4b. ReportLabBackend.render_layout()  → comandi Canvas
#    4c. ReportLabBackend.finalize()  → PDF bytes
```

---

## 5. LRCResolver (Cuore del Modello LRC)

`LRCResolver` è il componente che risolve le dimensioni elastiche per il modello Layout/Row/Cell.

### 5.1 Input/Output

```python
# Input: Bag con Layout/Row/Cell (sorgente puro)
# Output: ComputedLayout (dimensioni risolte)

@dataclass
class ComputedCell:
    x: float              # coordinata X assoluta (mm)
    y: float              # coordinata Y assoluta (mm)
    computed_width: float  # larghezza calcolata (mm)
    computed_height: float # altezza calcolata (mm)
    border: bool
    border_width: float
    content: str | None
    nested_layout: ComputedLayout | None

@dataclass
class ComputedRow:
    y: float
    computed_height: float
    cells: list[ComputedCell]

@dataclass
class ComputedLayout:
    x: float
    y: float
    width: float
    height: float
    rows: list[ComputedRow]
```

### 5.2 Algoritmo

```python
class DimensionCompiler:
    def compute(self, bag: Bag) -> ComputedLayout:
        layout_node = bag.root
        return self._compute_layout(
            layout_node,
            origin_x=0,
            origin_y=0,
            available_width=layout_node.attr['width'],
            available_height=layout_node.attr['height']
        )

    def _compute_layout(self, node, origin_x, origin_y, available_width, available_height):
        # 1. Calcola area utile
        top = node.attr.get('top', 0)
        bottom = node.attr.get('bottom', 0)
        left = node.attr.get('left', 0)
        right = node.attr.get('right', 0)

        useful_width = available_width - left - right
        useful_height = available_height - top - bottom

        # 2. Prima passata: raccogli info righe
        rows = list(node.children)
        fixed_height = sum(r.attr.get('height', 0) for r in rows if r.attr.get('height', 0) > 0)
        elastic_rows = [r for r in rows if r.attr.get('height', 0) == 0]
        elastic_height = (useful_height - fixed_height) / len(elastic_rows) if elastic_rows else 0

        # 3. Calcola ogni riga
        computed_rows = []
        current_y = origin_y + top

        for row_node in rows:
            row_height = row_node.attr.get('height', 0) or elastic_height

            # Calcola celle della riga
            computed_cells = self._compute_row_cells(
                row_node,
                origin_x + left,
                current_y,
                useful_width,
                row_height
            )

            computed_rows.append(ComputedRow(
                y=current_y,
                computed_height=row_height,
                cells=computed_cells
            ))

            current_y += row_height

        return ComputedLayout(
            x=origin_x,
            y=origin_y,
            width=available_width,
            height=available_height,
            rows=computed_rows
        )

    def _compute_row_cells(self, row_node, origin_x, origin_y, available_width, row_height):
        cells = list(row_node.children)
        fixed_width = sum(c.attr.get('width', 0) for c in cells if c.attr.get('width', 0) > 0)
        elastic_cells = [c for c in cells if c.attr.get('width', 0) == 0]
        elastic_width = (available_width - fixed_width) / len(elastic_cells) if elastic_cells else 0

        computed_cells = []
        current_x = origin_x

        for cell_node in cells:
            cell_width = cell_node.attr.get('width', 0) or elastic_width

            # RICORSIONE per layout annidati
            nested = None
            if cell_node.has_child_layout:
                nested = self._compute_layout(
                    cell_node.nested_layout,
                    current_x,
                    origin_y,
                    cell_width,
                    row_height
                )

            computed_cells.append(ComputedCell(
                x=current_x,
                y=origin_y,
                computed_width=cell_width,
                computed_height=row_height,
                border=cell_node.attr.get('border', False),
                border_width=cell_node.attr.get('border_width', 0),
                content=cell_node.value,
                nested_layout=nested
            ))

            current_x += cell_width

        return computed_cells
```

---

## 6. ReportLabBackend (Motore Condiviso)

### 6.1 Responsabilità

- Motore ReportLab condiviso da tutti e tre i compiler
- Due modalità: Platypus (flowables) e Canvas (disegno diretto)
- Trasformazione coordinate (mm top-left → punti bottom-left)
- Rendering ComputedLayout (per LRC)
- Rendering styled elements (per Styled)
- Rendering grafici (bar_chart, pie_chart, line_chart, qrcode)
- Parsing colori e finalizzazione PDF bytes

### 6.2 Architettura

```python
class ReportLabBackend:
    # Setup
    def set_page(width, height, margins)
    def ensure_canvas() -> Canvas
    def ensure_platypus()
    def finalize() -> bytes

    # Platypus
    def add_paragraph(content, style)
    def add_spacer(width, height)
    def add_pagebreak()
    def add_image(src, width, height)
    def add_table(data, col_widths)

    # Canvas
    def canvas_op(method_name, attrs)  # generic canvas method

    # Styled
    def draw_statictext(x, y, text, align, style)
    def draw_styledrect(x, y, width, height, radius, style)
    def draw_styledcircle(x_cen, y_cen, radius, style)

    # LRC
    def render_layout(computed: ComputedLayout)

    # Charts
    def draw_bar_chart(x, y, width, height, data, ...)
    def draw_pie_chart(...)
    def draw_line_chart(...)
    def draw_qrcode(...)
```

---

## 7. Confronto con Legacy

| Aspetto | Legacy Genropy | genro-print |
|---------|----------------|-------------|
| **Sorgente** | Mescolato con calcoli | Puro (solo dati) |
| **Calcolo dimensioni** | Durante costruzione | In compile() |
| **Stato** | Mutabile | Immutabile |
| **Output primario** | HTML → WeasyPrint | ReportLab via BagCompilerBase |
| **Annidamento** | Funziona ma con bug | Ricorsione pulita |
| **Testabilità** | Difficile | Facile (strutture dati) |

---

## 8. Stato Implementazione

### Completato (v0.2.0)

- [x] Tre builder mixin-composed (PrintBuilder, PrintLRCBuilder, PrintStyledBuilder)
- [x] Tre compiler BagCompilerBase (PrintCompiler, LRCPrintCompiler, StyledPrintCompiler)
- [x] LRCResolver con elasticita' e annidamento frattale
- [x] ReportLabBackend condiviso (platypus, canvas, styled, charts, qrcode)
- [x] App class basate su BuilderManager con data binding `^pointer`
- [x] Componenti @component (page_template, labeledtext, titled_box, etc.)
- [x] ComputedLayout dataclasses
- [x] Bordi con ereditarieta'
- [x] Cell content elements (image, paragraph, spacer)
- [x] PyMuPDF utilities (watermark, merge, preview)

### Da fare

- [ ] Paginazione automatica multi-pagina per LRC
- [ ] Output HTML alternativo (futuro renderer)
- [ ] Test di regressione esaustivi

---

## 9. PyMuPDF (fitz) - Utilities

PyMuPDF è incluso come **dipendenza opzionale** per operazioni di post-processing su PDF.

### 9.1 Perché fitz (non ReportLab)

| Operazione | ReportLab | fitz |
|------------|-----------|------|
| **Watermark su PDF esistente** | Difficile | Nativo |
| **Merge PDF** | Possibile ma verboso | Una riga |
| **PDF → Immagine** | Non supportato | Nativo |
| **Leggere PDF** | Non supportato | Nativo |

### 9.2 Nota Licenza

PyMuPDF è **AGPL**. Per uso commerciale closed-source serve licenza a pagamento.
Le utilities fitz sono **opzionali** - genro-print funziona senza.

### 9.3 API Utilities

```python
from genro_print.utils import PdfUtils

# Watermark su PDF esistente
PdfUtils.add_watermark(
    input_pdf="documento.pdf",
    output_pdf="documento_watermark.pdf",
    text="BOZZA",
    opacity=0.3,
    angle=45
)

# Merge documenti
PdfUtils.merge(
    inputs=["doc1.pdf", "doc2.pdf", "doc3.pdf"],
    output="merged.pdf"
)

# Preview (PDF → immagine)
image = PdfUtils.to_image(
    pdf_path="documento.pdf",
    page=0,
    dpi=150
)

# Aggiungere pagine da un PDF a un altro
PdfUtils.append_pages(
    target="main.pdf",
    source="appendix.pdf",
    pages=[0, 2, 4]  # solo alcune pagine
)
```

### 9.4 Struttura Codice

```text
src/genro_print/
├── utils/
│   ├── __init__.py
│   └── pdf_utils.py      # Wrapper fitz (opzionale)
```

```python
# pdf_utils.py
try:
    import fitz
    FITZ_AVAILABLE = True
except ImportError:
    FITZ_AVAILABLE = False

class PdfUtils:
    @staticmethod
    def add_watermark(input_pdf, output_pdf, text, opacity=0.3, angle=45):
        if not FITZ_AVAILABLE:
            raise ImportError("PyMuPDF required: pip install pymupdf")

        doc = fitz.open(input_pdf)
        for page in doc:
            # Inserisce watermark
            rect = page.rect
            point = fitz.Point(rect.width / 2, rect.height / 2)
            page.insert_text(
                point, text,
                fontsize=72,
                rotate=angle,
                opacity=opacity,
                color=(0.8, 0.8, 0.8)
            )
        doc.save(output_pdf)
```

### 9.5 Dipendenze

```toml
[project.optional-dependencies]
fitz = ["pymupdf>=1.23.0"]

# Installazione
# pip install genro-print[fitz]
```

---

## 10. Conclusione

genro-print combina:

- **Tre builder specializzati** assemblati da mixin condivisi
- **Infrastruttura genro-builders** (BagCompilerBase, BuilderManager, `^pointer`)
- **Separazione sorgente/compilato** corretta (pointer formali risolti just-in-time)
- **ReportLabBackend condiviso** per generazione PDF
- **Componenti @component** con named slots per strutture riutilizzabili
- **PyMuPDF (fitz)** per utilities (watermark, merge, preview)

Il principio guida: **sorgente puro, calcoli in compile(), ricorsione per frattali, infrastruttura genro-builders**.
