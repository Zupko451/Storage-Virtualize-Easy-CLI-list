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
- ↔️ **Side-by-side comparison** — every system shows in its own column so you can compare values.
- 🔀 **Dynamic column control** — drag any column header left or right to reorder it across all
  cards at once. Use the **⚙ Columns** picker to hide columns you don't care about, giving you a
  focused view of only the attributes you need.
- 🔒 **Read-only & safe** — only `ls*` (list) commands are ever sent; passwords stay in memory and
  are never written to disk. Saved host profiles keep IP/username/port only.

## Install & run

```bash
cd svc-list-tool
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# Normal mode (connects to real systems over SSH):
.venv/bin/python app.py

# Try it with no hardware, using bundled sample output:
.venv/bin/python app.py --demo
```

Then open **http://localhost:5000** in your browser.

Options: `--port 8080`, `--host 0.0.0.0`, `--demo`.


## Windows:
Step	README      Windows
Create venv	      python -m venv .venv
Install deps		  .venv\Scripts\pip install -r requirements.txt
Run App           .venv\Scripts\python app.py

---

## How to use

1. **Systems & login** — enter username / password / port (default `22`). Add each system's IP.
   Leave *"Use the same credentials for all systems"* checked to reuse one login, or uncheck it to
   enter a different username/password/port per system. **Save hosts** stores the IPs for next time
   (never the password).
2. **What do you want to see?** — start typing; pick a suggestion. The exact CLI command it will run
   is shown for transparency. Need something not listed? Open **Advanced** and type any `ls*` command
   (autocompletes from the full command set).
3. Press **Run**. Each system appears as its own card.
   - **Reorder columns** — drag any column header and drop it onto another to swap their positions.
     The change applies to all system cards simultaneously.
   - **Hide/show columns** — click **⚙ Columns** (top-right of the results area) to open a checklist.
     Uncheck any column to hide it; check it again to bring it back. All cards update instantly.
   - **Export CSV** saves the full data (all columns, all systems) regardless of which columns are
     currently hidden in the view.

## How it works

- Connects over **SSH** (paramiko) and runs the command with `-delim |` so output parses cleanly.
- Auto-detects the two output shapes: multi-object **tables** (e.g. `lsvdisk`) and single-object
  **detail** views (e.g. `lssystem`).
- The plain-English catalog lives in [`queries.py`](queries.py) — easy to extend with more phrases.

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
| `templates/index.html` | Single-page UI |
| `profiles.json` | Saved hosts (created at runtime; IP/user/port only — git-ignored) |
