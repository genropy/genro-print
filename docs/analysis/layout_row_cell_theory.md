# Layout/Row/Cell: Analisi Teorica

**Status**: 🔴 DA REVISIONARE
**Data**: 2026-01-27

## Obiettivo

Analizzare in astratto il modello **Layout → Row → Cell** di Genropy per:

1. Comprenderne i principi teorici
2. Identificare punti di forza e debolezze
3. Definire come reimplementarlo correttamente in genro-print

---

## 1. Il Modello Concettuale

### 1.1 Gerarchia Strutturale

```text
Layout (contenitore 2D con margini)
├── Row (banda orizzontale con altezza)
│   ├── Cell (porzione di riga con larghezza)
│   │   └── [contenuto | Layout annidato]
│   ├── Cell
│   └── Cell
├── Row
│   └── Cell
│       └── Layout (annidato!)
│           ├── Row
│           └── Row
└── Row
```

### 1.2 Regole di Composizione

| Elemento | Può contenere      | Contenuto in        |
|----------|--------------------|---------------------|
| Layout   | solo Row           | Cell oppure root    |
| Row      | solo Cell          | Layout              |
| Cell     | Layout o contenuto | Row                 |

**Invariante fondamentale**: La ricorsione avviene SOLO attraverso Cell → Layout.

### 1.3 Analogia con HTML/CSS

```text
Layout  ≈  <div> con display:grid o position:relative
Row     ≈  <div> con display:flex; flex-direction:row
Cell    ≈  <div> con width fissa o flex
```

Ma con una differenza cruciale: **le dimensioni sono in unità fisiche (mm)**, non relative.

---

## 2. Sistema di Dimensionamento

### 2.1 Unità di Misura

```python
um = 'mm'  # Unità di misura (millimetri di default)
```

Il sistema è progettato per la **stampa**, quindi usa millimetri come unità base. Questo garantisce che il layout sia identico su qualsiasi dispositivo/stampante.

### 2.2 Layout: Margini e Area Utile

```text
┌─────────────────────────────────────┐
│              top                    │
│  ┌─────────────────────────────┐    │
│  │                             │    │
│l │       AREA UTILE            │ r  │
│e │    (per le Row)             │ i  │
│f │                             │ g  │
│t │                             │ h  │
│  │                             │ t  │
│  └─────────────────────────────┘    │
│             bottom                  │
└─────────────────────────────────────┘
```

```python
# Parametri del Layout
layout(
    width=210,      # Larghezza totale (o 0 = eredita)
    height=297,     # Altezza totale (o 0 = eredita)
    top=10,         # Margine superiore
    bottom=10,      # Margine inferiore
    left=10,        # Margine sinistro
    right=10,       # Margine destro
    um='mm'         # Unità di misura
)
```

**Area utile** = `(width - left - right)` × `(height - top - bottom)`

### 2.3 Row: Altezza Fissa o Elastica

```python
row(height=20)   # Altezza fissa: 20mm
row(height=0)    # Altezza elastica: si espande per riempire
```

**Regola di distribuzione verticale**:

1. Somma le altezze fisse di tutte le Row
2. Calcola lo spazio rimanente
3. Distribuisci equamente tra le Row elastiche (height=0)

```text
Layout (height=100, top=10, bottom=10)  → Area utile: 80mm
├── Row (height=20)  → 20mm fissi
├── Row (height=0)   → elastica
├── Row (height=30)  → 30mm fissi
└── Row (height=0)   → elastica

Spazio fisso: 20 + 30 = 50mm
Spazio elastico: 80 - 50 = 30mm
Ogni row elastica: 30 / 2 = 15mm
```

### 2.4 Cell: Larghezza Fissa o Elastica

```python
cell(width=50)   # Larghezza fissa: 50mm
cell(width=0)    # Larghezza elastica: si espande
```

