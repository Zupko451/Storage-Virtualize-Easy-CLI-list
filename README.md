# IBM Storage Virtualize — Easy List

A simple web tool for junior admins to pull information from IBM Storage Virtualize /
FlashSystem / SVC systems **without memorizing CLI commands**.

- 🔍 **Search in plain English** — type *"show all volumes"*, *"capacity of all volumes"*,
  *"list pools"*, *"list hosts"* and it runs the right `ls*` command for you.
- 🖥️ **One or many systems** — enter an IP, username, password and port. Add more systems and,
  by default, reuse the same credentials; or switch on **unique credentials** to give each system
  its own login.
- 📊 **Readable, formatted output** — raw `lsvdisk` output is dense and hard to read; this renders
  a clean table with **humanized capacities** (GB/TB), **colored status chips**, and a **totals row**.
- ↔️ **Side-by-side comparison** — every system shows in its own card so you can compare values.
- 🔀 **Drag-to-reorder columns and rows** — grab any column header to drag it left or right; grab
  the grip handle (⠿) on any row to reorder it. While dragging, the table auto-scrolls when the
  pointer nears an edge so off-screen columns and rows are always reachable.
- 🖱️ **Pan the results area** — click and drag anywhere in the results area (not on a header or
  grip) to scroll the entire card view left or right.
- ⧉ **Apply column order to all cards** — the *Apply to all* button in each card's header mirrors
  that card's current column order across every system shown in the same run. *Reset* restores the
  original layout (and clears the remembered order).
- 💾 **Persistent column preference** — column order is saved to `localStorage` keyed by command
  name. Re-running the same query picks up where you left off. *Reset* clears the saved preference.
- 🔒 **Read-only & safe** — only `ls*` (list) commands are ever sent; passwords stay in memory and
  are never written to disk. Saved host profiles keep IP/username/port only.

## Install & run

```bash
cd svc-list-tool
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

.venv/bin/python app.py
```

Then open **http://localhost:5000** in your browser.

Options: `--port 8080`, `--host 0.0.0.0`.

## Standalone offline file

A single self-contained `standalone.html` can be generated and opened from the
desktop with no server, no Python, and no install. It uses bundled demo data for
all queries — real SSH connections are not available in this mode.

```bash
.venv/bin/python build_standalone.py        # writes standalone.html
# then just double-click standalone.html
```

The file is a build artifact — regenerate it any time you update the catalog in
`queries.py`. It is git-ignored.

**Limitations vs the server-backed tool:**

| Feature | Server-backed | Standalone |
|---|---|---|
| Real array connections | ✅ | ❌ (demo data only) |
| All 35 catalog queries | ✅ | ✅ |
| Search, drag-reorder, CSV export | ✅ | ✅ |
| Save hosts (profiles.json) | ✅ | ❌ (button hidden) |

## How to use

1. **Systems & login** — enter username / password / port (default `22`). Add each system's IP.
   Leave *"Use the same credentials for all systems"* checked to reuse one login, or uncheck it to
   enter a different username/password/port per system. **Save hosts** stores the IPs for next time
   (never the password).
2. **What do you want to see?** — start typing; pick a suggestion. The exact CLI command it will run
   is shown for transparency. Need something not listed? Open **Advanced** and type any `ls*` command
   (autocompletes from the full command set).
3. Press **Run**. Each system appears as its own card. Use **Export CSV** to save the combined data.

### Results table interactions

| Interaction | How |
|---|---|
| **Reorder columns** | Drag any column header left or right. Drop on either the header row or anywhere in the table body — the nearest column is highlighted as the target. While dragging, the table auto-scrolls when the pointer nears an edge. |
| **Reorder rows** | Mousedown on the ⠿ grip handle on the left of any row, then drag up or down. Auto-scroll also applies near the top/bottom edges. |
| **Pan cards left/right** | Click and drag anywhere in the results area (not on a header or grip) — the cursor becomes a hand and the entire results view scrolls horizontally. |
| **Reset layout** | Click **↺ Reset** in the card header — restores the original server-returned order and clears the remembered column preference for that command. |
| **Mirror to all** | Click **⧉ Apply to all** in the card header — copies that card's current column order to every other system card shown, and saves it for future runs of the same command. |
| **Export CSV** | Click **⬇ Export CSV** (appears after a successful run) — downloads one CSV file containing all visible systems; rows are in the current drag-reordered sequence and column headers use the current drag-reordered names. |

## How it works

- Connects over **SSH** (paramiko) and runs the command with `-delim |` so output parses cleanly.
- Auto-detects the two output shapes: multi-object **tables** (e.g. `lsvdisk`) and single-object
  **detail** views (e.g. `lssystem`).
- The plain-English catalog lives in [`queries.py`](queries.py) — easy to extend with more phrases.
- Column/row drag uses the HTML5 Drag and Drop API. The model (`colOrder` / `rowOrder` index arrays
  in `cardState`) is the single source of truth — it drives rendering, CSV export, Reset, and Apply-to-all.
- **Edge auto-scroll** (`edgeAutoScroll`) activates during any drag: when the pointer enters a 52 px
  band near any edge of the card's scroll body, the table scrolls automatically toward that edge so
  off-screen columns and rows are always reachable without ending the drag.
- **Results pan** uses a separate `mousedown/mousemove/mouseup` listener on `.res-scroll`. Dragging
  outside headers and grip handles scrolls the whole results area horizontally via `requestAnimationFrame`.
- Preferred column order is persisted per command name in `localStorage` (key `svc-colorder:<cmd>`).

## Security notes

- **Read-only:** the backend rejects anything that isn't a single `ls*` command (no `mk*`, `ch*`,
  `rm*`, `svctask`, shell metacharacters, etc.).
- **Passwords** are used only for the live SSH call and are never persisted or logged.
- Host keys are auto-accepted (`AutoAddPolicy`) for ease of first use. On untrusted networks,
  verify the system's SSH fingerprint out of band before connecting.
- Serves on `127.0.0.1` by default. Only use `--host 0.0.0.0` on a trusted network.

## Files

| File | Purpose |
|------|---------|
| `app.py` | Flask backend + JSON API (`/api/queries`, `/api/run`, `/api/profiles`) |
| `svc_client.py` | SSH execution, command validation, output parsing, capacity/status formatting |
| `queries.py` | Plain-English query catalog + full `ls*` command list |
| `templates/index.html` | Single-page UI — search, system management, results with drag-to-reorder tables |
| `build_standalone.py` | Generates `standalone.html` from the catalog + demo data |
| `standalone.html` | Generated standalone file (build artifact; git-ignored) |
| `profiles.json` | Saved hosts (created at runtime; IP/user/port only — git-ignored) |
