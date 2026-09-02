# WAAPI Procedure Catalogue

Complete URI list of WAAPI procedures used by this skill, grouped by domain. **Every URI here is callable with `python scripts/wwise_waapi.py <uri> <args-json> [options-json]`.** Argument signatures are the minimum needed to construct calls; for the authoritative schema use:

```powershell
python scripts/wwise_waapi.py ak.wwise.waapi.getSchema '{"uri":"<URI>","includeExamples":true}'
```

To list all procedures Wwise currently exposes:

```powershell
python scripts/wwise_waapi.py ak.wwise.waapi.getFunctions
python scripts/wwise_waapi.py ak.wwise.waapi.getTopics
```

---

## ak.wwise.core — object hierarchy

| URI | Args (key fields) |
| --- | --- |
| `ak.wwise.core.object.get` | `waql` (str). Options: `return` (list of accessors). |
| `ak.wwise.core.object.create` | `parent`, `type`, `name`, optional `onNameConflict` (`fail`/`replace`/`rename`/`merge`), `children`, `notes`, `platform`, `autoAddToSourceControl`. Property/reference accessors prefixed with `@` go inline. |
| `ak.wwise.core.object.delete` | `object`, `autoCheckOutToSourceControl?`. |
| `ak.wwise.core.object.set` | `objects` (list of dicts with `object` + `@<Property>` / `@<Reference>` / `@<List>` / `children` / `import`). Options: `return`. See [set-objects-cookbook.md](set-objects-cookbook.md). |
| `ak.wwise.core.object.copy` | `object`, `parent`, `onNameConflict?`. **Copying a Work Unit is irreversible and force-saves.** |
| `ak.wwise.core.object.move` | `object`, `parent`, `onNameConflict?`. |
| `ak.wwise.core.object.diff` | `source`, `target` → returns `properties` and `lists` deltas. |
| `ak.wwise.core.object.setProperty` | `object`, `property`, `value`, `platform?`. |
| `ak.wwise.core.object.setReference` | `object`, `reference`, `value` (GUID/path; null-GUID `{00000000-...}` clears). |
| `ak.wwise.core.object.setRandomizer` | `object`, `property`, `enabled`, `min?`, `max?`, `platform?`. |
| `ak.wwise.core.object.setStateGroups` | `object`, `stateGroups` (list of paths/GUIDs). |
| `ak.wwise.core.object.setStateProperties` | `object`, `stateProperties` (list of property names). See [state-properties.md](state-properties.md). |
| `ak.wwise.core.object.getPropertyAndReferenceNames` | `object?` or `classId?` (one required). |
| `ak.wwise.core.object.getPropertyInfo` | `property`, plus `object?` or `classId?`. |
| `ak.wwise.core.object.getTypes` | (no args) → all type names + class IDs. |
| `ak.wwise.core.object.isLinked` | `object`, `property`, `platform`. |
| `ak.wwise.core.object.getAttenuationCurve` | `object` (Attenuation), `curveType`, `platform?`. |
| `ak.wwise.core.object.setAttenuationCurve` | `object`, `curveType`, `use` (`None`/`Custom`/`UseVolumeDry`/`UseProject`), `points` (list of `{x,y,shape}`), `platform?`. |

Curve `shape` values: `Constant`, `Linear`, `Log1`, `Log2`, `Log3`, `SCurve`, `InvertedSCurve`, `Exp1`, `Exp2`, `Exp3`.

`curveType` values include `VolumeDryUsage`, `LowPassFilterUsage`, `HighPassFilterUsage`, `SpreadUsage`, `FocusUsage`, plus the obstruction/occlusion/diffraction/transmission `Volume|LPF|HPF` family.

---

## ak.wwise.core — audio / import

| URI | Args |
| --- | --- |
| `ak.wwise.core.audio.import` | `importOperation` (`createNew`/`useExisting`/`replaceExisting`), `imports` (list of import items — see [workflows/import-audio.md](../workflows/import-audio.md)). Options: `return`. |
| `ak.wwise.core.audio.solo` | `objects` (list), `value` (bool). |
| `ak.wwise.core.audio.mute` | `objects` (list), `value` (bool). |
| `ak.wwise.core.audio.resetSolo` | (no args). |
| `ak.wwise.core.audio.resetMute` | (no args). |
| `ak.wwise.core.audioSourcePeaks.getMinMaxPeaksInRegion` | `object`, `timeFrom`, `timeTo`, `numPeaks`, `getCrossChannelPeaks?`. |
| `ak.wwise.core.audioSourcePeaks.getMinMaxPeaksInTrimmedRegion` | `object`, `numPeaks`, `getCrossChannelPeaks?`. |
| `ak.wwise.core.sound.setActiveSource` | `sound` (parent Sound), `source` (child Source), `platform?`. |

---

## ak.wwise.core — SoundBank