**Regola di distribuzione orizzontale** (identica a Row ma sull'asse X):

1. Somma le larghezze fisse di tutte le Cell nella Row
2. Calcola lo spazio rimanente
3. Distribuisci equamente tra le Cell elastiche

```text
Row (in Layout con area utile larga 180mm)
├── Cell (width=40)  → 40mm fissi
├── Cell (width=0)   → elastica
└── Cell (width=60)  → 60mm fissi

Spazio fisso: 40 + 60 = 100mm
Spazio elastico: 180 - 100 = 80mm
La cell elastica: 80mm
```

---

## 3. Sistema dei Bordi

### 3.1 Bordi come Proprietà Ereditata

```python
layout(border_width=0.3, border_color='#e0e0e0')
    row(row_border=True)      # Eredita border dal layout
        cell(cell_border=True)  # Eredita border dalla row
```

I bordi sono **sottratti** dalle dimensioni utili:

- Una Row con `height=20` e `border_width=0.3` ha area utile di `19.7mm`
- Una Cell con `width=50` e `border_width=0.3` ha area utile di `49.7mm`

### 3.2 Bordi Selettivi

```python
layout(
    hasBorderTop=True,
    hasBorderBottom=True,
    hasBorderLeft=False,
    hasBorderRight=False
)
```

---

## 4. Sistema delle Label

### 4.1 Cell con Label

Una Cell può avere una **label** (etichetta) sopra il contenuto:

```text
┌─────────────────┐
│ lbl_class       │ ← lbl_height (es: 3mm)
├─────────────────┤
│                 │
│ content_class   │ ← resto dell'altezza
│                 │
└─────────────────┘
```

```python
cell(
    content="Valore",
    lbl="Etichetta",
    lbl_height=3,
    lbl_class='caption',
    content_class='value'
)
```

---

## 5. Annidamento (Nesting)

### 5.1 Layout dentro Cell

```python
layout = page.layout(...)
row = layout.row(height=50)
cell = row.cell(width=100)

# Layout annidato!
inner_layout = cell.layout(...)
inner_row = inner_layout.row(...)
inner_cell = inner_row.cell(...)
```

### 5.2 Contesto di Annidamento

Il layout annidato:

- **Eredita** l'area della Cell contenitrice come suo spazio totale
- **NON eredita** automaticamente margini o bordi
- È **completamente indipendente** nel suo sistema di coordinate

---

## 6. Modello Corretto: Separazione Sorgente/Compilato

### 6.1 Fase 1: Costruzione (Sorgente Puro)

```python
# L'utente costruisce la Bag - SOLO DATI DICHIARATIVI
doc = Bag(builder=PrintBuilder)

layout = doc.layout(width=210, height=297, top=10, bottom=10, left=10, right=10)
row1 = layout.row(height=20)
row1.cell(width=50, content="Titolo")
row1.cell(content="Descrizione")  # width=0 implicito

row2 = layout.row()  # height=0 implicito (elastica)
cell = row2.cell(width=100)
# Layout annidato
inner = cell.layout(border_width=0.3)
inner.row(height=10).cell(content="Nested")
```

**La Bag contiene SOLO**:

```text
layout[width=210, height=297, top=10, bottom=10, left=10, right=10]
├── row[height=20]
│   ├── cell[width=50] = "Titolo"
│   └── cell[] = "Descrizione"
└── row[]
    └── cell[width=100]
        └── layout[border_width=0.3]
            └── row[height=10]
                └── cell[] = "Nested"
```

Nessun calcolo, nessuno stato derivato, nessuna struttura generata.

### 6.2 Fase 2: Compilazione (Calcolo e Rendering)

```python
html = doc.builder.compile()
```

**Durante compile()**:

1. **Calcola dimensioni elastiche** (risolvi height=0 e width=0)
2. **Sottrai bordi** dalle dimensioni
3. **Genera CSS** per ogni elemento
4. **Genera HTML** con le dimensioni calcolate

```python
def compile(self):
    # 1. Prima passata: raccogli info
    elastic_rows = []
    fixed_height = 0
    for row in layout.children:
        if row.attr.get('height', 0) == 0:
            elastic_rows.append(row)
        else:
            fixed_height += row.attr['height']

    # 2. Calcola spazio elastico
    available = layout.attr['height'] - layout.attr['top'] - layout.attr['bottom']
    elastic_space = available - fixed_height
    elastic_height = elastic_space / len(elastic_rows) if elastic_rows else 0

    # 3. Genera HTML con dimensioni risolte
    # ...
```

### 6.3 Vantaggi della Separazione

| Aspetto         | Vecchio (mescolato)  | Nuovo (separato)      |
|-----------------|----------------------|-----------------------|
| Serializzazione | ❌ Impossibile       | ✅ Bag standard       |
| Ricompilazione  | ❌ Stato corrotto    | ✅ Sempre possibile   |
| Clonazione      | ❌ Stato condiviso   | ✅ Bag immutabile     |
| Testing         | ❌ Dipende da ordine | ✅ Deterministico     |
| Debug           | ❌ Stato nascosto    | ✅ Sorgente leggibile |

---

## 7. Schema per PrintBuilder

### 7.1 Elementi

```python
@element(sub_tags='row')
def layout(
    self,
    width: float = 0,      # 0 = eredita da parent
    height: float = 0,     # 0 = eredita da parent
    top: float = 0,
    bottom: float = 0,
    left: float = 0,
    right: float = 0,
    um: str = 'mm',
    border_width: float = 0,
    border_color: str = 'silver',
    border_style: str = 'solid'
): ...

@element(sub_tags='cell')
def row(
    self,
    height: float = 0,     # 0 = elastica
    border: bool = None,   # None = eredita da layout
): ...

@element(sub_tags='layout,@inline')  # può contenere layout annidato o contenuto
def cell(
    self,
    node_value: str = '',  # contenuto testuale
    width: float = 0,      # 0 = elastica
    border: bool = None,   # None = eredita da row
    lbl: str = None,
    lbl_height: float = 0,
    lbl_class: str = None,
    content_class: str = None
): ...
```

### 7.2 Compile: Algoritmo

```text
compile(layout_node, context):
    1. Risolvi dimensioni del layout
       - Se width=0 e in Cell: width = cell.computed_width
       - Se height=0 e in Cell: height = cell.computed_height

    2. Calcola area utile
       - useful_width = width - left - right
       - useful_height = height - top - bottom

    3. Prima passata sulle Row: raccogli info
       - fixed_heights = sum(row.height for row where height > 0)
       - elastic_rows = [row for row where height == 0]
       - border_heights = sum(border_width for each row)

    4. Calcola altezze elastiche
       - remaining = useful_height - fixed_heights - border_heights
       - elastic_height = remaining / len(elastic_rows)

    5. Per ogni Row:
       - computed_height = row.height or elastic_height
       - Ripeti logica simile per le Cell (larghezze)
       - Per ogni Cell con layout annidato: ricorsione

    6. Genera HTML/CSS con dimensioni computed
```

---

## 8. Domande Aperte

1. **Overflow**: Cosa succede se le celle fisse superano lo spazio disponibile?
2. **Percentuali**: Supportare `width="50%"` oltre ai mm?
3. **Min/Max**: Supportare `min_height`, `max_width`?
4. **Allineamento**: Dentro la Cell, il contenuto può essere allineato?

---

## 9. Conclusione

Il modello Layout/Row/Cell è **solido concettualmente**:

- Gerarchia chiara e predicibile
- Sistema di dimensionamento coerente (fisso + elastico)
- Annidamento potente ma controllato

L'errore dell'implementazione originale è stato **mescolare costruzione e compilazione**.

La nuova implementazione in genro-print deve:

1. **Mantenere il sorgente puro** (solo dati dichiarativi)
2. **Calcolare tutto in compile()** (dimensioni, bordi, CSS)
3. **Non mutare mai la Bag** durante la compilazione
