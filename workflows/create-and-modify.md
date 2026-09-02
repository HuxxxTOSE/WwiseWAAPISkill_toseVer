# Create, Modify, and Delete Wwise Objects

Three escalating tools cover the entire create/edit surface:

1. **`ak.wwise.core.object.create`** — single object, optional accessors / children.
2. **`ak.wwise.core.object.set`** — batch edits; the powerhouse. Reach for this whenever you would otherwise issue 2+ create/setProperty/setReference calls.
3. **`setProperty` / `setReference` / `setRandomizer` / `setStateGroups` / `setStateProperties`** — narrow, single-axis edits.

Plus structural moves: `move`, `copy`, `delete`, `diff`.

For payload shapes, load [../references/set-objects-cookbook.md](../references/set-objects-cookbook.md). For node tags in paths, [../references/object-types.md](../references/object-types.md).

## Create one object

```powershell
python scripts\wwise_waapi.py ak.wwise.core.object.create '{
  "parent": "\\Actor-Mixer Hierarchy\\Default Work Unit",
  "type": "RandomSequenceContainer",
  "name": "MyContainer",
  "onNameConflict": "rename",
  "children": [
    {"type": "Sound", "name": "Variant_A"},
    {"type": "Sound", "name": "Variant_B"}
  ]
}'
```

`onNameConflict`: `fail` (default), `rename`, `replace`, `merge`.

Inline accessors: any `@<Property>` / `@<Reference>` key in the entry is applied at creation time. Override switches must be set in the same call (`@OverridePositioning: true` before `@Positioning_*`).

## Batch set / create

`ak.wwise.core.object.set` accepts a list of "root entries", each addressing an existing object via `object` (path or GUID). Within each entry you may rename, set properties, set references, replace lists, and create children — recursively.

```powershell
python scripts\wwise_waapi.py ak.wwise.core.object.set '{
  "objects": [
    {
      "object": "{1514A4D8-1DA6-412A-A17E-75CA0C2149F3}",
      "name": "RenamedSound",
      "@Volume": -6,
      "@OverrideOutput": true,
      "@OutputBus": "\\Master-Mixer Hierarchy\\Default Work Unit\\Master Audio Bus\\SFX"
    }
  ]
}' '{"return":["id","name","path","@Volume"]}'
```

The skill ships a cookbook with seven canonical patterns including curve assignment, Music container construction, plug-in instantiation, and conflict-policy combinations: see [../references/set-objects-cookbook.md](../references/set-objects-cookbook.md).

### `listMode`

Default behavior on a list-typed accessor (`@RTPC`, `@Effects`, `@Cues`, …) is `append`. Pass `"listMode": "replaceAll"` on the root entry to wipe the list before applying.

### Inspect logs in the response

`ak.wwise.core.object.set` returns `{"objects": [...], "logs": [...]}` (when sub-operations warned/failed). Always check `logs` — the call can succeed at the transport layer while individual edits silently misbehaved.

## Single-axis edits

Use these only when one or two trivial values change. Otherwise prefer `set_objects` for atomicity.

```powershell
# Set a single property
python scripts\wwise_waapi.py ak.wwise.core.object.setProperty '{"object":"<path>","property":"Volume","value":-3}'

# Set a reference (or clear it with the null GUID)
python scripts\wwise_waapi.py ak.wwise.core.object.setReference '{"object":"<path>","reference":"Attenuation","value":"\\Attenuations\\Default Work Unit\\MyAtt"}'
python scripts\wwise_waapi.py ak.wwise.core.object.setReference '{"object":"<path>","reference":"Attenuation","value":"{00000000-0000-0000-0000-000000000000}"}'

# Property randomizer
python scripts\wwise_waapi.py ak.wwise.core.object.setRandomizer '{"object":"<path>","property":"Volume","enabled":true,"min":-3,"max":3}'

# State groups + state columns
python scripts\wwise_waapi.py ak.wwise.core.object.setStateGroups '{"object":"<path>","stateGroups":["\\States\\Default Work Unit\\MoodGroup"]}'
python scripts\wwise_waapi.py ak.wwise.core.object.setStateProperties '{"object":"<path>","stateProperties":["Volume","Pitch","Lowpass"]}'
```

