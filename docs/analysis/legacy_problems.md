# Problemi dell'Implementazione Legacy

**Status**: 🔴 DA REVISIONARE
**Data**: 2026-01-27

## Obiettivo

Documentare i problemi architetturali dell'implementazione originale del sistema di stampa Genropy, identificando gli errori da non ripetere in genro-print.

---

## 1. Preprocessing nel Sorgente (ERRORE CRITICO)

L'implementazione attuale **mescola costruzione e compilazione**.

**Fonte**: [`gnrhtml.py:190-227`](gnrpy/gnr/core/gnrhtml.py#L190-L227) - metodi `row()` e `cell()`

```python
# In row() (gnrhtml.py:211-214) - PROBLEMA:
row.border_width = (border_width or layout.border_width) * row.row_border
if height:
    height = height - row.border_width  # ← CALCOLO DURANTE COSTRUZIONE!
row.height = float(height or 0)

# In layout() (gnrhtml.py:172-175) - PROBLEMA:
layout.rowborder_total_height += layout.last_row_border_height  # ← STATO MUTABILE!

# In cell() (gnrhtml.py:247-248) - PROBLEMA:
if not content is None:
    cell.child(tag='div', content=content, ...)  # ← GENERA STRUTTURA!
```

**Conseguenze**:
- Il "sorgente" non è più il sorgente originale
- Impossibile serializzare/deserializzare la ricetta
- Impossibile ricompilare con parametri diversi

---

## 2. Stato Mutabile nel Layout

**Fonte**: [`gnrhtml.py:162-187`](gnrpy/gnr/core/gnrhtml.py#L162-L187) - metodo `layout()`

```python
layout.elastic_rows = []           # Lista che cresce (riga 182)
layout.rowborder_total_height = 0  # Accumulatore (riga 172)
row.elastic_cells = []             # Lista che cresce (riga 223)
row.cellborder_total_width = 0     # Accumulatore (riga 224)
```

Questo stato viene **modificato** durante la costruzione, rendendo impossibile:
- Costruire lo stesso layout due volte
- Clonare un layout
- Calcolare dimensioni "what-if"

---

## 3. Risoluzione Valori Durante Costruzione

**Fonte**: [`gnrbaseclasses.py:187-207`](gnrpy/gnr/web/gnrbaseclasses.py#L187-L207) - classe `GnrTableScriptHtmlSrc`

```python
class GnrTableScriptHtmlSrc(GnrHtmlSrc):
    def cellFromField(self, field=None, width=0, ...):
        # Prende il campo dalla tabella
        colobj = tableScriptInstance.tblobj.column(field)
        content = tableScriptInstance.field(field)  # ← RISOLVE il valore!
        lbl = lbl or colobj.attributes.get('name_long')  # ← RISOLVE la label!

        # Poi chiama cell() standard
        self.cell(content=content, width=width, lbl=lbl, ...)
```

**Problema**: `cellFromField` **risolve** `field` → `content` **durante la costruzione**, non durante compile. Questo significa che:
- Il sorgente contiene già il valore risolto, non il riferimento al campo
- Impossibile ricompilare con dati diversi senza ricostruire

---

## 4. Preprocessing delle Struct (Colonne Griglia)

**Fonte**: [`gnrbaseclasses.py:518-552`](gnrpy/gnr/web/gnrbaseclasses.py#L518-L552) - metodo `gridColumnsFromStruct()`

```python
def gridColumnsFromStruct(self, struct=None):
    grid_columns = []
    for n in cells:
        attr = n.attr
        field = attr.get('caption_field') or attr.get('field')
        field_getter = attr.get('field_getter') or field
        # ... 30 righe di trasformazioni ...
        pars = dict(field=field, name=self.localize(attr.get('name')), ...)  # ← TRADUCE!
        if self.row_table:
            self._calcSqlColumn(pars)  # ← CALCOLA SQL!
        grid_columns.append(pars)
    return grid_columns
```

**Problemi**:
- `self.localize()` traduce durante costruzione (dipende da locale corrente)
- `self._calcSqlColumn()` calcola colonne SQL durante costruzione
- La struct viene **trasformata**, non conservata pura

---

## 5. Mutazione Durante Analisi Multi-Sheet

**Fonte**: [`gnrbaseclasses.py:447-507`](gnrpy/gnr/web/gnrbaseclasses.py#L447-L507) - metodo `structAnalyze()`

```python
def structAnalyze(self, struct, grid_width=None, ...):
    # Calcola se le colonne stanno in una pagina
    min_grid_width = sum([col.mm_width for col in columns])

    # Se non stanno, dividi in sheet
    if extra_space < 0:
        sheet_count = ceil(net_min_grid_width / grid_free_width)
        # Assegna ogni colonna a uno sheet
        for col in columns:
            col['sheet'] = s  # ← MODIFICA la struct direttamente!
```

**Problema**: Modifica direttamente `col['sheet']` nella struct - **stato mutabile durante analisi**. La struct originale viene persa.

---

## 6. Il Sistema Generatore + Callback per Paginazione

**Fonte**: [`gnrbaghtml.py:556-571`](gnrpy/gnr/core/gnrbaghtml.py#L556-L571) - metodo `lineIterator()`

Il cuore del sistema di paginazione è un **generatore** che calcola altezze e decide i page break:

```python
def lineIterator(self, nodes):
    lastNode = nodes[-1]
    for lineno, rowDataNode in enumerate(nodes):
        self.lineno = lineno                          # ← Stato mutabile!
        self.isLastRow = rowDataNode is lastNode      # ← Stato mutabile!
        self.prevDataNode = self.currRowDataNode      # ← Stato mutabile!
        self.currRowDataNode = rowDataNode            # ← Stato mutabile!
        extra_row_height = self.onNewRow() or 0       # ← Callback!
        row_kw = self.getRowAttrsFromData()
        self.updateRunningTotals(rowData=self.rowData) # ← Side effect!
        subtotal_rows = self.checkSubtotals(...)
        rowheight = row_kw.pop('height', None) or self.calcRowHeight()  # ← Callback!
        for copy in range(self.copies_per_page):
            self.copy = copy
            yield (lineno, rowDataNode, rowheight, row_kw, extra_row_height, subtotal_rows)
    self.updateRunningTotals(rowData=None)
```

---

## 7. Il Consumatore del Generatore: mainLoop

**Fonte**: [`gnrbaghtml.py:586-640`](gnrpy/gnr/core/gnrbaghtml.py#L586-L640) - metodo `mainLoop()`

```python
def mainLoop(self):
    # ... setup ...
    carry_height = self.totalizeCarryHeight()
    self.remainingLines = len(nodes)

    for lineno, rowDataNode, rowheight, row_kw, extra_row_height, subtotal_rows in self.lineIterator(nodes):
        bodyUsed = self.copyValue('grid_body_used')   # ← Legge stato accumulato
        self.remainingLines -= 1

        # Calcolo spazio disponibile (con callback!)
        gridNetHeight = self.grid_height - self.calcGridHeaderHeight() - self.calcGridFooterHeight() - \
                        carry_height - self.totalizeFooterHeight() - self.grid_row_height
        availableSpace = gridNetHeight - bodyUsed - self.grid_body_adjustment

        # Calcolo altezza totale riga
        rowTotalHeight = rowheight + extra_row_height + len(subtotal_rows) * rowheight

        # DECISIONE: serve nuova pagina?
        doNewPage = rowTotalHeight > availableSpace

        if doNewPage:
            carry_height = self.totalizeCarryHeight()
            self._newPage()
            self.grid_height = None  # ← Reset per ricalcolo!

        # Accumula spazio usato
        self.copies[self.copykey]['grid_body_used'] = self.copyValue('grid_body_used') + rowTotalHeight
```

---

## 8. Le Callback Overridabili

**Fonte**: [`gnrbaghtml.py:1223-1244`](gnrpy/gnr/core/gnrbaghtml.py#L1223-L1244)

```python
def calcRowHeight(self):
    """override for special needs"""
    return self.grid_row_height

def calcGridHeaderHeight(self):
    """override for special needs"""
    return self.grid_header_height * 2 if self.columnsets else self.grid_header_height

def calcGridFooterHeight(self):
    """override for special needs"""
    return self.grid_footer_height

def calcDocHeaderHeight(self):
    """override for special needs"""
    return self.doc_header_height

def calcDocFooterHeight(self):
    """override for special needs"""
    return self.doc_footer_height
```

---

## 9. Problemi del Pattern Generatore + Callback

### 9.1 Mescolanza di responsabilità

Il generatore fa **tre cose** invece di una:
- Itera sui dati (ok)
- Calcola altezze e subtotali (dovrebbe essere separato)
- Modifica stato globale (side effect!)

### 9.2 Stato mutabile durante iterazione

```python
self.lineno = lineno
self.isLastRow = ...
self.currRowDataNode = rowDataNode
```

Rende impossibile iterare due volte o in parallelo.

### 9.3 Callback intrecciate

```text
mainLoop()
  → lineIterator()
    → onNewRow()
    → calcRowHeight()
    → checkSubtotals()
      → getGridCellValue()
  → calcGridHeaderHeight()
  → totalizeFooterHeight()
  → _newPage()
    → _closePage()
      → fillBodyGrid()
```

### 9.4 Impossibile predire il risultato

Non puoi sapere quante pagine servono senza eseguire tutto il loop con tutti i side effect.

---

## 10. Pattern Corretto: Separazione Calcolo/Rendering

```python
# FASE 1: Calcola paginazione (PURO, nessun side effect)
def compute_pagination(rows, page_config):
    """Restituisce lista di pagine, ogni pagina è lista di righe"""
    pages = []
    current_page = []
    available = page_config.body_height

    for row in rows:
        row_height = row.get('height') or page_config.default_row_height

        if row_height > available:
            # Nuova pagina
            pages.append(current_page)
            current_page = []
            available = page_config.body_height

        current_page.append((row, row_height))
        available -= row_height

    if current_page:
        pages.append(current_page)

    return pages  # Struttura dati immutabile

# FASE 2: Rendering (usa il risultato del calcolo)
def render_pages(pages, template):
    """Genera HTML/PDF dalle pagine pre-calcolate"""
    for page_num, page_rows in enumerate(pages):
        yield render_page(page_rows, page_num, len(pages))
```

**Vantaggi**:
- `compute_pagination()` è **pura**: stesso input → stesso output
- Puoi calcolare il numero di pagine **senza renderizzare**
- Puoi testare la logica di paginazione **in isolamento**
- Nessuno stato globale, nessun side effect

---

## 11. Riepilogo Errori da Evitare

| Errore | Conseguenza | Soluzione |
|--------|-------------|-----------|
| Calcoli durante costruzione | Sorgente corrotto | Tutto in compile() |
| Stato mutabile nel layout | Impossibile clonare | Bag immutabile |
| Risoluzione valori in costruzione | Impossibile ricompilare | Riferimenti, non valori |
| Mutazione struct | Struct originale persa | Copy-on-write |
| Side effect in generatore | Non testabile | Funzioni pure |
| Callback intrecciate | Imprevedibile | Fasi separate |

---

## 12. Fonti

- `gnrpy/gnr/core/gnrhtml.py` - Implementazione GnrHtmlSrc
- `gnrpy/gnr/core/gnrbaghtml.py` - Implementazione BagToHtml
- `gnrpy/gnr/web/gnrbaseclasses.py` - Classi TableScript e estensioni
