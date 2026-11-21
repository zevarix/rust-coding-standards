#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Peder Klockmann (Zevarix)
# SPDX-License-Identifier: MIT OR Apache-2.0
"""Build the skills-only RCS Agent Plugin from canonical repository files.

The generated ZIP is deliberately not tracked. It contains the two current
repository skills, not a separately maintained copy of their documentation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

PACKAGE = "rust-coding-standards"
SKILLS = ("rcs-guidance", "rust-performance")
# Known public files only. New support files must be reviewed before packaging.
SKILL_FILES = (
    "SKILL.md",
    "agents/openai.yaml",
    "LICENSE-MIT",
    "LICENSE-APACHE",
    "NOTICE",
)
SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
STAMP = (1980, 1, 1, 0, 0, 0)


def collect_files(repository: Path) -> dict[str, bytes]:
    manifest_path = repository / "plugin" / PACKAGE / "plugin.json"
    # Universal-newline text reading avoids Windows checkout CRLF in the ZIP.
    manifest_text = manifest_path.read_text(encoding="utf-8")
    manifest = json.loads(manifest_text)
    if manifest.get("$schema") != SCHEMA or manifest.get("name") != PACKAGE:
        raise ValueError("Plugin name/schema mismatch")
    if not re.fullmatch(r"\d+\.\d+\.\d+", str(manifest.get("version", ""))):
        raise ValueError("Plugin version must be SemVer")
    interface = manifest.get("extensions", {}).get("com.openai", {}).get("interface", {})
    if interface.get("category") != "Developer Tools":
        raise ValueError("Plugin category does not match supported category")
    subtitle = interface.get("shortDescription", "")
    if not subtitle or len(subtitle) > 30:
        raise ValueError("Plugin subtitle must be 1 to 30 characters")
    if "mcpServers" in manifest or "apps" in manifest:
        raise ValueError("Skills-only plugin must not declare invented tools or apps")
    openai = manifest.get("extensions", {}).get("com.openai", {})
    if openai.get("apps") is not None:
        raise ValueError("Public skills-only plugin must not declare app bindings")

    entries = {f"{PACKAGE}/plugin.json": manifest_text.encode("utf-8")}
    mark = repository / "plugin" / PACKAGE / "assets" / "forge-crab.png"
    if mark.is_symlink() or not mark.is_file():
        raise ValueError("Openly licensed Forge PNG missing or symlinked")
    image = mark.read_bytes()
    if len(image) > 5 * 1024 * 1024 or len(image) < 24:
        raise ValueError("Forge PNG is missing or exceeds the supported size")
    if image[:8] != b"\x89PNG\r\n\x1a\n" or image[12:16] != b"IHDR":
        raise ValueError("Forge mark is not a valid PNG")
    width, height = struct.unpack(">II", image[16:24])
    if width != height or not (256 <= width <= 4096):
        raise ValueError("Forge PNG must be a square image of at least 256 pixels")
    entries[f"{PACKAGE}/assets/forge-crab.png"] = image
    for field in ("logo", "composerIcon"):
        if interface.get(field) != "./assets/forge-crab.png":
            raise ValueError(f"Unexpected {field} icon reference")

    for name in SKILLS:
        folder = repository / "skills" / name
        if not folder.is_dir() or folder.is_symlink():
            raise ValueError(f"Missing or symlinked skill directory: {name}")
        available = {
            path.relative_to(folder).as_posix()
            for path in folder.rglob("*") if path.is_file() or path.is_symlink()
        }
        if available != set(SKILL_FILES):
            raise ValueError(f"Unexpected/missing files in {name}: {sorted(available ^ set(SKILL_FILES))}")
        for relative in SKILL_FILES:
            source = folder / relative
            if source.is_symlink() or not source.is_file():
                raise ValueError(f"Missing or symlinked required file: {name}/{relative}")
            payload = source.read_bytes()
            if not payload or len(payload) > 1024 * 1024:
                raise ValueError(f"Missing or excessively large skill component: {name}/{relative}")
            payload.decode("utf-8")
            entries[f"{PACKAGE}/skills/{name}/{relative}"] = payload
        header = (folder / "SKILL.md").read_text(encoding="utf-8")
        if not re.search(r"\A---\r?\nname:\s*" + re.escape(name) + r"\s*\r?\n", header):
            raise ValueError(f"Skill {name} lacks expected name frontmatter")
        if not re.search(r"(?m)^description:\s*\S", header):
            raise ValueError(f"Skill {name} lacks description frontmatter")
    return entries


def build(repository: Path, archive: Path) -> str:
    entries = collect_files(repository)
    archive.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(archive, "w") as output:
        for path, content in sorted(entries.items()):
            info = ZipInfo(path, date_time=STAMP)
            info.compress_type = ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = (0o100644 << 16)
            output.writestr(info, content, compress_type=ZIP_DEFLATED, compresslevel=9)

    with ZipFile(archive) as result:
        if result.testzip() is not None or set(result.namelist()) != set(entries):
            raise RuntimeError("Plugin ZIP inventory or CRC mismatch")
        for name, original in entries.items():
            if result.read(name) != original:
                raise RuntimeError(f"Plugin ZIP content drift: {name}")
    return hashlib.sha256(archive.read_bytes()).hexdigest()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args()
    repository = args.root.resolve()
    manifest = json.loads((repository / "plugin" / PACKAGE / "plugin.json").read_text(encoding="utf-8"))
    out = (args.output or Path("dist") / f"rcs-plugin-{manifest['version']}.zip").resolve()
    digest = build(repository, out)
    print("PASS: deterministic skills-only plugin ZIP; two canonical skills, notices and icon verified")
    print(f"ARCHIVE={out}")
    print(f"SHA256={digest}")
