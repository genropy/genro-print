# ReportLabBuilder: Specifiche di Implementazione

**Status**: 🔴 DA REVISIONARE
**Data**: 2026-01-27

## Obiettivo

Definire l'architettura del **ReportLabBuilder**, un builder che genera PDF direttamente usando ReportLab, senza passare per HTML/WeasyPrint.

---

## 1. Motivazione

### 1.1 Perché ReportLab Diretto?

| Aspetto | HTML → WeasyPrint | ReportLab Diretto |
|---------|-------------------|-------------------|
| Performance | Lento (parsing HTML + CSS) | Veloce (API diretta) |
| Controllo | Limitato dal CSS | Totale (pixel-perfect) |
| Funzionalità | Solo ciò che CSS supporta | Tutto ReportLab (grafici, forme, etc.) |
| Dipendenze | WeasyPrint + Cairo + Pango | Solo ReportLab |
| Dimensione output | Più grande | Più compatto |

### 1.2 Casi d'Uso

- **Documenti ad alta fedeltà**: fatture, report finanziari
- **Grafica vettoriale**: diagrammi, grafici, schemi
- **Barcode/QRCode**: integrazione nativa
- **Watermark e overlay**: controllo preciso dei layer
- **Performance critica**: generazione massiva di PDF

---

## 2. Architettura

### 2.1 Posizione nel Sistema

```text
Bag (sorgente puro)
    │
    ├── HtmlBuilder      → HTML → WeasyPrint → PDF
    ├── ReportLabBuilder → ReportLab → PDF (diretto)
    ├── PandocBuilder    → Pandoc → vari formati
    └── ExcelBuilder     → openpyxl → XLSX
```

### 2.2 Stesso Sorgente, Output Diverso

```python
# Lo stesso documento può essere compilato con builder diversi
doc = Bag()
layout = doc.layout(width=210, height=297)
row = layout.row(height=20)
row.cell(width=50, content="Titolo")
row.cell(content="Descrizione")

# Output HTML/PDF via WeasyPrint
html_result = HtmlBuilder(doc).compile()

# Output PDF diretto via ReportLab
pdf_result = ReportLabBuilder(doc).compile()
```

---

## 3. Mapping Layout → ReportLab

### 3.1 Concetti Fondamentali

| Layout/Row/Cell | ReportLab Equivalente |
|-----------------|----------------------|
| Layout | Frame o coordinate assolute |
| Row | Posizione Y calcolata |
| Cell | Posizione X calcolata + larghezza |
| Border | `canvas.rect()` o `Table` borders |
| Content | `drawString`, `Paragraph`, `Table` |

### 3.2 Sistema di Coordinate

ReportLab usa coordinate **bottom-left origin** (come PostScript):

```text
ReportLab:                    Layout/Row/Cell:
    ▲ Y                           (0,0)───────► X
    │                               │
    │                               │
    │                               ▼ Y
    └───────► X
  (0,0)
```

Il builder deve **trasformare** le coordinate:

```python
def transform_y(self, y: float, page_height: float) -> float:
    """Converte da top-left a bottom-left origin."""
    return page_height - y
```

### 3.3 Unità di Misura

```python
from reportlab.lib.units import mm, cm, inch

# Layout usa mm di default
# ReportLab accetta qualsiasi unità

def to_points(self, value: float, unit: str = 'mm') -> float:
    """Converte in punti (unità nativa ReportLab)."""
    units = {'mm': mm, 'cm': cm, 'inch': inch, 'pt': 1}
    return value * units.get(unit, mm)
```

---

## 4. Implementazione Compile

### 4.1 Struttura del Builder

```python
class ReportLabBuilder:
    """Builder che genera PDF usando ReportLab direttamente."""

    def __init__(self, bag: Bag):
        self.bag = bag
        self.canvas = None
        self.page_width = 0
        self.page_height = 0

    def compile(self, output: str | BytesIO) -> bytes | None:
        """Compila la Bag in PDF."""
        # 1. Calcola dimensioni (come tutti i builder)
        computed = self._compute_dimensions(self.bag)

        # 2. Crea canvas ReportLab
        self.canvas = canvas.Canvas(output, pagesize=self._get_pagesize())

        # 3. Renderizza ricorsivamente
        self._render_layout(computed)

        # 4. Salva
        self.canvas.save()

        if isinstance(output, BytesIO):
            return output.getvalue()
```

