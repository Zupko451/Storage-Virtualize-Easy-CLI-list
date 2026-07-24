# Dynamic Results Columns Plan

## Overview

Enhance the results table in `templates/index.html` so users can:
1. **Drag-and-drop column headers** to reorder columns across all system cards simultaneously.
2. **Toggle column visibility** via a global column picker panel (show/hide any column across all cards).

State resets to defaults on every **Run**. Changes are global — all system cards reflect the same column order and visibility at all times. No backend changes required; this is entirely a frontend enhancement.

---

## Sub-Tasks

---

### Sub-Task 1 — Column State Model

**Intent**
Introduce a client-side state object that tracks the current column order and visibility for the active result set. All rendering reads from this state rather than computing order inline.

**Expected Outcomes**
- A `columnState` object exists after each Run: `{ order: [colIndex, ...], hidden: Set<colIndex> }`
- `renderTable(r)` reads from `columnState` instead of calling `orderColumns()` directly.
- The existing `orderColumns()` logic is used to seed the initial `columnState.order` on Run.
- The existing behavior (preferred columns first, rest appended) is preserved as the default.

**Todo List**
1. Declare a module-level `let columnState = null` variable.
2. In the `run()` function, after receiving results, compute the initial `order` using the existing `orderColumns()` logic applied to the first successful result's columns, and set `columnState = { order, hidden: new Set() }`.
3. Refactor `renderTable(r)` to read `columnState.order` and filter out `columnState.hidden` indices instead of calling `orderColumns()` internally.
4. Ensure `columnState` is reset to `null` (then re-initialized) on each new Run so no stale state leaks between commands.

**Relevant Context**
- [`orderColumns(cols)`](templates/index.html:462) — existing preferred-columns logic to reuse for seeding state.
- [`renderTable(r)`](templates/index.html:469) — currently calls `orderColumns` inline; needs to read from `columnState` instead.
- [`run()`](templates/index.html:413) — the function that triggers result rendering; the right place to initialize `columnState`.
- [`renderResults(data)`](templates/index.html:439) — called by `run()`, passes results to card rendering.

**Status** — `[ ] pending`

---

### Sub-Task 2 — Column Visibility Toggle Panel

**Intent**
Add a "Columns" button in the results bar that opens a compact dropdown panel listing all column names as checkboxes. Checking/unchecking a column instantly re-renders all cards with that column shown or hidden.

**Expected Outcomes**
- A "⚙ Columns" button appears in `.results-bar` next to the Export CSV button (only visible when results are present).
- Clicking it opens a dropdown panel with one checkbox per column, all checked by default.
- Unchecking a column hides it from all system cards immediately (live re-render).
- Re-checking it restores it.
- The panel closes when clicking outside it.
- Panel is only populated/shown after a Run produces results.

**Todo List**
1. Add HTML for the column picker button (`id="colPickerBtn"`) and its dropdown panel (`id="colPickerPanel"`) inside `.results-bar` in the template, hidden by default.
2. Add CSS for the dropdown panel: positioned below the button, scrollable if many columns, checkbox rows with column name labels.
3. Write `buildColPicker(columns)` — populates the panel with one labeled checkbox per column name, wired to toggle `columnState.hidden` and call `rerenderAllCards()`.
4. Write `rerenderAllCards()` — re-renders the `.sc-body` of every `.syscard` in `#resGrid` using the current `lastResults` and updated `columnState`, without rebuilding the card chrome (header, error state).
5. In `renderResults(data)`, call `buildColPicker(columns)` after cards are rendered and show the button.
6. Hide the button and clear the panel when a new Run starts.

**Relevant Context**
- `.results-bar` in HTML ([templates/index.html:228](templates/index.html:228)) — where the button lives alongside Export CSV.
- `lastResults` module variable — holds the result data needed for re-render.
- [`renderCard(r, wide)`](templates/index.html:449) — card chrome (header) should not be rebuilt on re-render; only `.sc-body` content is replaced.
- [`renderTable(r)`](templates/index.html:469) — called per card to produce table HTML; will use updated `columnState` automatically after Sub-Task 1.

**Status** — `[x] done`

---

### Sub-Task 3 — Drag-and-Drop Column Reordering

**Intent**
Make column headers in every `table.data` draggable. Dragging a header and dropping it onto another reorders that column globally (updates `columnState.order`) and immediately re-renders all cards.

**Expected Outcomes**
- Column `<th>` elements have a drag handle cursor and are `draggable`.
- Dragging a header over another highlights the drop target.
- On drop, `columnState.order` is updated by swapping the dragged column index to the target position.
- All cards re-render with the new column order instantly.
- Detail-view cards (attribute/value shape) are unaffected — drag is only active on table-shape results.
- The TOTAL row (capacity sum) correctly reflects the reordered columns after re-render.

**Todo List**
1. In `renderTable(r)`, add `draggable="true"` and `data-colidx` attributes to each `<th>` (only when `r.shape === "table"`).
2. Add CSS for drag states: `th[draggable]:hover` shows a grab cursor; a `.drag-over` class on a `<th>` shows a left-border highlight.
3. In `rerenderAllCards()` (from Sub-Task 2), after injecting new table HTML, attach drag event listeners (`dragstart`, `dragover`, `dragleave`, `drop`) to all `<th>` elements inside `#resGrid`.
4. In the `drop` handler: read the source `data-colidx` and target `data-colidx`, reorder `columnState.order` by moving the source index to the target position, then call `rerenderAllCards()`.
5. Ensure event delegation or re-attachment happens on every re-render (since innerHTML replacement removes old listeners).

**Relevant Context**
- [`renderTable(r)`](templates/index.html:469) — where `<th>` elements are built; add attributes here.
- `rerenderAllCards()` from Sub-Task 2 — the re-render hook; drag listeners attach here after each re-render.
- The `order` array in `columnState` is the source of truth; reordering it moves the column everywhere.
- The TOTAL row uses `order.map((i,k) => ...)` so it naturally follows order changes with no extra work.

**Status** — `[x] done`
