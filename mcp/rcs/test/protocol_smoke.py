#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Peder Klockmann (Zevarix)
# SPDX-License-Identifier: MIT OR Apache-2.0
"""Test the real stateless Streamable HTTP RCS MCP server on loopback.

This starts only the project's own local dev process and stops its process tree.
It never invokes a Cloudflare deployment or touches unrelated listeners.
"""
from __future__ import annotations

import json
import os
import signal
import socket
import subprocess
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[3]
PROJECT = ROOT / "mcp" / "rcs"
LOG = PROJECT / ".cloudflare" / "protocol-smoke.log"
PORT = 8795
BASE = "http://127.0.0.1:" + str(PORT)


def send(method: str, path: str, payload=None, headers=None):
    all_headers = {
        "Accept": "application/json, text/event-stream",
        "Content-Type": "application/json",
        "MCP-Protocol-Version": "2025-06-18",
    }
    if headers:
        all_headers.update(headers)
    data = None if payload is None else json.dumps(payload, separators=(",", ":")).encode()
    request = Request(BASE + path, data=data, headers=all_headers, method=method)
    try:
        with urlopen(request, timeout=8) as response:
            return response.status, response.read().decode("utf-8")
    except HTTPError as error:
        return error.code, error.read().decode("utf-8", errors="replace")


def rpc(request_id: int, method: str, params=None, headers=None):
    status, body = send("POST", "/mcp", {
        "jsonrpc": "2.0", "id": request_id, "method": method, "params": params or {},
    }, headers)
    if body.startswith("event:"):
        body = next(line[6:].strip() for line in body.splitlines() if line.startswith("data: "))
    return status, json.loads(body)


def run():
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with socket.socket() as probe:
        if probe.connect_ex(("127.0.0.1", PORT)) == 0:
            raise RuntimeError("Loopback test port occupied; refusing to affect another process")

    env = os.environ.copy()
    env["CI"] = "true"
    local_node = ROOT / ".toolchain" / "node_modules" / "node" / "bin"
    if local_node.is_dir():
        env["PATH"] = str(local_node) + os.pathsep + env["PATH"]

    if os.name == "nt":
        command = ["cmd.exe", "/c", "npm.cmd", "run", "dev", "--",
                   "--host", "127.0.0.1", "--port", str(PORT)]
        flags = subprocess.CREATE_NEW_PROCESS_GROUP
        options = {"creationflags": flags}
    else:
        command = ["npm", "run", "dev", "--", "--host", "127.0.0.1", "--port", str(PORT)]
        options = {"start_new_session": True}

    with LOG.open("wb") as output:
        process = subprocess.Popen(command, cwd=PROJECT, env=env,
                                   stdout=output, stderr=subprocess.STDOUT, **options)
        try:
            for attempt in range(100):
                if process.poll() is not None:
                    raise RuntimeError("Local MCP server stopped: " + str(process.returncode))
                try:
                    status, body = send("GET", "/health")
                    if status == 200:
                        break
                except (OSError, URLError):
                    pass
                time.sleep(0.2)
            else:
                raise RuntimeError("Local MCP server failed to become ready")

            catalog = json.loads(
                (PROJECT / "src/generated/catalog.json").read_text(encoding="utf-8")
            )
            health = json.loads(body)
            assert health["rule_count"] == len(catalog["rules"])
            assert health["revision"] == catalog["revision"]

            status, init = rpc(1, "initialize", {
                "protocolVersion": "2025-06-18", "capabilities": {},
                "clientInfo": {"name": "rcs-protocol-smoke", "version": "0.1.0"},
            })
            assert status == 200 and init["result"]["serverInfo"]["name"] == "rcs-readonly"

            status, data = rpc(2, "tools/list")
            assert status == 200
            tools = data["result"]["tools"]
            assert {tool["name"] for tool in tools} == {
                "catalog_info", "search_rules", "get_rule", "get_guidance",
            }
            for tool in tools:
                annotations = tool["annotations"]
                assert annotations["readOnlyHint"] is True
                assert annotations["destructiveHint"] is False
                assert annotations["openWorldHint"] is False

            status, data = rpc(3, "tools/call", {
                "name": "get_rule", "arguments": {"rule_id": "RCS-PERF-001"},
            })
            assert status == 200
            rule = data["result"]["structuredContent"]
            assert rule["id"] == "RCS-PERF-001"
            assert catalog["revision"] in rule["source_url"]
            assert "entire action path" in rule["markdown"]

            status, data = rpc(4, "tools/call", {
                "name": "search_rules", "arguments": {"query": "redundant", "limit": 3},
            })
            assert status == 200 and data["result"]["structuredContent"]["rules"]

            status, data = rpc(5, "tools/call", {
                "name": "get_guidance", "arguments": {"guide_id": "verification"},
            })
            assert status == 200
            assert "Risk-weighted behavioral verification" in data["result"]["structuredContent"]["markdown"]

            status, data = rpc(6, "tools/call", {
                "name": "catalog_info", "arguments": {},
            })
            assert status == 200
            assert data["result"]["structuredContent"]["revision"] == catalog["revision"]

            status, data = rpc(7, "tools/call", {
                "name": "get_rule", "arguments": {"rule_id": "RCS-NONE-999"},
            })
            assert status == 200 and data["result"]["isError"] is True

            status, _ = send("POST", "/mcp", {
                "jsonrpc": "2.0", "id": 8, "method": "tools/list",
                "params": {"too_large": "x" * 67000},
            })
            assert status == 413
            status, _ = send("GET", "/mcp")
            assert status in (400, 405)
            status, _ = send("POST", "/mcp", {
                "jsonrpc": "2.0", "id": 9, "method": "tools/list",
            }, {"Origin": "https://malicious.example"})
            assert status == 403
            print("PASS: real MCP protocol/4 read-only tools, source citations, "
                  "error/size/Origin controls and loopback lifecycle")
        except BaseException:
            output.flush()
            log = LOG.read_text(encoding="utf-8", errors="replace")
            print("MCP_DEV_LOG_TAIL=", log[-4000:].encode("ascii", "backslashreplace").decode())
            raise
        finally:
            if os.name == "nt":
                subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"],
                               capture_output=True, text=True, timeout=15)
            elif process.poll() is None:
                os.killpg(process.pid, signal.SIGTERM)
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()


if __name__ == "__main__":
    run()
