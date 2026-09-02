# Project Info, Save, Logs, and Schema Discovery

Procedures that are conceptually "global" — about the project, the running Wwise instance, the WAAPI surface itself, and Wwise's own log channels.

## Project info

```powershell
# The current project (path, platforms, languages, …)
python scripts\wwise_waapi.py ak.wwise.core.getProjectInfo

# The Wwise installation (version, install dirs, build configuration)
python scripts\wwise_waapi.py ak.wwise.core.getInfo
```

`getInfo` is useful for branching behavior on Wwise version (some procedures only exist in 2024.1+).

## Save

```powershell
python scripts\wwise_waapi.py ak.wwise.core.project.save
python scripts\wwise_waapi.py ak.wwise.core.project.save '{"autoCheckOutToSourceControl": false}'
```

Default `autoCheckOutToSourceControl` is true. Set false when the user is on a non-Perforce/SVN setup or wants to manage check-outs manually.

**Don't auto-save after every WAAPI edit.** Save when the user asks, or at meaningful checkpoints (after a batch import, before a SoundBank generate). Repeated saves churn source control.

## Liveness check

```powershell
python scripts\wwise_waapi.py ak.wwise.core.ping
```

Always the first call before doing anything substantial. `{isAvailable: false}` means a modal dialog is blocking — see [setup-and-connect.md](setup-and-connect.md).

## Logs

```powershell
python scripts\wwise_waapi.py ak.wwise.core.log.get '{"channel":"general"}'
python scripts\wwise_waapi.py ak.wwise.core.log.get '{"channel":"soundbankGenerate"}'
python scripts\wwise_waapi.py ak.wwise.core.log.get '{"channel":"conversion"}'
python scripts\wwise_waapi.py ak.wwise.core.log.get '{"channel":"projectLoad"}'
python scripts\wwise_waapi.py ak.wwise.core.log.get '{"channel":"waapi"}'
python scripts\wwise_waapi.py ak.wwise.core.log.get '{"channel":"sourceControl"}'
python scripts\wwise_waapi.py ak.wwise.core.log.get '{"channel":"copyPlatformSettings"}'
python scripts\wwise_waapi.py ak.wwise.core.log.get '{"channel":"lua"}'
```

Each entry has `severity` (`Message` / `Warning` / `Error` / `Fatal Error`), `time`, `messageId`, `message`, optional `platform` and `parameters`. Use this to surface SoundBank generation warnings, conversion failures, or Lua errors back to the user.

## Undo / redo

```powershell
python scripts\wwise_waapi.py ak.wwise.core.undo.undo
python scripts\wwise_waapi.py ak.wwise.core.undo.redo

# Wrap multiple WAAPI edits into a single undo entry
python scripts\wwise_waapi.py ak.wwise.core.undo.beginGroup
# ... edits ...
python scripts\wwise_waapi.py ak.wwise.core.undo.endGroup
# or
python scripts\wwise_waapi.py ak.wwise.core.undo.cancelGroup
```

`beginGroup` / `endGroup` / `cancelGroup` nest. Always pair `beginGroup` with exactly one `endGroup` or `cancelGroup`.

## Blend container assignments

```powershell
python scripts\wwise_waapi.py ak.wwise.core.blendContainer.addAssignment '{
  "object": "{Blend-Track-GUID}",
  "child":  "{Child-of-Blend-Container-GUID}",
  "edges": [
    {"fadeMode":"Manual",  "fadeShape":"Linear", "edgePosition": 0.0,  "fadePosition": 0.2},
    {"fadeMode":"Manual",  "fadeShape":"Linear", "edgePosition": 100.0, "fadePosition": 80.0}
  ]
}'
```

Edges are only meaningful when the Blend Track has a crossfade Game Parameter; if so there must be exactly two (`0` left, `1` right). `fadeMode`: `None` / `Manual` / `Automatic`. `fadeShape` covers the same shapes as attenuation curves.

## Schema introspection (truth source)

When this skill's docs and Wwise's reality disagree, trust Wwise:

```powershell
python scripts\wwise_waapi.py ak.wwise.waapi.getFunctions
python scripts\wwise_waapi.py ak.wwise.waapi.getTopics
python scripts\wwise_waapi.py ak.wwise.waapi.getSchema '{"uri":"ak.wwise.core.object.set","includeExamples":true}'
```

The schema for any URI returns `argsSchema`, `optionsSchema`, `resultSchema`, optional `publishSchema` (for topics), and `examples`. This is the most reliable place to confirm an unfamiliar field shape.
