#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Peder Klockmann (Zevarix)
# SPDX-License-Identifier: MIT OR Apache-2.0
"""Read-only external acceptance for the public RCS MCP Hostinger endpoint."""
from __future__ import annotations
import argparse
import json
import re
from urllib.parse import urlparse
from urllib.error import HTTPError
from urllib.request import Request, urlopen

if not __debug__:
    raise RuntimeError("Live acceptance must not run with optimized assertions")

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument("--base-url",required=True,help="HTTPS site URL, without a path")
parser.add_argument("--expected-revision",required=True,help="Exact 40-character Git source commit")
parser.add_argument("--expected-rules",type=int,default=36)
parser.add_argument("--expected-guides",type=int,default=7)
args=parser.parse_args()
u=urlparse(args.base_url)
if u.scheme!="https" or not u.hostname or u.username or u.password or u.query or u.fragment or u.path not in ("","/"):
    parser.error("--base-url must be a public HTTPS host without path or credentials")
if not re.fullmatch(r"[0-9a-f]{40}",args.expected_revision):
    parser.error("--expected-revision must be an exact lowercase Git SHA")
if args.expected_rules<1 or args.expected_guides<1:
    parser.error("Expected catalog sizes must be positive")
BASE=args.base_url.rstrip("/")
REVISION=args.expected_revision
DEFAULT={
    "Accept":"application/json, text/event-stream",
    "MCP-Protocol-Version":"2025-06-18",
    "Content-Type":"application/json",
    "User-Agent":"rcs-verified-live-smoke/1.0",
}

def send(method,path,payload=None,extra=None):
    data=None if payload is None else json.dumps(payload,separators=(",",":")).encode("utf-8")
    headers=dict(DEFAULT)
    if extra:headers.update(extra)
    req=Request(BASE+path,method=method,data=data,headers=headers)
    try:
        with urlopen(req,timeout=15) as res:
            status,body=res.status,res.read().decode("utf-8")
            server=res.headers.get("platform","")
    except HTTPError as err:
        status,body=err.code,err.read().decode("utf-8")
        server=err.headers.get("platform","")
    if body.startswith("event:"):
        body=next(line[6:].strip() for line in body.splitlines() if line.startswith("data: "))
    try:
        parsed=json.loads(body)
    except Exception:
        raise RuntimeError(f"Non-JSON HTTP {status}: {body[:240]}")
    return status,parsed,server

def rpc(i,method,params=None,extra=None):
    return send("POST","/mcp",{"jsonrpc":"2.0","id":i,"method":method,"params":params or {}},extra)

s,health,platform=send("GET","/health")
assert s==200,(s,health)
assert health["revision"]==REVISION,health
assert health["rule_count"]==args.expected_rules
assert len(health["guides"])==args.expected_guides
assert health["transport"]=="streamable-http" and health["endpoint"]=="/mcp"
assert platform=="hostinger",platform
print("HEALTH=PASS HTTP_200 HOSTINGER_TLS REVISION="+health["revision"])

s,init,_=rpc(1,"initialize",{
    "protocolVersion":"2025-06-18",
    "capabilities":{},
    "clientInfo":{"name":"rcs-live-smoke","version":"0.1"},
})
assert s==200 and init["result"]["serverInfo"]["name"]=="rcs-readonly",(s,init)
print("MCP_INITIALIZE=PASS")

s,listed,_=rpc(2,"tools/list")
assert s==200,(s,listed)
expected={"search_rules","get_rule","get_guidance","catalog_info"}
toolNames={t["name"] for t in listed["result"]["tools"]}
assert toolNames==expected,toolNames
for tool in listed["result"]["tools"]:
    annotations=tool["annotations"]
    assert annotations["readOnlyHint"] is True
    assert annotations["destructiveHint"] is False
    assert annotations["openWorldHint"] is False
print("TOOLS_LIST=PASS COUNT=4 READ_ONLY=true")

for i,name,call_args in [
    (3,"catalog_info",{}),
    (4,"search_rules",{"query":"RCS-PERF-001"}),
    (5,"get_rule",{"rule_id":"RCS-PERF-001"}),
    (6,"get_guidance",{"guide_id":"optimization"}),
]:
    s,result,_=rpc(i,"tools/call",{"name":name,"arguments":call_args})
    assert s==200,(name,s,result)
    item=result["result"]["structuredContent"]
    assert item["revision"]==REVISION,(name,item)
    if name=="catalog_info":
        assert item["rule_count"]==args.expected_rules
    if name=="search_rules":
        assert item["rules"][0]["id"]=="RCS-PERF-001"
    if name in ("get_rule","get_guidance"):
        assert REVISION in item["source_url"]
        assert item["markdown"]
    print("TOOL_"+name.upper()+"=PASS")

s,missing,_=rpc(7,"tools/call",{"name":"get_rule","arguments":{"rule_id":"RCS-FAKE-999"}})
assert s==200 and missing["result"]["isError"] is True,(s,missing)
print("UNKNOWN_RULE=PASS_ERROR")

s,blocked,_=rpc(8,"tools/list",extra={"Origin":"https://attacker.example"})
assert s==403,(s,blocked)
print("HOSTILE_ORIGIN=PASS_HTTP_403")
s,method,_=send("GET","/mcp")
assert s==405,(s,method)
print("MCP_BAD_METHOD=PASS_HTTP_405")
s,tooBig,_=rpc(9,"tools/list",{"payload":"x"*70_000})
assert s==413,(s,tooBig)
print("OVERSIZE_BODY=PASS_HTTP_413")
print("LIVE_RCS_MCP_ACCEPTANCE=PASS")