| URI | Args |
| --- | --- |
| `ak.wwise.core.soundbank.generate` | `soundbanks?`, `platforms?`, `languages?`, `skipLanguages?`, `rebuildSoundBanks?`, `clearAudioFileCache?`, `writeToDisk?`, `rebuildInitBank?`. |
| `ak.wwise.core.soundbank.getInclusions` | `soundbank` (path/GUID). |
| `ak.wwise.core.soundbank.setInclusions` | `soundbank`, `operation` (`add`/`remove`/`replace`), `inclusions` (list of `{object, filter:[events|structures|media]}`). |

---

## ak.wwise.core — Profiler

| URI | Args |
| --- | --- |
| `ak.wwise.core.profiler.startCapture` | (no args) → returns ms cursor. |
| `ak.wwise.core.profiler.stopCapture` | (no args) → returns ms cursor. |
| `ak.wwise.core.profiler.saveCapture` | `file` (.prof path). |
| `ak.wwise.core.profiler.enableProfilerData` | `dataTypes`: list of `{dataType, enable}`. Types: `cpu`, `memory`, `stream`, `voices`, `listener`, `obstructionOcclusion`, `markersNotification`, `soundbanks`, `loadedMedia`, `preparedObjects`, `preparedGameSyncs`, `interactiveMusic`, `streamingDevice`, `meter`, `auxiliarySends`, `apiCalls`, `spatialAudio`, `spatialAudioRaycasting`, `voiceInspector`, `audioObjects`, `gameSyncs`. |
| `ak.wwise.core.profiler.getCursorTime` | `cursor` (`user` or `capture`). |
| `ak.wwise.core.profiler.getCpuUsage` | `time`. |
| `ak.wwise.core.profiler.getPerformanceMonitor` | `time`. |
| `ak.wwise.core.profiler.getVoices` | `time`, `voicePipelineID?`. Options: `return`. |
| `ak.wwise.core.profiler.getVoiceContributions` | `voicePipelineID`, `time`, `bussesPipelineID?`. |
| `ak.wwise.core.profiler.getBusses` | `time`, `busPipelineID?`. Options: `return`. |
| `ak.wwise.core.profiler.getAudioObjects` | `time`, `busPipelineID?`. Options: `return`. |
| `ak.wwise.core.profiler.getRTPCs` | `time`. |
| `ak.wwise.core.profiler.getGameObjects` | `time`. |
| `ak.wwise.core.profiler.getLoadedMedia` | `time`. |
| `ak.wwise.core.profiler.getStreamedMedia` | `time`. |
| `ak.wwise.core.profiler.getMeters` | `time`. Options: `return`, `platform`, `language`. |
| `ak.wwise.core.profiler.registerMeter` | `object` (bus/auxBus/device). |
| `ak.wwise.core.profiler.unregisterMeter` | `object`. |

`time` is either an integer (ms) or one of the strings `"user"` / `"capture"`.

---

## ak.wwise.core — project / global / log / undo / source control

| URI | Args |
| --- | --- |
| `ak.wwise.core.ping` | (no args) → `{isAvailable: bool}`. |
| `ak.wwise.core.getInfo` | (no args). |
| `ak.wwise.core.getProjectInfo` | (no args). |
| `ak.wwise.core.log.get` | `channel` (`general`/`soundbankGenerate`/`conversion`/`projectLoad`/`waapi`/`sourceControl`/`copyPlatformSettings`/`lua`). |
| `ak.wwise.core.project.save` | `autoCheckOutToSourceControl?` (default true). |
| `ak.wwise.core.undo.undo` | (no args). |
| `ak.wwise.core.undo.redo` | (no args). |
| `ak.wwise.core.undo.beginGroup` | (no args) — pair with `endGroup`. Nestable. |
| `ak.wwise.core.undo.endGroup` | (no args). |
| `ak.wwise.core.undo.cancelGroup` | (no args). |
| `ak.wwise.core.blendContainer.addAssignment` | `object` (Blend Track), `child`, `index?`, `edges?` (list of `{fadeMode, fadeShape, edgePosition, fadePosition?}`). |

---

## ak.soundengine — runtime control

