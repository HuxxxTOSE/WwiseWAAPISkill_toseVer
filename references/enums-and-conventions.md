# Enums, Units & Call Conventions

The cookbook shows *what* to send; this page covers the conventions that make a
call actually parse and mean what you intend: how to resolve the bare integers
(enums), how paths must be escaped, what units values are in, and the shape of
what comes back so you can VERIFY.

The golden rule for anything numeric or name-based you're unsure of: **don't
guess — introspect.** Two offline-safe authorities beat memory every time:

```powershell
# 1) Ask the property itself: type, default, range/enum, unit, override switch.
python scripts\wwise_waapi.py ak.wwise.core.object.getPropertyInfo '{"property":"Volume","object":"<path-or-guid>"}'
#    (or use "classId": <int> instead of "object")

# 2) Copy a value off an object already configured the way you want:
python scripts\wwise_waapi.py ak.wwise.core.object.get '{"waql":"$ from object \"<path>\""}' '{"return":["@ActionType","@RandomOrSequence"]}'
```

---

## 1. Path escaping (the #1 silent parse failure)

Wwise project paths use **backslashes**, and they live inside JSON, so every
separator must be a **double backslash**:

```jsonc
"object": "\\Actor-Mixer Hierarchy\\Default Work Unit\\MySound"   // correct
"object": "\Actor-Mixer Hierarchy\Default Work Unit\MySound"      // WRONG - invalid JSON / broken path
```

- A path always starts at a top category (`\\Actor-Mixer Hierarchy`, `\\Events`,
  `\\Interactive Music Hierarchy`, `\\Switches`, `\\Game Parameters`,
  `\\Master-Mixer Hierarchy`, `\\Attenuations`, …) and includes the Work Unit.
- Inside a **WAQL string that is itself inside JSON**, the quotes must be escaped
  too: `'{"waql":"$ from object \"\\\\Events\\\\Default Work Unit\\\\Play\""}'`.
- The null GUID `"{00000000-0000-0000-0000-000000000000}"` clears a reference.
- Prefer GUIDs over paths once resolved — they survive renames/moves.

---

## 2. Enums & magic numbers

Integer-valued properties (`@ActionType`, `@CueType`, `@RandomOrSequence`,
`@PlaylistItemType`, waveform selectors, …) are **0-based indices into that
property's option list** (the order you see in the Wwise dropdown, top to
bottom). The same integer can mean different things on different properties, so
resolve per-property, not from a global table.

**Authoritative resolution** (in order):
1. `getPropertyInfo` → for an enum, `restriction` describes the allowed set;
   `ui.dataMeaning` / `display` describe how it is shown.
2. Read the integer back off an existing, correctly-set object (see the `get`
   snippet at the top).
3. Only then fall back to the table below.

### Two different `ActionType`s — do not confuse them

