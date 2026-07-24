"""SSH connection, command execution and output parsing for IBM Storage
Virtualize systems.

Design notes
------------
* Connections use SSH (paramiko). Storage Virtualize presents a restricted CLI
  on login (not a general shell), so an executed command goes straight to that
  CLI. We still hard-validate that only read-only ``ls*`` commands are sent.
* We append ``-delim |`` so concise output is cleanly delimited. ``|`` is used
  (rather than ``:``) because colons appear inside IPv6 addresses and some
  values, while ``|`` effectively never does.
* Output comes in two shapes:
    - "table"  : concise multi-object view. First line is the header row.
    - "detail" : single-object view. Every line is ``attribute|value``.
  We detect the shape from a small known set plus a structural fallback.
"""

from __future__ import annotations

import re
import shlex

try:
    import paramiko
except ImportError:  # allows --demo / tests without paramiko installed
    paramiko = None

DELIM = "|"
DEFAULT_TIMEOUT = 20

# Commands that return a single-object (attribute/value) detailed view.
DETAILED_COMMANDS = {
    "lssystem", "lssystemstats", "lssystemcapacity", "lssystemlimits",
    "lscurrentuser", "lssecurity", "lsencryption", "lscloudcallhome",
}

_VALID_CMD = re.compile(r"^ls[a-z0-9_]{1,40}$")
_CAP_RE = re.compile(r"^\s*([0-9]+(?:\.[0-9]+)?)\s*(PB|TB|GB|MB|KB|B)?\s*$", re.I)
_UNIT_FACTOR = {
    "B": 1, "KB": 1024, "MB": 1024 ** 2, "GB": 1024 ** 3,
    "TB": 1024 ** 4, "PB": 1024 ** 5,
}


class CommandError(ValueError):
    """Raised when a command is not an allowed read-only ls* command."""


def sanitize_command(raw: str) -> str:
    """Validate and normalize a user-supplied command.

    Only a single ``ls*`` command with plain option arguments is allowed. Any
    shell metacharacters (``; | & $ ` > <`` newlines, etc.) are rejected so the
    tool can never be used to run a mutating or chained command.
    """
    if raw is None:
        raise CommandError("No command provided.")
    cmd = raw.strip()
    if not cmd:
        raise CommandError("No command provided.")
    if any(ch in cmd for ch in ";|&$`><\n\r\\"):
        raise CommandError("Command contains disallowed characters.")
    try:
        parts = shlex.split(cmd)
    except ValueError as exc:
        raise CommandError(f"Could not parse command: {exc}") from exc
    if not parts:
        raise CommandError("No command provided.")
    base = parts[0]
    # allow an optional leading 'svcinfo'
    if base == "svcinfo":
        parts = parts[1:]
        base = parts[0] if parts else ""
    if not _VALID_CMD.match(base):
        raise CommandError(
            f"'{base}' is not allowed. This tool only runs read-only 'ls' "
            "commands (e.g. lsvdisk, lsmdiskgrp, lshost)."
        )
    return " ".join(parts)


def _with_delim(cmd: str) -> str:
    # The delimiter is single-quoted because Storage Virtualize runs the CLI
    # inside a restricted shell (rbash): an unquoted '|' would be read as a
    # shell pipe ("syntax error: unexpected end of file"). Quoting makes the
    # shell pass the literal character to the command. Single quotes are also
    # harmless in csh, so this is safe across shells.
    return cmd if "-delim" in cmd else f"{cmd} -delim '{DELIM}'"


def _base_command(cmd: str) -> str:
    parts = cmd.split()
    if parts and parts[0] == "svcinfo":
        parts = parts[1:]
    return parts[0] if parts else ""


# --------------------------------------------------------------------------- #
# Parsing
# --------------------------------------------------------------------------- #
def parse_output(raw: str, base_cmd: str = "") -> dict:
    """Turn raw delimited CLI text into {shape, columns, rows}."""
    lines = [ln.rstrip("\r") for ln in raw.split("\n")]
    lines = [ln for ln in lines if ln.strip() != ""]
    if not lines:
        return {"shape": "empty", "columns": [], "rows": []}

    split = [ln.split(DELIM) for ln in lines]

    detail = base_cmd in DETAILED_COMMANDS
    if not detail:
        # Structural fallback: every line has exactly 2 fields and the first
        # column values are all unique -> looks like an attribute/value dump.
        if all(len(s) == 2 for s in split) and len(split) >= 3:
            firsts = [s[0] for s in split]
            if len(set(firsts)) == len(firsts):
                detail = True

    if detail:
        rows = [[s[0], DELIM.join(s[1:])] for s in split]
        return {"shape": "detail", "columns": ["Attribute", "Value"], "rows": rows}

    header = split[0]
    ncols = len(header)
    rows = []
    for s in split[1:]:
        if len(s) < ncols:
            s = s + [""] * (ncols - len(s))
        elif len(s) > ncols:
            # extra delimiters inside the last field: re-join the overflow
            s = s[: ncols - 1] + [DELIM.join(s[ncols - 1:])]
        rows.append(s)
    return {"shape": "table", "columns": header, "rows": rows}


# --------------------------------------------------------------------------- #
# Capacity / formatting helpers (also used by tests and demo mode)
# --------------------------------------------------------------------------- #
def parse_capacity(value: str):
    """Parse '10.00GB' / '3.00TB' / '512' into bytes (int), or None."""
    if value is None:
        return None
    m = _CAP_RE.match(str(value))
    if not m:
        return None
    num = float(m.group(1))
    unit = (m.group(2) or "B").upper()
    return int(num * _UNIT_FACTOR[unit])


