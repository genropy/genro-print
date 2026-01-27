# Architettura genro-print

**Status**: 🔴 DA REVISIONARE
**Data**: 2026-01-27

## Decisione Architetturale

genro-print adotta un'architettura a **due livelli**:

1. **API Layout/Row/Cell** - Stesse regole del sistema Genropy legacy
2. **Backend ReportLab** - Generazione PDF diretta (no HTML intermedio)
3. **PyMuPDF (fitz)** - Utilities opzionali (watermark, merge, preview)

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

### 2.1 I Due Builder Principali

genro-print utilizza **due builder distinti** con responsabilità separate:

| Builder | Responsabilità | Input | Output |
|---------|---------------|-------|--------|
| **LRCPrintBuilder** | API Layout/Row/Cell + Calcolo dimensioni | Bag | ComputedLayout |
| **ReportLabBuilder** | Rendering PDF | ComputedLayout | bytes (PDF) |

### 2.2 Diagramma Architetturale

```text
┌─────────────────────────────────────────────────────────────┐
│                     LRCPrintBuilder                         │
│               (Layout / Row / Cell Builder)                 │
│                                                             │
│   Responsabilità:                                           │
│   - Definisce elementi: layout(), row(), cell()             │
│   - Gestisce API utente (stesse regole Genropy)             │
│   - Calcola dimensioni elastiche (height=0, width=0)        │
│   - Propaga bordi (ereditarietà)                            │
│   - Ricorsione per layout annidati (frattale)               │
│                                                             │
│   Input: Bag (sorgente puro)                                │
│   Output: ComputedLayout (coordinate assolute in mm)        │
│                                                             │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    ComputedLayout                           │
│                                                             │
│   Struttura intermedia con valori risolti:                  │
│   - Coordinate assolute (x, y) per ogni elemento            │
│   - Dimensioni calcolate (computed_width, computed_height)  │
│   - Bordi propagati                                         │
│   - Layout annidati già risolti                             │
│                                                             │
└─────────────────────────┬───────────────────────────────────┘
                          │
            ┌─────────────┴─────────────┐
            ▼                           ▼
┌───────────────────────┐   ┌───────────────────────┐
│   ReportLabBuilder    │   │   HtmlBuilder         │
│                       │   │   (futuro)            │
│  ComputedLayout       │   │                       │
│       ↓               │   │  ComputedLayout       │
│  Canvas commands      │   │       ↓               │
│  (rect, drawString)   │   │  HTML + CSS inline    │
│       ↓               │   │       ↓               │
│  PDF diretto          │   │  WeasyPrint → PDF     │
│  PDF                  │   │                       │
└───────────────────────┘   └───────────────────────┘
```

---

## 3. Struttura del Codice

```text
src/genro_print/
├── __init__.py
├── builders/
│   ├── __init__.py
│   ├── lrc.py                 # LRCPrintBuilder (Layout/Row/Cell)
│   └── reportlab.py           # ReportLabBuilder (PDF rendering)
├── computed/
│   ├── __init__.py
│   └── layout.py              # ComputedLayout, ComputedRow, ComputedCell
└── utils/
    ├── __init__.py
    └── pdf_utils.py           # PyMuPDF utilities (opzionale)
```

---

## 4. Flusso di Esecuzione

### 4.1 Costruzione (Utente)

```python
from genro_print import PrintBuilder

doc = Bag(builder=PrintBuilder)

# Costruisce il sorgente - PURO, nessun calcolo
layout = doc.layout(width=210, height=297, top=10, bottom=10, left=10, right=10)

header = layout.row(height=30)
header.cell(width=60, content="Logo")
header.cell(content="FATTURA N. 123")  # elastica

body = layout.row()  # elastica
detail = body.cell()
# Layout annidato - FRATTALE
inner = detail.layout(border_width=0.3)
inner.row(height=10).cell(content="Riga 1")
inner.row().cell(content="Riga 2")  # elastica
```

### 4.2 Compilazione (Sistema)

```python
# Opzione 1: PDF via ReportLab (raccomandato)
from genro_print.builders import ReportLabBuilder

builder = ReportLabBuilder(doc)
pdf_bytes = builder.compile()

# Opzione 2: PDF via HTML + WeasyPrint
from genro_print.builders import HtmlBuilder

builder = HtmlBuilder(doc)
html = builder.compile()
# poi WeasyPrint per PDF
```

