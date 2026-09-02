---
name: wwise-waapi-skill
description: Drive Wwise Authoring directly via WAAPI (Wwise Authoring API) without an MCP server. Use when the user wants to query/create/modify Wwise objects, import audio, generate SoundBanks, control transport/profiler, or manipulate the Wwise UI/layout from a Python or shell session. Trigger phrases include "Wwise", "WAAPI", "ak.wwise.*", "ak.soundengine.*", "WAQL", "SoundBank generate", "Wwise object", "Wwise event".
---

# Wwise WAAPI Skill

Use this skill to drive Wwise Authoring through WAAPI from the local machine. It is the non-MCP counterpart to the WwiseMCP server: the same procedure surface, exposed via a thin Python wrapper you invoke with the Bash tool.

## When to use this skill

- The user mentions Wwise, WAAPI, WAQL, SoundBank, Wwise events, RTPC/State/Switch, or any `ak.wwise.*` / `ak.soundengine.*` URI.
- The user wants to script Wwise from a terminal or a Python file rather than through an MCP client.
- Any task requiring object query, creation, audio import, SoundBank generation, profiler capture, transport playback, or UI/layout control of a running Wwise Authoring instance.

If the user is asking only conceptual/documentation questions about Wwise (no live operation), still load the relevant reference page from `references/`, but skip the runtime setup.

## Prerequisites (verify before any call)

1. Wwise 2024.1+ is running with **Project > User Preferences > Enable Wwise Authoring API** turned on.
2. Python 3.9+ is available on PATH.
3. The `waapi-client` package is installed: `pip install waapi-client`.

Confirm the connection with one ping before doing anything else:

```powershell
python "<skill-dir>\scripts\wwise_waapi.py" ak.wwise.core.ping
```

A healthy response is `{"isAvailable": true}`. If it errors, see [workflows/setup-and-connect.md](workflows/setup-and-connect.md).

## How to call WAAPI

The skill ships a single helper, `scripts/wwise_waapi.py`, that wraps `waapi.WaapiClient`. Invoke any procedure by passing its URI plus a JSON args object (and optional options object):

```powershell
python scripts\wwise_waapi.py <procedure-uri> [args-json] [options-json]
```

Examples (Windows PowerShell — note the single-quoted JSON to avoid PS expansion):

```powershell
python scripts\wwise_waapi.py ak.wwise.core.ping
python scripts\wwise_waapi.py ak.wwise.core.object.get '{"waql":"$ from type Sound take 5"}' '{"return":["id","name","path","type"]}'
python scripts\wwise_waapi.py ak.wwise.core.soundbank.generate '{"rebuildSoundBanks":true,"writeToDisk":true}'
```

Output is the raw WAAPI JSON written to stdout. Errors (unreachable, modal dialog, bad args) print to stderr with a non-zero exit code.

For multi-step Python automation, import the helper directly:

```python
from scripts.wwise_waapi import call
sounds = call("ak.wwise.core.object.get",
              args={"waql": "$ from type Sound where volume > 0"},
              options={"return": ["id", "name"]})
```

Full setup details (install, connect failures, port, persistent client) are in [workflows/setup-and-connect.md](workflows/setup-and-connect.md). **Read it only if `ping` fails or the user asks about installation.**

## Progressive disclosure — load the right page only when needed

This skill keeps SKILL.md small. Each operation has a dedicated workflow page; each lookup has a dedicated reference page. **Do not load every file up front.** Read only what the current task needs.

### Workflow pages (load when doing the operation)

| Task | File |
| --- | --- |
| Find / list objects with WAQL | [workflows/query-objects.md](workflows/query-objects.md) |
| Create, set, copy, move, delete objects (incl. batch `set_objects`) | [workflows/create-and-modify.md](workflows/create-and-modify.md) |
| Import WAV/voice files into the project | [workflows/import-audio.md](workflows/import-audio.md) |
| Edit SoundBank inclusions; generate banks | [workflows/soundbank.md](workflows/soundbank.md) |
| Post events, set RTPC/State/Switch, mute/solo, transport | [workflows/transport-soundengine.md](workflows/transport-soundengine.md) |
| Profiler capture and data retrieval | [workflows/profiler.md](workflows/profiler.md) |
| UI commands, layouts, view docking, screen capture | [workflows/ui-and-layout.md](workflows/ui-and-layout.md) |
| Project info, save, open/close, schema/topic discovery | [workflows/project-and-meta.md](workflows/project-and-meta.md) |

### Reference pages (load when constructing args or interpreting results)

| Lookup | File |
| --- | --- |
| Full WAAPI URI catalogue + argument signatures | [references/waapi-procedures.md](references/waapi-procedures.md) |
| WAQL grammar, sources, transforms, operators | [references/waql-syntax.md](references/waql-syntax.md) |
| `<nodeType>` tags for path-based creation | [references/object-types.md](references/object-types.md) |
| Common properties/references (`@Volume`, `parent.descendants`, etc.) | [references/object-accessors.md](references/object-accessors.md) |
| Canonical `set_objects` payload shapes (RTPC, Attenuation curves, Music, Effects) | [references/set-objects-cookbook.md](references/set-objects-cookbook.md) |
| Properties usable as State columns | [references/state-properties.md](references/state-properties.md) |

When you don't know which property/reference a type exposes, call the live introspection procedure instead of hunting docs:

```powershell
python scripts\wwise_waapi.py ak.wwise.core.object.getPropertyAndReferenceNames '{"object":"<path-or-guid>"}'
python scripts\wwise_waapi.py ak.wwise.core.object.getPropertyInfo '{"property":"Volume","object":"<path>"}'
```

## Recommended task order

1. **Ping** — `ak.wwise.core.ping`. If unavailable, stop and surface the error.
2. **Resolve targets** — use `ak.wwise.core.object.get` (WAQL) to convert names/paths to GUIDs. GUIDs are safer than long paths in subsequent calls. Always cap large queries with `take N`.
3. **Read the relevant workflow page**, then construct the call.
4. **For property/reference set operations**, remember override switches: `@OverridePositioning`, `@EnableAttenuation`, etc. must be true before their downstream values become visible. Use `getPropertyInfo` to check.
5. **Save** when the user asks (`ak.wwise.core.project.save`). Do **not** auto-save after every edit.

## Hard rules

- **Confirm before destructive actions.** `ak.wwise.core.object.delete`, `ak.wwise.ui.project.close` (without `bypassSave`), `ak.wwise.core.soundbank.generate` with `clearAudioFileCache: true`, and `setInclusions` with `operation: "replace"` all destroy state. Confirm with the user first unless they explicitly authorized the action in this turn.
- **Never call `copy_object` on a Work Unit** without warning the user — the operation cannot be undone and force-saves the project.
- **Pagination uses `take`/`skip`, not `limit`.** A bare `$ from type Event` on a real project returns thousands of rows. Always bound it.
- **Don't fabricate property/reference names.** When unsure, call `getPropertyAndReferenceNames` rather than guessing.