| Where | Key | Meaning |
| --- | --- | --- |
| **Sound-engine** `executeActionOnEvent` (runtime playback control) | `actionType` | `0`=Stop, `1`=Pause, `2`=Resume, `3`=Break, `4`=ReleaseEnvelope |
| **Object model** Event *Action* object (authoring, via `create`/`set`) | `@ActionType` | Editor action-type enum; `1` = **Play** (as in the cookbook's `Play_SFX`). Others (Stop, Pause, SetVolume, SetSwitch, …) — confirm the exact int with `getPropertyInfo` on the `Action` classId. |

### Enums used in the cookbook

These are the integers that appear in [set-objects-cookbook.md](set-objects-cookbook.md).
Values marked "verify" should be confirmed with `getPropertyInfo` before relying
on them for anything other than the exact cookbook case:

| Property | Value in cookbook | Meaning |
| --- | --- | --- |
| `@ActionType` (Action) | `1` | Play |
| `@RandomOrSequence` (RandomSequenceContainer) | `1` | play mode (Random vs Sequence) — *verify orientation* |
| `@PlaylistItemType` (MusicPlaylistItem) | `1` | a **segment** leaf item; a **group** item omits `@Segment` and nests `children` |
| `@CueType` (MusicCue) | `2` | cue kind (Custom / Entry / Exit / …) — *verify* |
| `@LoopCount` (MusicPlaylistItem) | `0` | `0` = infinite loop |
| Curve `shape` | `"Linear"` | string enum, not an int: `Constant`, `Linear`, `Log1..3`, `SCurve`, `InvertedSCurve`, `Exp1..3` |

`classId` (e.g. `7733251`, `9699330`) identifies a **plug-in**, not an enum;
discover it with `get_all_object_types` (`ak.wwise.core.object.getTypes`) or by
reading `classId` off an existing instance.

Object **type codes** (the deprecated `from.id[].type` / class category ints you
may see in results): `10`=Event, `12`=SwitchGroup, `14`=StateGroup,
`17`=EffectPlugin, `18`=SoundBank, `19`=Bus, `20`=AuxBus, `22`=GameParameter,
`41`=Trigger, `68`=AudioDevicePlugin. Prefer WAQL type **names** over these.

---

## 3. Units

Values are **not** normalized — each property has its own unit, exposed by
`getPropertyInfo` under `ui.dataMeaning` (e.g. `"Decibels"`) and bounded by
`restriction` / `ui.value` (min/max/step). Common ones:

| Field | Unit |
| --- | --- |
| `@Volume`, output/aux-send volumes, attenuation curve `y` | decibels (dB) |
| `@Pitch` | cents |
| Lowpass / Highpass | 0–100 (percentage-like), not Hz |
| `@TimeMs`, `transitionDuration`, `fadeTime` | **milliseconds** |
| `audioSourceTrimValues.trimBegin/trimEnd`, `duration.min/max`, `originalDuration` | **seconds** |
| `loudness` (`integrated`, `momentaryMax`) | LUFS |
| Attenuation curve `x` (radius) | game units (metres, project-defined) |

When a value looks off by 1000×, you almost certainly mixed **ms vs seconds**.
Confirm with `getPropertyInfo` → `ui.dataMeaning` + `restriction`.

---

## 4. Response shapes — how to read results back (for VERIFY)

A missing exception is **not** proof of success. Know what each call returns:

| Call | Result shape | Notes |
| --- | --- | --- |
| `get` (`get_objects`) | `{ "return": [ { …requested fields… }, … ] }` | Empty `return` = query matched nothing (often a path/escaping bug). |
| `create` (`create_object`) | the created object's requested fields, e.g. `{ "id": "{…}", "name": "…" }` | Add `options.return` to get back `id`/`path`. |
| `set` (`set_objects`) | `{ "objects": [ … ], "logs": [ … ] }` | **Always inspect `logs`** — sub-edits can warn/fail while the transport call still "succeeds". |
| `getPropertyInfo` | `{ name, type, default, restriction, ui{…}, supports{rtpc,randomizer,unlink}, display{…} }` | `supports.unlink` = property can be per-platform; `restriction` = range/enum. |
| errors | a WAAPI error object (`uri`, `message`, sometimes `details`) | Also check `get_log_info` (`ak.wwise.core.log.get`) for the relevant channel. |

**Verify pattern:** after a write, `get` the same object back with the fields you
just set and compare, or `post_event` + profiler / `capture_screen` for audible/
visual proof. Back every success claim with a read-back, not an assumption.

---

## 5. Per-platform / linked values

Many properties can hold different values per platform. `getPropertyInfo`'s
`supports.unlink: true` marks these. To target one platform, pass `platform` in
the call; to check whether a property is currently linked (shared) or unlinked
(per-platform), use `is_object_linked` (`ak.wwise.core.object.isLinked`). If you
set a value without unlinking first, you may be editing the linked/all-platform
value rather than a single platform's.