### 4.3 Internamente

```python
class ReportLabBuilder:
    def compile(self, output=None):
        # 1. Calcola dimensioni (codice condiviso)
        computed = DimensionCompiler().compute(self.bag)

        # 2. Genera comandi ReportLab
        commands = self._generate_commands(computed)

        # 3. Esegui su canvas
        canvas = Canvas(output or BytesIO())
        self._execute(canvas, commands)
        canvas.save()

        return output.getvalue() if output else None
```

---

## 5. DimensionCompiler (Cuore del Sistema)

Il `DimensionCompiler` è il componente centrale, **condiviso tra tutti i builder**.

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

## 6. ReportLabBuilder

### 6.1 Responsabilità

- Riceve `ComputedLayout` dal `DimensionCompiler`
- Traduce in chiamate ReportLab Canvas
- Gestisce trasformazione coordinate (top-left → bottom-left)
- Gestisce paginazione (page break)

### 6.2 Implementazione Core

```python
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm

class ReportLabBuilder:
    def __init__(self, bag: Bag):
        self.bag = bag
        self.page_height = 297 * mm  # A4 default

    def compile(self, output=None):
        # 1. Calcola dimensioni
        computed = DimensionCompiler().compute(self.bag)

        # 2. Crea canvas
        out = output or BytesIO()
        c = canvas.Canvas(out, pagesize=(computed.width * mm, computed.height * mm))
        self.page_height = computed.height * mm

        # 3. Renderizza
        self._render_layout(c, computed)

        # 4. Salva
        c.save()
        return out.getvalue() if isinstance(out, BytesIO) else None

    def _render_layout(self, c, layout: ComputedLayout):
        for row in layout.rows:
            for cell in row.cells:
                self._render_cell(c, cell)

    def _render_cell(self, c, cell: ComputedCell):
        # Coordinate ReportLab (Y invertita)
        x = cell.x * mm
        y = self.page_height - (cell.y + cell.computed_height) * mm
        w = cell.computed_width * mm
        h = cell.computed_height * mm

        # Bordo
        if cell.border:
            c.setStrokeColor('black')
            c.setLineWidth(cell.border_width * mm)
            c.rect(x, y, w, h, stroke=1, fill=0)

        # Contenuto o ricorsione
        if cell.nested_layout:
            self._render_layout(c, cell.nested_layout)
        elif cell.content:
            # Testo (semplificato - TODO: Paragraph per wrap)
            c.drawString(x + 2*mm, y + h/2, cell.content)
```

---

## 7. Confronto con Legacy

| Aspetto | Legacy Genropy | genro-print |
|---------|----------------|-------------|
| **Sorgente** | Mescolato con calcoli | Puro (solo dati) |
| **Calcolo dimensioni** | Durante costruzione | In compile() |
| **Stato** | Mutabile | Immutabile |
| **Output primario** | HTML → WeasyPrint | ReportLab diretto |
| **Annidamento** | Funziona ma con bug | Ricorsione pulita |
| **Testabilità** | Difficile | Facile (strutture dati) |

---

## 8. Roadmap Implementazione

### Fase 1: Core
- [ ] `DimensionCompiler` con elasticità base
- [ ] `ComputedLayout` dataclasses
- [ ] `ReportLabBuilder` minimale (rect + text)
- [ ] Test unitari

### Fase 2: Completezza
- [ ] Bordi (ereditarietà, selettivi)
- [ ] Label nelle celle
- [ ] Paginazione automatica

### Fase 3: Contenuti
- [ ] Paragraph (testo con wrap)
- [ ] Immagini
- [ ] Barcode/QRCode

### Fase 4: HtmlBuilder
- [ ] Output HTML alternativo
- [ ] Test comparativi (stesso layout → stesso output)

### Fase 5: PyMuPDF Utilities
- [ ] Watermark su PDF esistenti
- [ ] Merge documenti
- [ ] PDF → immagine (preview)

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

- **API Layout/Row/Cell** provata e familiare
- **Separazione sorgente/compilato** corretta
- **Backend ReportLab** per generazione PDF
- **PyMuPDF (fitz)** per utilities (watermark, merge, preview)
- **Architettura estensibile** per futuri builder

Il principio guida: **sorgente puro, calcoli in compile(), ricorsione per frattali**.
