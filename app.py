"""IBM Storage Virtualize 'Easy List' tool — Flask backend.

Run:
    python app.py            # connects to real systems over SSH
    python app.py --port 8080

Then open http://localhost:5000 (or the port you chose).
"""

from __future__ import annotations

import argparse
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

from flask import Flask, jsonify, render_template, request

import queries
import svc_client

app = Flask(__name__)

PROFILES_PATH = os.path.join(os.path.dirname(__file__), "profiles.json")
MAX_WORKERS = 8
# --------------------------------------------------------------------------- #
# Pages
# --------------------------------------------------------------------------- #
@app.route("/")
def index():
    return render_template("index.html")


# --------------------------------------------------------------------------- #
# API
# --------------------------------------------------------------------------- #
@app.route("/api/queries")
def api_queries():
    return jsonify({
        "catalog": queries.public_catalog(),
        "all_commands": queries.ALL_LS_COMMANDS,
    })


@app.route("/api/run", methods=["POST"])
def api_run():
    data = request.get_json(force=True, silent=True) or {}
    command = (data.get("command") or "").strip()
    systems = data.get("systems") or []

    if not command:
        return jsonify({"error": "No command selected."}), 400
    if not systems:
        return jsonify({"error": "Add at least one system."}), 400

    # Validate once up front so a bad command fails fast with a clear message.
    try:
        svc_client.sanitize_command(command)
    except svc_client.CommandError as exc:
        return jsonify({"error": str(exc)}), 400

    results = [None] * len(systems)

    def work(idx, sys_def):
        label = sys_def.get("name") or sys_def.get("ip") or f"system-{idx + 1}"
        ip = (sys_def.get("ip") or "").strip()
        if not ip:
            return idx, {"system": label, **svc_client._err("Missing IP address.")}
        res = svc_client.run_command(
            ip=ip,
            username=sys_def.get("username") or "",
            password=sys_def.get("password") or "",
            command=command,
            port=sys_def.get("port") or 22,
        )
        res["system"] = label
        res["ip"] = ip
        return idx, res

    with ThreadPoolExecutor(max_workers=min(MAX_WORKERS, len(systems))) as pool:
        futures = [pool.submit(work, i, s) for i, s in enumerate(systems)]
        for fut in as_completed(futures):
            idx, res = fut.result()
            results[idx] = res

    return jsonify({"command": command, "results": results})


@app.route("/api/profiles", methods=["GET", "POST", "DELETE"])
def api_profiles():
    """Persist host definitions (IP / username / port only — never passwords)."""
    if request.method == "GET":
        return jsonify({"systems": _load_profiles()})

    if request.method == "DELETE":
        _save_profiles([])
        return jsonify({"systems": []})

    data = request.get_json(force=True, silent=True) or {}
    incoming = data.get("systems") or []
    cleaned = [
        {
            "name": (s.get("name") or "").strip(),
            "ip": (s.get("ip") or "").strip(),
            "port": s.get("port") or 22,
            "username": (s.get("username") or "").strip(),
        }
        for s in incoming
        if (s.get("ip") or "").strip()
    ]
    _save_profiles(cleaned)
    return jsonify({"systems": cleaned})


def _load_profiles():
    try:
        with open(PROFILES_PATH, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        return data.get("systems", []) if isinstance(data, dict) else []
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def _save_profiles(systems):
    with open(PROFILES_PATH, "w", encoding="utf-8") as fh:
        json.dump({"systems": systems}, fh, indent=2)


# --------------------------------------------------------------------------- #
def main():
    parser = argparse.ArgumentParser(description="IBM Storage Virtualize Easy List tool")
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--host", default="127.0.0.1")
    args = parser.parse_args()
    print(f" * Storage Virtualize Easy List → http://{args.host}:{args.port}")
    app.run(host=args.host, port=args.port, debug=False)


if __name__ == "__main__":
    main()
