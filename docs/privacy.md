---
title: "RCS Plugin — Privacy Policy"
description: "How the read-only Rust Coding Standards MCP service handles tool requests, technical access logs, retention and user privacy requests."
---

# RCS Plugin — Privacy Policy

**Effective date:** November 20, 2026

**Publisher:** Peder Klockmann, publishing Rust Coding Standards (RCS) as an individual developer.

## Scope

This policy describes the RCS read-only MCP service at
[rcsmcp.zevarix.com/mcp](https://rcsmcp.zevarix.com/mcp) and its connected
ChatGPT/Codex plugin. It does not replace the privacy practices of ChatGPT,
Codex, GitHub, or Hostinger, which operate their own services. The public RCS
documentation site is separately served through GitHub Pages; the applicable
hosting platform may process technical request information when the website
is viewed.

## Information the service receives

The RCS MCP server receives only the particular tool calls sent by the client,
such as a rule-search query, result limit, an exact RCS rule identifier, or a
fixed guidance identifier. It does not request authentication credentials,
account profiles, file contents, a complete conversation history, or private
repository access. Users should not include personal, confidential, medical,
financial, or credential information in search text.

Like other public web endpoints, the hosting layer may process connection and
request metadata. Hostinger describes website access logs as including the
time, visitor IP address, country, requested URL, HTTP status, and user agent.
This is separate from the application code, which does not deliberately log
tool input strings or response bodies. A read of recent Node.js application
runtime logs showed startup messages only; that observation does not establish
that all infrastructure logs are empty.

## Use of information

Tool-call inputs are processed to select and return publicly available RCS
documentation, rule descriptions, and source citations. Technical request
metadata may be processed by the hosting provider for delivery, abuse
prevention, troubleshooting, and service security. No RCS tool is able to
execute code, modify files, inspect private repositories, or store user
profiles. The publisher does not use these MCP requests for advertising,
profiling, or sale of personal information.

## Storage and retention

The RCS application is stateless: it does not create a database, persistent
tool-call history, or account. Tool-call parameters are handled in memory for
the duration of a request and not intentionally retained by the RCS
application after the response.

Hostinger states that website access logs are retained for **up to seven
days** in its standard access-log interface. Hostinger may separately maintain
operational or security records under its own policies; separate provider-
managed retention, backups or incident records may not follow that same
access-log period. ChatGPT and Codex may retain conversations and tool-related
activity under their own policies, outside the RCS publisher's control.

## Service providers and disclosures

Hostinger processes HTTP traffic and technical service data to host the MCP
endpoint. GitHub hosts the public RCS source, issue-support pages, and
documentation website through GitHub Pages. The client sending an MCP request
(for example, ChatGPT or Codex) receives the requested tool response. The
RCS publisher does not intentionally disclose tool-call content to
advertisers or data brokers, and the server does not forward queries to other
AI models or private third-party APIs.

## Choices and requests

You may avoid sending personal information in tool inputs, choose not to use
the plugin, and disconnect it through your client where supported. For
support or privacy questions, use the
[RCS issue tracker](https://github.com/zevarix/rust-coding-standards/issues)
to request a confidential contact route; **do not include personal
information in a public issue**. Requests concerning conversations stored by
ChatGPT or Codex should be directed to the respective provider. Access,
correction, or deletion requests will be handled as applicable law and
available provider controls permit; we cannot promise deletion of third-party
operational logs before their normal retention period.

## Security and changes

The service uses HTTPS and bounds tool inputs. No service can guarantee
perfect security. Material updates to this notice will be published on the
RCS site before or when new collection practices take effect. This service
is not intended to solicit data from children under 13.

For terms governing this service, see the
[RCS Plugin Terms of Service](terms.md).