## Move / copy / delete / diff

```powershell
# Move
python scripts\wwise_waapi.py ak.wwise.core.object.move '{"object":"<src>","parent":"<dst-parent>","onNameConflict":"rename"}'

# Copy (WARNING: copying a Work Unit is irreversible AND force-saves the project)
python scripts\wwise_waapi.py ak.wwise.core.object.copy '{"object":"<src>","parent":"<dst-parent>","onNameConflict":"rename"}'

# Delete
python scripts\wwise_waapi.py ak.wwise.core.object.delete '{"object":"<path-or-guid>"}'

# Compare two objects' properties + lists
python scripts\wwise_waapi.py ak.wwise.core.object.diff '{"source":"<a>","target":"<b>"}'
```

## Attenuation curves

```powershell
python scripts\wwise_waapi.py ak.wwise.core.object.getAttenuationCurve '{"object":"\\Attenuations\\Default Work Unit\\MyAtt","curveType":"VolumeDryUsage"}'

python scripts\wwise_waapi.py ak.wwise.core.object.setAttenuationCurve '{
  "object":"\\Attenuations\\Default Work Unit\\MyAtt",
  "curveType":"VolumeDryUsage",
  "use":"Custom",
  "points":[
    {"x":0,"y":0,"shape":"Linear"},
    {"x":50,"y":-12,"shape":"Log3"},
    {"x":100,"y":-200,"shape":"Constant"}
  ]
}'
```

`curveType` includes `VolumeDryUsage`, `LowPassFilterUsage`, `HighPassFilterUsage`, `SpreadUsage`, `FocusUsage`, plus the obstruction/occlusion/diffraction/transmission `Volume|LPF|HPF` family. `shape` values in [../references/waapi-procedures.md](../references/waapi-procedures.md).

## Group edits under one undo entry

When a batch of writes should appear as a single user-undoable step, wrap them with the undo group procedures:

```powershell
python scripts\wwise_waapi.py ak.wwise.core.undo.beginGroup
# ... your edits ...
python scripts\wwise_waapi.py ak.wwise.core.undo.endGroup
```

Pair every `beginGroup` with exactly one `endGroup` (or `cancelGroup` to roll back). They nest. Across multiple `waapi.py` invocations this works because the wrapper opens a fresh connection per process — but the undo group lives in Wwise, not in the client, so it spans calls. Still, prefer running grouped edits inside a single Python script for atomicity.

## Override switches — the recurring trap

Many properties don't surface their value until the corresponding override flag is on:

| Override | Gates |
| --- | --- |
| `@OverridePositioning` | Speaker / 3D positioning fields, Attenuation enable. |
| `@OverrideOutput` | `OutputBus`, `OutputBusVolume`. |
| `@OverrideUserAuxSends` | `UserAuxSendVolume0..3`, `UserAuxSendHPF/LPF`. |
| `@OverrideGameAuxSends` | `GameAuxSendVolume`, `GameAuxSendHPF/LPF`. |
| `@OverrideEarlyReflections` | `ReflectionsVolume`. |
| `@OverrideHdrEnvelope` | `HdrEnableEnvelope`, `HdrActiveRange`. |
| `@OverrideMidiNoteTracking` | `MidiNoteTracking*` fields. |
| `@OverrideMidiTempoSource` | `MidiTempoSource`. |
| `@OverrideMidiTargetNode` | `MidiTargetNode`. |
| `@OverrideAdvancedSettings` | Several priority / virtual-voice settings. |

Always set the override boolean **in the same `set_objects` entry** as the gated value. If unsure which switch governs a property:

```powershell
python scripts\wwise_waapi.py ak.wwise.core.object.getPropertyInfo '{"property":"OutputBusVolume","object":"<path>"}'
```

The response indicates the override property name when one exists.