### 4.2 Calcolo Dimensioni (Condiviso)

La logica di calcolo dimensioni elastiche è **identica** per tutti i builder:

```python
def _compute_dimensions(self, bag: Bag) -> ComputedLayout:
    """Calcola dimensioni risolvendo valori elastici.

    Questa logica è COMUNE a tutti i builder.
    Potrebbe essere estratta in una classe base o utility.
    """
    # ... stesso algoritmo di HtmlBuilder ...
```

### 4.3 Rendering Layout

```python
def _render_layout(self, layout: ComputedLayout, origin_x: float = 0, origin_y: float = 0):
    """Renderizza un layout con tutte le sue row e cell."""

    # Coordinate correnti (top-left del layout)
    current_y = origin_y + layout.top

    for row in layout.rows:
        current_x = origin_x + layout.left

        for cell in row.cells:
            # Renderizza cella
            self._render_cell(cell, current_x, current_y)
            current_x += cell.computed_width

        current_y += row.computed_height
```

### 4.4 Rendering Cell

```python
def _render_cell(self, cell: ComputedCell, x: float, y: float):
    """Renderizza una singola cella."""

    # Coordinate ReportLab (bottom-left)
    rl_x = self.to_points(x)
    rl_y = self.transform_y(y + cell.computed_height)
    width = self.to_points(cell.computed_width)
    height = self.to_points(cell.computed_height)

    # Bordo (se richiesto)
    if cell.border:
        self.canvas.rect(rl_x, rl_y, width, height, stroke=1, fill=0)

    # Contenuto
    if cell.has_nested_layout:
        # Ricorsione per layout annidato
        self._render_layout(cell.nested_layout, x, y)
    elif cell.content:
        # Testo semplice o Paragraph
        self._render_content(cell.content, rl_x, rl_y, width, height)
```

---

## 5. Gestione Contenuti Avanzati

### 5.1 Testo con Stili

```python
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet

def _render_paragraph(self, text: str, x: float, y: float, width: float, style_name: str = 'Normal'):
    """Renderizza testo con stili usando Platypus."""
    styles = getSampleStyleSheet()
    style = styles[style_name]

    para = Paragraph(text, style)
    para.wrapOn(self.canvas, width, 1000)  # height arbitrario per wrap
    para.drawOn(self.canvas, x, y)
```

### 5.2 Tabelle (per griglie dati)

```python
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors

def _render_grid(self, data: list[list], x: float, y: float, col_widths: list[float]):
    """Renderizza una griglia dati come Table ReportLab."""
    table = Table(data, colWidths=col_widths)
    table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Header
    ]))
    table.wrapOn(self.canvas, 0, 0)
    table.drawOn(self.canvas, x, y)
```

### 5.3 Immagini

```python
from reportlab.lib.utils import ImageReader

def _render_image(self, image_path: str, x: float, y: float, width: float, height: float):
    """Renderizza un'immagine."""
    img = ImageReader(image_path)
    self.canvas.drawImage(img, x, y, width, height, preserveAspectRatio=True)
```

### 5.4 Barcode/QRCode

```python
from reportlab.graphics.barcode import qr
from reportlab.graphics import renderPDF

def _render_qrcode(self, data: str, x: float, y: float, size: float):
    """Renderizza un QR code."""
    qr_code = qr.QrCodeWidget(data)
    bounds = qr_code.getBounds()
    qr_width = bounds[2] - bounds[0]
    qr_height = bounds[3] - bounds[1]

    from reportlab.graphics.shapes import Drawing
    d = Drawing(size, size, transform=[size/qr_width, 0, 0, size/qr_height, 0, 0])
    d.add(qr_code)
    renderPDF.draw(d, self.canvas, x, y)
```

---

## 6. Paginazione

### 6.1 Page Break Automatico

```python
def _check_page_break(self, required_height: float, current_y: float) -> float:
    """Verifica se serve un page break, lo esegue se necessario."""
    available = self.page_height - current_y - self.margin_bottom

    if required_height > available:
        self.canvas.showPage()
        self._draw_page_template()  # Header/footer se presenti
        return self.margin_top  # Reset Y position

    return current_y
```

