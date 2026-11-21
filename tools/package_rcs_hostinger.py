#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Peder Klockmann (Zevarix)
# SPDX-License-Identifier: MIT OR Apache-2.0
"""Package a standalone Hostinger-compatible RCS MCP Node.js service.

This archive contains only the read-only Node transport, canonical tool factory,
revision-qualified rule catalog, pinned production dependencies and licenses.
No host credentials, source collections, Cloudflare code or generated node_modules.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

STAMP = (1980, 1, 1, 0, 0, 0)
HOSTINGER_FILES = {
    "package.json": "mcp/rcs/hostinger/package.json",
    "package-lock.json": "mcp/rcs/hostinger/package-lock.json",
    "src/node.mjs": "mcp/rcs/src/node.mjs",
    "src/hostinger-entry.mjs": "mcp/rcs/src/hostinger-entry.mjs",
    "src/server.mjs": "mcp/rcs/src/server.mjs",
    "src/catalog.mjs": "mcp/rcs/src/catalog.mjs",
    "src/generated/catalog.json": "mcp/rcs/src/generated/catalog.json",
    "LICENSE-MIT": "LICENSE-MIT",
    "LICENSE-APACHE": "LICENSE-APACHE",
}
ALLOWED_DEPS = {
    "@modelcontextprotocol/server": "2.4.0",
    "@modelcontextprotocol/node": "2.1.2",
    "zod": "4.6.7",
}


def collect_files(root: Path) -> dict[str, bytes]:
    # Build the static catalog from the *current* Git revision, not a stale
    # generated checkout artifact. This process has no publishing privileges.
    subprocess.run(
        [sys.executable, str(root / "tools/build_rcs_mcp_index.py")],
        cwd=root, check=True, capture_output=True, text=True,
    )
    pkg = json.loads((root / HOSTINGER_FILES["package.json"]).read_text(encoding="utf-8"))
    lock = json.loads((root / HOSTINGER_FILES["package-lock.json"]).read_text(encoding="utf-8"))
    if not re.fullmatch(r"\d+\.\d+\.\d+", str(pkg.get("version", ""))):
        raise ValueError("Hostinger bundle must use an explicit release version")
    if pkg.get("dependencies") != ALLOWED_DEPS or pkg.get("scripts") != {"start": "node src/hostinger-entry.mjs"}:
        raise ValueError("Unexpected runtime dependencies or executable scripts")
    if pkg.get("private") is not True or pkg.get("type") != "module":
        raise ValueError("Unexpected package publishing/module settings")
    if lock.get("name") != pkg.get("name") or lock.get("version") != pkg["version"]:
        raise ValueError("Hostinger package and lockfile disagree")
    if lock.get("packages", {}).get("", {}).get("dependencies") != ALLOWED_DEPS:
        raise ValueError("Hostinger lockfile dependencies do not match")
    catalog = json.loads((root / HOSTINGER_FILES["src/generated/catalog.json"]).read_text(encoding="utf-8"))
    revision = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
    if catalog.get("revision") != revision or len(catalog.get("rules", [])) < 36:
        raise ValueError("Hostinger catalog missing or from an unexpected revision")
    if len(catalog.get("guides", [])) != 7:
        raise ValueError("Hostinger guide index is incomplete")

    result = {}
    for target, source in HOSTINGER_FILES.items():
        path = root / source
        if path.is_symlink() or not path.is_file():
            raise ValueError("Missing or symlinked public source: " + source)
        text = path.read_text(encoding="utf-8")
        payload = text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")
        if not payload or len(payload) > 2 * 1024 * 1024:
            raise ValueError("Missing or oversized bundle file: " + source)
        result[target] = payload
    return result


def build(root: Path, archive: Path) -> str:
    entries = collect_files(root)
    archive.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(archive, "w") as output:
        for name, payload in sorted(entries.items()):
            info = ZipInfo(name, date_time=STAMP)
            info.compress_type = ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = (0o100644 << 16)
            output.writestr(info, payload, compress_type=ZIP_DEFLATED, compresslevel=9)
    with ZipFile(archive) as check:
        if check.testzip() is not None or set(check.namelist()) != set(entries):
            raise RuntimeError("Hostinger ZIP inventory/CRC mismatch")
        for name, original in entries.items():
            if check.read(name) != original:
                raise RuntimeError("Hostinger ZIP content drift: " + name)
    return hashlib.sha256(archive.read_bytes()).hexdigest()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    repository = args.root.resolve()
    pkg = json.loads((repository / HOSTINGER_FILES["package.json"]).read_text(encoding="utf-8"))
    out = (args.output or Path("dist") / f"rcs-hostinger-mcp-{pkg['version']}.zip").resolve()
    digest = build(repository, out)
    print("PASS: self-contained Hostinger RCS MCP ZIP; read-only tool sources, versioned catalog and pinned runtimes")
    print("ARCHIVE=" + str(out))
    print("SHA256=" + digest)
