# Import Audio Files

`ak.wwise.core.audio.import` ingests one or many WAV files, optionally creating Sound / container / Event hierarchies in the same call. It's the right tool whenever audio assets need to land in the project — for editing existing structures only, prefer `set_objects` with an inline `import` block.

## Call shape

```powershell
python scripts\wwise_waapi.py ak.wwise.core.audio.import '{
  "importOperation": "useExisting",
  "imports": [
    {
      "objectPath": "\\Actor-Mixer Hierarchy\\Default Work Unit\\Footsteps\\<Random Container>Foot_Walk\\<Sound SFX>Foot_Walk_01",
      "audioFile": "C:\\Audio\\foot_walk_01.wav",
      "originalsSubFolder": "Player\\Footsteps",
      "@Volume": -3
    }
  ]
}' '{"return":["id","name","path","type"]}'
```

`importOperation`:

- `createNew` — name collision → unique-rename the new object.
- `useExisting` — name collision → keep existing object, only update specified attributes (idempotent re-runs).
- `replaceExisting` — name collision → delete existing, recreate.

## Each `imports[]` item

| Field | Notes |
| --- | --- |
| `objectPath` *(required)* | Full path. Missing segments are auto-created. Use `<NodeType>Name` to pin a segment's type — see [../references/object-types.md](../references/object-types.md). |
| `audioFile` | Absolute path to a WAV (or supported source). Optional only when the entry is purely a container creation. |
| `audioFileBase64` | Inline file content (base64). Useful when the WAV isn't on a path Wwise can read. |
| `importLanguage` | Required for Voice sounds. Must be a project-supported language (`English(US)`, `French(France)`, `Mandarin Chinese(China)`, …). |
| `originalsSubFolder` | Subfolder under `Originals/` where Wwise stores the master copy. e.g. `"Player\\Footsteps"`. |
| `notes` / `audioSourceNotes` | Notes for the Sound and the AudioSource respectively. |
| `event` | Auto-create an Event for the imported Sound. Provide the full path: `"\\Events\\Default Work Unit\\Play_Foot_Walk"`. |
| `dialogueEvent` | Auto-create a Dialogue Event for the imported Voice. |
| `@<Property>` / `@<Reference>` | Inline accessors on the created Sound. Override switches still required. |

## Idempotent batch import (the typical case)

```powershell
python scripts\wwise_waapi.py ak.wwise.core.audio.import '{
  "importOperation": "useExisting",
  "imports": [
    {"objectPath": "\\Actor-Mixer Hierarchy\\Default Work Unit\\UI\\<Sound SFX>Click", "audioFile": "C:\\sfx\\click.wav", "event": "\\Events\\Default Work Unit\\Play_Click"},
    {"objectPath": "\\Actor-Mixer Hierarchy\\Default Work Unit\\UI\\<Sound SFX>Hover", "audioFile": "C:\\sfx\\hover.wav", "event": "\\Events\\Default Work Unit\\Play_Hover"}
  ]
}' '{"return":["id","name","path","type"]}'
```

Re-running the same call with `useExisting` updates audio for already-present objects without duplicates — safe in build pipelines.

## Voice import

```json
{
  "objectPath": "\\Actor-Mixer Hierarchy\\Default Work Unit\\NPC\\Greeting\\<Sound Voice>Hello_FR",
  "audioFile": "C:\\voice\\fr\\hello.wav",
  "importLanguage": "French(France)",
  "originalsSubFolder": "NPC\\Greeting"
}
```

Each language requires its own entry — Wwise creates one AudioSource per (Voice, language) pair.

## Importing inside a complex structure

If you're already constructing a Music Switch Container or similar, skip the standalone import call and embed an `import` block inside the leaf entry of `set_objects`. Example in [../references/set-objects-cookbook.md](../references/set-objects-cookbook.md) recipe #4.

## Solo / Mute control (audition aid)

```powershell
python scripts\wwise_waapi.py ak.wwise.core.audio.solo '{"objects":["\\Actor-Mixer Hierarchy\\Default Work Unit\\UI\\Click"], "value": true}'
python scripts\wwise_waapi.py ak.wwise.core.audio.mute '{"objects":["..."], "value": true}'
python scripts\wwise_waapi.py ak.wwise.core.audio.resetSolo
python scripts\wwise_waapi.py ak.wwise.core.audio.resetMute
```

Reset variants clear all solo/mute state across the project.

## Audio source peaks (waveform inspection)

For drawing a waveform or detecting silence:

```powershell
python scripts\wwise_waapi.py ak.wwise.core.audioSourcePeaks.getMinMaxPeaksInTrimmedRegion '{"object":"<AudioSource path/GUID>","numPeaks":1024}'
python scripts\wwise_waapi.py ak.wwise.core.audioSourcePeaks.getMinMaxPeaksInRegion '{"object":"<AudioSource>","timeFrom":0.0,"timeTo":1.5,"numPeaks":256}'
```

Returns base64-encoded interleaved 16-bit min/max pairs per channel. Decode with NumPy:

```python
import base64, numpy as np
raw = base64.b64decode(peaksBinaryStrings[0])
peaks = np.frombuffer(raw, dtype=np.int16).reshape(-1, 2) / maxAbsValue
```

## Switching the active source on a Sound

```powershell
python scripts\wwise_waapi.py ak.wwise.core.sound.setActiveSource '{"sound":"<Sound>", "source":"<AudioSource child of the Sound>"}'
```

Useful when a Sound has multiple Audio Sources (variants / language editions) and you need to programmatically pick the active one.
