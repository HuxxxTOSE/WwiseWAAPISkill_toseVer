# Object Types & `<nodeType>` Tags

When creating objects through `ak.wwise.core.audio.import` (and inside path arguments to `ak.wwise.core.object.set` `import` blocks), missing path segments are auto-created. To pin the type of an auto-created segment, wrap the type in angle brackets in front of the segment name.

## Path syntax

```
\Actor-Mixer Hierarchy\Default Work Unit\<Random Container>MyContainer\<Sound SFX>MySound
```

- Backslashes separate segments (in JSON strings, escape as `\\`).
- A bare segment (`MyContainer`) refers to an existing object; if absent, Wwise picks a default type for that location.
- A `<Type>Name` segment forces the new object's type.

## Valid `<nodeType>` tags

```
<Work Unit>
<Actor-Mixer>
<Virtual Folder>
<Physical Folder>
<Sound SFX>
<Sound Voice>
<Switch Container>
<Random Container>
<Sequence Container>
<Blend Container>
<Music Playlist Container>
<Music Switch Container>
<Music Segment>
<Music Track>
<Event>
<SoundBank>
```

For `ak.wwise.core.object.create`, the **type is a separate `type` argument** and uses the bare type name (no angle brackets). Common values include:

```
Sound, RandomSequenceContainer, SwitchContainer, BlendContainer,
ActorMixer, Folder, WorkUnit,
MusicSegment, MusicTrack, MusicSwitchContainer, MusicPlaylistContainer,
Event, Action, AuxBus, Bus, SoundBank, Attenuation, Curve,
RTPC, EffectSlot, Effect, SourcePlugin, MultiSwitchEntry, MusicPlaylistItem
```

## Discovering all type names live

```powershell
python scripts\waapi.py ak.wwise.core.object.getTypes
```

Returns each type's `name` and `classId` — the latter is what some payloads (e.g. effect/source plug-in placement) need.

## Class IDs you'll commonly need

`classId` is required when you want `set_objects` to create an `Effect` or `SourcePlugin` of a specific plug-in. Discover them with `getTypes`, or read them off an existing instance with WAQL:

```
$ from object "\Effects\Default Work Unit\MyReverb" select this
```

Then ask for `classId` in the `return` option.

Examples used in the cookbook: `7733251` (a particular reverb), `9699330` (Wwise SynthOne).