### 6.2 Header/Footer Ripetuti

```python
def _draw_page_template(self):
    """Disegna elementi ripetuti su ogni pagina."""
    # Numero pagina
    page_num = self.canvas.getPageNumber()
    self.canvas.drawRightString(
        self.page_width - self.margin_right,
        self.margin_bottom / 2,
        f"Pagina {page_num}"
    )

    # Header custom (se definito nel sorgente)
    if self.header_layout:
        self._render_layout(self.header_layout, 0, 0)
```

---

## 7. Elementi Specifici ReportLab

### 7.1 Elementi Non Disponibili in HTML

Il ReportLabBuilder può supportare elementi che HTML/CSS non gestisce bene:

```python
@element
def watermark(
    self,
    text: str,
    angle: float = 45,
    opacity: float = 0.1,
    font_size: float = 72
):
    """Watermark diagonale sulla pagina."""
    ...

@element
def vector_shape(
    self,
    shape: Literal['rect', 'circle', 'ellipse', 'polygon'],
    **coords
):
    """Forma vettoriale arbitraria."""
    ...

@element
def barcode(
    self,
    data: str,
    barcode_type: Literal['Code128', 'QR', 'EAN13', ...],
    width: float,
    height: float
):
    """Barcode di vario tipo."""
    ...
```

### 7.2 Compatibilità con HtmlBuilder

Per elementi standard (layout, row, cell), il comportamento deve essere **identico** a HtmlBuilder. Gli elementi specifici ReportLab vengono **ignorati** da HtmlBuilder (o generano warning).

---

## 8. Testing

### 8.1 Test Strutturali

```python
def test_layout_dimensions():
    """Verifica che le dimensioni calcolate siano corrette."""
    doc = Bag()
    layout = doc.layout(width=210, height=297)
    layout.row(height=20).cell(width=100)

    builder = ReportLabBuilder(doc)
    computed = builder._compute_dimensions(doc)

    assert computed.rows[0].computed_height == 20
    assert computed.rows[0].cells[0].computed_width == 100
```

### 8.2 Test Output PDF

```python
def test_pdf_generation():
    """Verifica che il PDF venga generato correttamente."""
    doc = Bag()
    layout = doc.layout(width=210, height=297)
    layout.row(height=20).cell(content="Test")

    builder = ReportLabBuilder(doc)
    pdf_bytes = builder.compile(BytesIO())

    # Verifica header PDF
    assert pdf_bytes.startswith(b'%PDF-')
```

### 8.3 Test Comparativo

```python
def test_same_source_different_builders():
    """Verifica che lo stesso sorgente funzioni con entrambi i builder."""
    doc = Bag()
    layout = doc.layout(width=210, height=297)
    row = layout.row(height=20)
    row.cell(width=50, content="A")
    row.cell(content="B")

    # Entrambi devono compilare senza errori
    html = HtmlBuilder(doc).compile()
    pdf = ReportLabBuilder(doc).compile(BytesIO())

    assert html is not None
    assert pdf is not None
```

---

## 9. Dipendenze

```toml
[project.optional-dependencies]
reportlab = [
    "reportlab>=4.0.0",
]
```

Il ReportLabBuilder è **opzionale**: se reportlab non è installato, il builder non è disponibile ma il resto del sistema funziona.

---

## 10. Roadmap Implementazione

1. **Fase 1**: Layout/Row/Cell base con bordi
2. **Fase 2**: Contenuto testuale con stili
3. **Fase 3**: Paginazione automatica
4. **Fase 4**: Elementi avanzati (barcode, immagini, forme)
5. **Fase 5**: Ottimizzazioni performance

---

## 11. Conclusione

Il ReportLabBuilder offre:

- **Output PDF diretto** senza conversione HTML
- **Performance superiori** per generazione massiva
- **Controllo pixel-perfect** sul layout
- **Funzionalità avanzate** non disponibili via CSS
- **Compatibilità sorgente** con gli altri builder

Il principio fondamentale rimane: **sorgente puro, calcoli in compile()**.
