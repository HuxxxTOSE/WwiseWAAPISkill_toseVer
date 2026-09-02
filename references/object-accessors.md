# Object Accessors (Properties & References)

The accessors listed here are the *common* surface — usable both in WAQL `where` / `select` clauses and in the `return` option of `ak.wwise.core.object.get` / `ak.wwise.core.object.set`. Type-specific properties (e.g. effect-plugin parameters) are discoverable with:

```powershell
python scripts\wwise_waapi.py ak.wwise.core.object.getPropertyAndReferenceNames '{"object":"<path-or-guid>"}'
python scripts\wwise_waapi.py ak.wwise.core.object.getPropertyInfo '{"property":"Volume","object":"<path>"}'
```

## Accessor expression grammar

- `<reference>` — `parent`, `descendants`, `workunit`, …
- `<reference>.<reference>` — chains, e.g. `parent.parent`.
- `<property>` — scalar field, e.g. `name`, `volume`.
- `<property>.<key>` — for dict-valued properties, e.g. `duration.min`, `audioSourceTrimValues.trimBegin`.
- `<reference>.<property>` — e.g. `descendants.audioSourceTrimValues`, `randomizer("Volume").min`.

## References (apply to all objects unless noted)

| Accessor | Returns |
| --- | --- |
| `children` | Direct children only. |
| `parent` | Direct parent. |
| `ancestors` | All ancestors recursively (excludes self). |
| `descendants` | All descendants recursively (excludes self). |
| `this` | The object itself (useful in `select this, descendants`). |
| `referencesTo` | Every object that references this one. |
| `owner` | Owner object — only present for `Custom` objects defined inside another. |
| `workunit` | The Work Unit storing this object. |
| `randomizer("PROPERTY_NAME")` | Randomizer object for a property. Sub-keys: `min`, `max`, `enabled`. |

Hierarchy-only references:

| Accessor | Applies to | Returns |
| --- | --- | --- |
| `maxDurationSource` | Actor-Mixer / Interactive-Music / Event objects | AudioSource with the largest duration: `{id, duration}`. |
| `maxDurationSourceObject` | same | `{id, name}`. |
| `maxRadiusAttenuation` | same | Attenuation with largest radius: `{id, radius}`. |
| `maxRadiusAttenuationObject` | same | `{id, name}`. |
| `audioSourceLanguage` | AudioSource | The language object. |
| `switchContainerChildContext` | SwitchContainer children | The Switch context object. |
| `panner` | Positioning-capable objects | Speaker Panner: `{id}`. |

## Common properties

### All objects

`id`, `shortId`, `name`, `path`, `type`, `nodeType`, `classId`, `category`, `notes`, `activeSource`, `pluginName`, `filePath`, `isPlayable`, `childrenCount`, `isExplicitMute`, `isExplicitSolo`, `isImplicitMute`, `isImplicitSolo`, `isIncluded`, `stateProperties` (list), `stateGroups` (list).

### Sound / AudioSource

`originalFilePath`, `loudness` (`{integrated, momentaryMax}` LUFS), `audioSourceTrimValues` (`{trimBegin, trimEnd}` seconds).

### Sound / AudioSource / MusicClip / PluginMedia (file metadata)

`originalRelativeFilePath`, `originalChannelConfig`, `originalChannelMask`, `originalSampleRate`, `originalBitDepth`, `originalFileSize`, `originalDataSize`, `originalSampleCount`, `originalDuration`, `originalCodec`, plus the parallel `original*` channel-count fields and the matching `converted*` set (`convertedChannelConfig`, `convertedSampleRate`, `convertedDuration`, `convertedCodec`, …).

### Work Unit

`workunitIsDefault`, `workunitType` (`nestedFile` / `rootFile` / `folder`), `workunitIsDirty`.

### Effect Slot / Event / Action

`validity` — `{isValid, details, severity}`.

### SoundBank

`soundbankBnkFilePath` — absolute path to the generated `.bnk`.

### Containers of AudioSource (recursive)

`duration` — `{min, max, type}`. `type` is `Infinite`, `Mixed`, `OneShot`, or `Unknown`.

### AudioSource / MidiFileSource / PluginMediaSource

`mediaId`, `conversionHash`, `contentHash`.

## Using accessors in `set_objects` payloads

Inside a `set_objects` entry, accessors are prefixed with `@`:

- `@<Property>: value` — set a property.
- `@<Reference>: "<path-or-guid>"` — bind a reference.
- `@<Reference>: "{00000000-0000-0000-0000-000000000000}"` — clear a reference.
- `@<Reference>: { "type": ..., "name": ..., "@..." }` — create a referenced object inline.
- `@<List>: [...]` — assign a list (existing items) or create entries.

**Override switches**: many properties (positioning, attenuation, output bus, etc.) are gated by an `@OverrideXxx` boolean. Set the override true in the same payload; otherwise the underlying field stays hidden in the editor and your assignment may be ignored. Use `getPropertyInfo` to confirm which switch controls a given property.

See [set-objects-cookbook.md](set-objects-cookbook.md) for canonical examples.
