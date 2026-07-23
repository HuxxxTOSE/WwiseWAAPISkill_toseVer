# Property Names Usable as State Columns

Properties below can be passed in `stateProperties` to `ak.wwise.core.object.setStateProperties` for the matching object type. They become the visible columns in the object's States tab and can be driven by State Groups associated via `setStateGroups`.

> Setting `stateProperties` **replaces all previous columns**, including the defaults. Re-add anything you want to keep.

## Bus

`BusVolume`, `BypassEffect`, `EnableAttenuation`, `GameAuxSendHPF`, `GameAuxSendLPF`, `GameAuxSendVolume`, `Highpass`, `Lowpass`, `MakeUpGain`, `OutputBusHighpass`, `OutputBusLowpass`, `OutputBusVolume`, `Pitch`, `ReflectionsVolume`, `UserAuxSendHPF0..3`, `UserAuxSendLPF0..3`, `UserAuxSendVolume0..3`, `Volume`.

## AuxBus

`BusVolume`, `BypassEffect`, `EnableAttenuation`, `GameAuxSendHPF`, `GameAuxSendLPF`, `GameAuxSendVolume`, `OutputBusHighpass`, `OutputBusLowpass`, `OutputBusVolume`, `ReflectionsVolume`, `UserAuxSendHPF0..3`, `UserAuxSendLPF0..3`, `UserAuxSendVolume0..3`.

## ActorMixer

`BypassEffect`, `EnableAttenuation`, `GameAuxSendHPF`, `GameAuxSendLPF`, `GameAuxSendVolume`, `Highpass`, `Lowpass`, `MakeUpGain`, `MidiTransposition`, `MidiVelocityOffset`, `OutputBusHighpass`, `OutputBusLowpass`, `OutputBusVolume`, `Pitch`, `Priority`, `ReflectionsVolume`, `UserAuxSendHPF0..3`, `UserAuxSendLPF0..3`, `UserAuxSendVolume0..3`, `Volume`.

## Sound / SwitchContainer / RandomSequenceContainer / BlendContainer

The same set as ActorMixer, plus `InitialDelay`. RandomSequenceContainer also has `PlayMechanismSpecialTransitionsValue`.

## MusicSwitchContainer / MusicPlaylistContainer / MusicSegment

`BypassEffect`, `EnableAttenuation`, `GameAuxSendHPF`, `GameAuxSendLPF`, `GameAuxSendVolume`, `Highpass`, `Lowpass`, `MakeUpGain`, `OutputBusHighpass`, `OutputBusLowpass`, `OutputBusVolume`, `Priority`, `ReflectionsVolume`, `UserAuxSendHPF0..3`, `UserAuxSendLPF0..3`, `UserAuxSendVolume0..3`, `Volume`.

(Music containers omit `Pitch`, `MidiTransposition`, `MidiVelocityOffset`, `InitialDelay`.)

## Other types

For any object type not covered here, query live:

```powershell
python scripts\waapi.py ak.wwise.core.object.getPropertyAndReferenceNames '{"object":"<path>"}'
```

Then cross-check each candidate with `getPropertyInfo` — the response indicates whether the property is state-capable.
