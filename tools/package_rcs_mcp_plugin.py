#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Peder Klockmann (Zevarix)
# SPDX-License-Identifier: MIT OR Apache-2.0
"""Reproducibly package a separate RCS plugin with public read-only MCP and both skills.

Reuses the validated skills-only packager for the exact canonical skill payload.
Public submission still requires owner-controlled demo, verification and attestations.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

from package_rcs_plugin import PACKAGE as SKILLS_PACKAGE
from package_rcs_plugin import STAMP, collect_files as collect_canonical_skill_files

PACKAGE = "rcs-rust-standards"
MCP_URL = "https://rcsmcp.zevarix.com/mcp"
LEGAL_URLS = {
    "privacyPolicyURL": "https://rcs.zevarix.com/privacy/",
    "termsOfServiceURL": "https://rcs.zevarix.com/terms/",
}
TOOLS = frozenset(("search_rules", "get_rule", "get_guidance", "catalog_info"))
PLUGIN_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
MCP_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json"


def canonical_text(path: Path) -> bytes:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"Missing or symlinked package file: {path.name}")
    return path.read_bytes().decode("utf-8").replace("\r\n", "\n").encode("utf-8")


def collect_files(repository: Path) -> dict[str, bytes]:
    folder = repository / "plugin" / PACKAGE
    manifest_bytes = canonical_text(folder / "plugin.json")
    mcp_bytes = canonical_text(folder / "mcp.json")
    manifest, mcp = json.loads(manifest_bytes), json.loads(mcp_bytes)

    if manifest.get("$schema") != PLUGIN_SCHEMA or manifest.get("name") != PACKAGE:
        raise ValueError("Unexpected connected-plugin schema or identity")
    if not re.fullmatch(r"\d+\.\d+\.\d+", str(manifest.get("version", ""))):
        raise ValueError("Connected-plugin version must be SemVer")
    if any(key in manifest for key in ("apps", "mcpServers", "hooks")):
        raise ValueError("Unsupported root app/hook/MCP declarations")
    ext = manifest.get("extensions", {}).get("com.openai", {})
    if any(key in ext for key in ("apps", "hooks")):
        raise ValueError("MCP public submission cannot include app bindings or hooks")
    ui = ext.get("interface", {})
    if ui.get("category") != "Developer Tools":
        raise ValueError("Unexpected connected-plugin category")
    if not 1 <= len(ui.get("shortDescription", "")) <= 30:
        raise ValueError("Connected-plugin subtitle exceeds 30 characters")
    if ui.get("developerName") != manifest.get("author", {}).get("name"):
        raise ValueError("Individual publisher name mismatch")
    for icon in ("logo", "composerIcon"):
        if ui.get(icon) != "./assets/forge-crab.png":
            raise ValueError(f"Unexpected {icon} path")
    if not ui.get("websiteURL", "").startswith("https://") or not ui.get("supportURL", "").startswith("https://"):
        raise ValueError("Public website and support links must use HTTPS")
    for key, verified_url in LEGAL_URLS.items():
        if ui.get(key) != verified_url:
            raise ValueError(f"{key} must use the verified RCS public HTTPS page")
    cases = ext.get("review", {}).get("test_cases", {})
    positive, negative = cases.get("positive", []), cases.get("negative", [])
    if len(positive) != 5 or len(negative) != 3:
        raise ValueError("Initial MCP review requires five positive and three negative tests")
    for case in positive:
        if not all(case.get(k) for k in ("description", "prompt", "tools_triggered", "expected_behavior")):
            raise ValueError("Incomplete positive reviewer case")
        if not set(x.strip() for x in case["tools_triggered"].split(",")) <= TOOLS:
            raise ValueError("Reviewer case references an unsupported MCP tool")
    for case in negative:
        if not all(case.get(k) for k in ("description", "prompt")):
            raise ValueError("Incomplete negative reviewer case")
    if not ext.get("publication", {}).get("release_notes"):
        raise ValueError("Missing initial release notes")
    if mcp.get("$schema") != MCP_SCHEMA or set(mcp.get("mcpServers", {})) != {"rcs"}:
        raise ValueError("Connected-plugin must declare exactly one RCS MCP server")
    server = mcp["mcpServers"]["rcs"]
    if server.get("url") != MCP_URL or server.get("type") != "streamable-http":
        raise ValueError("Unexpected RCS remote MCP endpoint or transport")
    if server.get("extensions", {}).get("com.openai", {}).get("auth") != {"type": "none"}:
        raise ValueError("Public read-only RCS MCP must not claim user authentication")
    if any(key in mcp for key in ("apps", "hooks")):
        raise ValueError("Unsupported MCP app or lifecycle hooks")

    existing = collect_canonical_skill_files(repository)
    prefix = SKILLS_PACKAGE + "/"
    result = {}
    for path, data in existing.items():
        relative = path.removeprefix(prefix)
        if relative.startswith("skills/") or relative == "assets/forge-crab.png":
            result[f"{PACKAGE}/{relative}"] = data
    if len(result) != len(existing) - 1:
        raise ValueError("Source skill or icon inventory changed unexpectedly")
    result[f"{PACKAGE}/plugin.json"] = manifest_bytes
    result[f"{PACKAGE}/mcp.json"] = mcp_bytes
    return result


def build(repository: Path, archive: Path) -> str:
    entries = collect_files(repository)
    archive.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(archive, "w") as output:
        for path, contents in sorted(entries.items()):
            info = ZipInfo(path, date_time=STAMP)
            info.compress_type = ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            output.writestr(info, contents, compress_type=ZIP_DEFLATED, compresslevel=9)
    with ZipFile(archive) as check:
        if check.testzip() is not None or set(check.namelist()) != set(entries):
            raise RuntimeError("MCP candidate ZIP failed CRC or inventory verification")
        for path, contents in entries.items():
            if check.read(path) != contents:
                raise RuntimeError(f"MCP candidate content drift: {path}")
    return hashlib.sha256(archive.read_bytes()).hexdigest()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args()
    root = args.root.resolve()
    version = json.loads((root / "plugin" / PACKAGE / "plugin.json").read_text(encoding="utf-8"))["version"]
    output = (args.output or Path("dist") / f"rcs-connected-plugin-{version}.zip").resolve()
    digest = build(root, output)
    print("PASS: reproducible RCS connected-plugin candidate with four public MCP tools and two canonical skills")
    print("PORTAL SUBMISSION PENDING: reviewer demo, domain verification, scans and owner attestations")
    print(f"ARCHIVE={output}")
    print(f"SHA256={digest}")