These hit the connected sound engine (Wwise authoring tools' built-in player) rather than the editor model.

| URI | Args |
| --- | --- |
| `ak.soundengine.postEvent` | `event` (GUID/name/shortId), `gameObject` (uint64). |
| `ak.soundengine.executeActionOnEvent` | `event`, `actionType` (0–4), `gameObject`, `transitionDuration?`, `fadeCurve?`. |
| `ak.soundengine.stopAll` | `gameObject?`. |
| `ak.soundengine.stopPlayingID` | `playingID`, `transitionDuration?`, `fadeCurve?`. |
| `ak.soundengine.seekOnEvent` | `event`, `position` (ms or % depending on `inPercent`), `gameObject?`, `seekToNearestMarker?`, `playingID?`, `inPercent?`. |
| `ak.soundengine.setRTPCValue` | `rtpc` (GUID/name), `value` (float), `gameObject?`. |
| `ak.soundengine.resetRTPCValue` | `rtpc`, `gameObject?`. |
| `ak.soundengine.setState` | `stateGroup`, `state`. |
| `ak.soundengine.getState` | `stateGroup`. Options: `return`. |
| `ak.soundengine.setSwitch` | `switchGroup`, `switchState`, `gameObject`. |
| `ak.soundengine.getSwitch` | `switchGroup`, `gameObject`. |
| `ak.soundengine.postTrigger` | `trigger`, `gameObject`. |
| `ak.soundengine.registerGameObj` | `gameObject` (uint64), `name?`. |
| `ak.soundengine.unregisterGameObj` | `gameObject`. |
| `ak.soundengine.setPosition` | `gameObject`, `position` (`{x,y,z}` orientation+position struct). |
| `ak.soundengine.setMultiplePositions` | `gameObject`, `positions` (list), `multiPositionType?`. |
| `ak.soundengine.setListeners` | `emitter` (gameObject), `listeners` (list). |
| `ak.soundengine.setDefaultListeners` | `listeners`. |
| `ak.soundengine.setListenerSpatialization` | `listener`, `spatialized`, `channelConfig?`, `volumeOffsets?`. |
| `ak.soundengine.setGameObjectAuxSendValues` | `gameObject`, `auxSendValues` (list). |
| `ak.soundengine.setGameObjectOutputBusVolume` | `emitter`, `listener`, `controlValue`. |
| `ak.soundengine.setObjectObstructionAndOcclusion` | `gameObject`, `listener`, `obstructionLevel`, `occlusionLevel`. |
| `ak.soundengine.setScalingFactor` | `gameObject`, `attenuationScalingFactor`. |
| `ak.soundengine.loadBank` | `soundBank` (name/shortId). |
| `ak.soundengine.unloadBank` | `soundBank`. |
| `ak.soundengine.postMsgMonitor` | `message` (string). |

---

## ak.wwise.ui — UI commands, layouts, capture

| URI | Args |
| --- | --- |
| `ak.wwise.ui.commands.execute` | `command` (id), `objects?`, `platforms?`, `value?`. |
| `ak.wwise.ui.commands.getCommands` | (no args). |
| `ak.wwise.ui.commands.register` | `commands` (list of definitions — see workflows/ui-and-layout.md). |
| `ak.wwise.ui.commands.unregister` | `commands` (list of IDs). |
| `ak.wwise.ui.getSelectedObjects` | Options: `return`, `platform`, `language`. |
| `ak.wwise.ui.project.open` | `path` (.wproj), `onMigrationRequired?` (`migrate`/`fail`), `bypassSave?`, `autoCheckOutToSourceControl?`. |
| `ak.wwise.ui.project.close` | `bypassSave?`. |
| `ak.wwise.ui.project.create` | `path`, `platforms?`, `languages?`. |
| `ak.wwise.ui.layout.getLayout` | `name`. |
| `ak.wwise.ui.layout.getLayoutNames` | (no args). |
| `ak.wwise.ui.layout.getCurrentLayoutName` | (no args). |
| `ak.wwise.ui.layout.setLayout` | `name`, `layout` (full Layout dict). |
| `ak.wwise.ui.layout.switchLayout` | `name`. |
| `ak.wwise.ui.layout.removeLayout` | `name`. |
| `ak.wwise.ui.layout.getViewTypes` | (no args). |
| `ak.wwise.ui.layout.getViewInstances` | `name`. |
| `ak.wwise.ui.layout.getOrCreateView` | `name`, `posX?`, `posY?`. |
| `ak.wwise.ui.layout.dockView` | `name`, `viewID`, `targetID`, `side`. |
| `ak.wwise.ui.layout.undockView` | `name`, `viewID`, `posX?`, `posY?`. |
| `ak.wwise.ui.layout.moveSplitter` | `id`, `delta`. |
| `ak.wwise.ui.layout.getElementRectangle` | `id`. |
| `ak.wwise.ui.captureScreen` | `viewName?`, `viewSelectionChannel?`, `rect?` (`{x,y,width,height}`). Returns `{contentType, contentBase64}`. |

---

## ak.wwise.console (CLI mode only)

| URI | Args |
| --- | --- |
| `ak.wwise.console.project.close` | (no args). Use only when working with a WwiseConsole-launched project. Default close = `ak.wwise.ui.project.close`. |

---

## ak.wwise.waapi — meta / introspection

| URI | Args |
| --- | --- |
| `ak.wwise.waapi.getFunctions` | (no args). |
| `ak.wwise.waapi.getTopics` | (no args). |
| `ak.wwise.waapi.getSchema` | `uri`, `includeExamples?`. |

Use these whenever you need to verify a procedure's exact schema rather than guessing from this file.