def humanize_bytes(n) -> str:
    if n is None:
        return ""
    n = float(n)
    for unit in ("B", "KB", "MB", "GB", "TB", "PB"):
        if abs(n) < 1024 or unit == "PB":
            if unit == "B":
                return f"{int(n)} B"
            return f"{n:.2f} {unit}"
        n /= 1024
    return f"{n:.2f} PB"


# --------------------------------------------------------------------------- #
# SSH execution
# --------------------------------------------------------------------------- #
def run_command(ip, username, password, command, port=22,
                timeout=DEFAULT_TIMEOUT) -> dict:
    """Run one ls* command against one system. Never raises for connection
    problems; returns a dict with ok=False and an error message instead."""
    try:
        clean = sanitize_command(command)
    except CommandError as exc:
        return _err(str(exc))

    if paramiko is None:
        return _err("paramiko is not installed (run: pip install -r requirements.txt).")

    base = _base_command(clean)
    full = _with_delim(clean)

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(
            hostname=ip, port=int(port), username=username, password=password,
            timeout=timeout, banner_timeout=timeout, auth_timeout=timeout,
            look_for_keys=False, allow_agent=False,
        )
    except paramiko.AuthenticationException:
        return _err("Authentication failed — check username/password.")
    except Exception as exc:  # timeouts, unreachable, refused, host-key, etc.
        return _err(f"Connection failed: {exc}")

    try:
        stdin, stdout, stderr = client.exec_command(full, timeout=timeout)
        out = stdout.read().decode("utf-8", "replace")
        err = stderr.read().decode("utf-8", "replace").strip()
    except Exception as exc:
        client.close()
        return _err(f"Command failed: {exc}")
    finally:
        client.close()

    # Storage Virtualize surfaces CLI errors like "CMMVC5707E ..." on stderr.
    if err and not out.strip():
        return _err(err)

    parsed = parse_output(out, base)
    parsed.update({"ok": True, "error": None, "raw": out.rstrip(),
                   "command": full})
    return parsed


def run_demo(command) -> dict:
    """Offline mode: parse bundled sample output so the UI/formatting can be
    exercised without a live array."""
    try:
        clean = sanitize_command(command)
    except CommandError as exc:
        return _err(str(exc))
    base = _base_command(clean)
    raw = DEMO_OUTPUTS.get(base)
    if raw is None:
        return _err(f"No demo data for '{base}'. Try: "
                    + ", ".join(sorted(DEMO_OUTPUTS)))
    parsed = parse_output(raw, base)
    parsed.update({"ok": True, "error": None, "raw": raw,
                   "command": _with_delim(clean) + "  [demo]"})
    return parsed


def _err(msg: str) -> dict:
    return {"ok": False, "error": msg, "shape": None,
            "columns": [], "rows": [], "raw": ""}


# --------------------------------------------------------------------------- #
# Demo data (delimited with DELIM). Derived from a real lsvdisk concise view.
# --------------------------------------------------------------------------- #
DEMO_OUTPUTS = {
    "lsvdisk": "\n".join([
        "id|name|IO_group_name|status|mdisk_grp_name|capacity|type|RC_name|vdisk_UID|fast_write_state|se_copy_count|volume_name|function",
        "0|CS-Vol2|io_grp0|online|cspool|10.00GB|striped||600507681081821A2000000000013493|empty|0|CS-Vol2|",
        "1|sds_epic_vol0|io_grp0|online|Pool0|3.00TB|striped||600507681081821A20000000000009D9|empty|0|sds_epic_vol0|",
        "2|CS-Vol1|io_grp0|online|cspool|10.00GB|striped||600507681081821A2000000000013495|empty|0|CS-Vol1|",
        "3|del_bzvol-11784805735744|io_grp0|online|bz-pool-71-1|1.00GB|striped||600507681081821A2000000000013497|empty|0|del_bzvol-11784805735744|",
        "4|deleting4|io_grp0|online|Pool0|10.00GB|striped||600507681081821A2000000000013555|not_empty|1|deleting4|",
        "5|pbr_demo_vol_9500|io_grp0|offline|Pool0|1000.00GB|striped|many|600507681081821A200000000000135BB|not_empty|1|pbr_demo_vol_9500|",
        "6|deleting0|io_grp0|online|Pool0|10.00GB|striped||600507681081821A2000000000013557|not_empty|1|deleting0|",
        "9|bz-vol-71-1000|io_grp0|online|bz-pool-71-1|1.00GB|striped||600507681081821A200000000000135BB|empty|0|bz-vol-71-1000|",
    ]),
    "lsmdiskgrp": "\n".join([
        "id|name|status|mdisk_count|vdisk_count|capacity|free_capacity|used_capacity|virtual_capacity|overallocation",
        "0|Pool0|online|4|18|91.00TB|64.20TB|26.80TB|30.10TB|33",
        "1|cspool|online|2|2|10.00TB|9.98TB|20.00GB|20.00GB|0",
        "6|bz-pool-71-1|online|1|3|5.00TB|4.99TB|3.00GB|3.00GB|0",
    ]),
    "lshost": "\n".join([
        "id|name|status|host_cluster_name|port_count|type|protocol",
        "0|esx-host-01|online|prod-cluster|2|generic|scsi",
        "1|esx-host-02|online|prod-cluster|2|generic|scsi",
        "2|epic-db-01|degraded||2|generic|nvme",
        "3|backup-proxy|offline||1|generic|scsi",
    ]),
    "lssystem": "\n".join([
        "id|00000204A1C0XXXX",
        "name|FS9500-DC1",
        "location|local",
        "code_level|8.7.0.2 (build 169.4.2410)",
        "topology|standard",
        "total_mdisk_capacity|106.00TB",
        "total_used_capacity|29.83TB",
        "total_free_space|76.17TB",
        "console_IP|10.20.30.40",
        "product_name|IBM FlashSystem 9500",
    ]),
}
