# Transport, Sound Engine Runtime, RTPC / State / Switch

`ak.soundengine.*` procedures hit the **sound engine** running inside Wwise Authoring (the same engine the Transport view drives). Use them to audition events, drive RTPC values for live preview, set states/switches, and inspect runtime behavior — without an external game.

## Game objects (mandatory for most calls)

The sound engine routes events to game objects identified by an unsigned 64-bit integer. You can use any value (e.g. `1`, `12345`); just keep it consistent across related calls.

```powershell
python scripts\waapi.py ak.soundengine.registerGameObj '{"gameObject": 1, "name": "Audition"}'
python scripts\waapi.py ak.soundengine.unregisterGameObj '{"gameObject": 1}'
```

Most procedures accept an unregistered game object too; explicit registration with a name makes the Profiler's Game Object view far more readable.

## Post events

```powershell
# By name
python scripts\waapi.py ak.soundengine.postEvent '{"event": "Play_Click", "gameObject": 1}'

# By Short ID (uint32)
python scripts\waapi.py ak.soundengine.postEvent '{"event": 245489792, "gameObject": 1}'

# By GUID
python scripts\waapi.py ak.soundengine.postEvent '{"event": "{F546017D-201A-49BD-8D4E-0A28F5DBB28D}", "gameObject": 1}'
```

Returns `playingID` (uint64) — keep it if you need to stop or seek the specific instance.

## Stop / pause / resume

```powershell
# Stop everything on a game object (or all of it if gameObject omitted)
python scripts\waapi.py ak.soundengine.stopAll '{"gameObject": 1}'

# Stop a specific instance
python scripts\waapi.py ak.soundengine.stopPlayingID '{"playingID": <id>, "transitionDuration": 250, "fadeCurve": 4}'

# Run any of the standard event actions on the targets of an event
# actionType: 0=Stop, 1=Pause, 2=Resume, 3=Break, 4=ReleaseEnvelope
python scripts\waapi.py ak.soundengine.executeActionOnEvent '{"event":"Play_Click","actionType":1,"gameObject":1,"transitionDuration":100,"fadeCurve":4}'
```

`fadeCurve` values follow `AkCurveInterpolation` (0–9). Default 4 ≈ Linear.

## Seek

```powershell
# Seek to 1500 ms
python scripts\waapi.py ak.soundengine.seekOnEvent '{"event":"Play_Music","position":1500,"gameObject":1}'

# Seek to 25% of the playback length
python scripts\waapi.py ak.soundengine.seekOnEvent '{"event":"Play_Music","position":25,"gameObject":1,"inPercent":true,"seekToNearestMarker":true}'
```

## RTPC (Game Parameter)

```powershell
# Set a global RTPC
python scripts\waapi.py ak.soundengine.setRTPCValue '{"rtpc": "Distance", "value": 25.0}'

# Per-game-object override
python scripts\waapi.py ak.soundengine.setRTPCValue '{"rtpc": "Distance", "value": 25.0, "gameObject": 1}'

python scripts\waapi.py ak.soundengine.resetRTPCValue '{"rtpc": "Distance"}'
```

## State

```powershell
python scripts\waapi.py ak.soundengine.setState '{"stateGroup": "MoodGroup", "state": "Tense"}'
python scripts\waapi.py ak.soundengine.getState '{"stateGroup": "MoodGroup"}' '{"return":["id","name"]}'
```

There's a ≤10 ms propagation delay; immediate `getState` after `setState` may still report the previous value.

## Switch

```powershell
python scripts\waapi.py ak.soundengine.setSwitch '{"switchGroup": "Surface", "switchState": "Wood", "gameObject": 1}'
python scripts\waapi.py ak.soundengine.getSwitch '{"switchGroup": "Surface", "gameObject": 1}'
```

## Trigger

```powershell
python scripts\waapi.py ak.soundengine.postTrigger '{"trigger": "MyTrigger", "gameObject": 1}'
```

## Positioning

```powershell
# Single 3D position
python scripts\waapi.py ak.soundengine.setPosition '{
  "gameObject": 1,
  "position": {
    "position":   {"x": 10.0, "y": 0.0, "z": 5.0},
    "orientationFront": {"x": 1.0, "y": 0.0, "z": 0.0},
    "orientationTop":   {"x": 0.0, "y": 1.0, "z": 0.0}
  }
}'

# Multi-position (e.g. line emitter)
python scripts\waapi.py ak.soundengine.setMultiplePositions '{
  "gameObject": 1,
  "multiPositionType": 2,
  "positions": [
    {"position": {"x":0,"y":0,"z":0}, "orientationFront": {"x":1,"y":0,"z":0}, "orientationTop": {"x":0,"y":1,"z":0}},
    {"position": {"x":5,"y":0,"z":0}, "orientationFront": {"x":1,"y":0,"z":0}, "orientationTop": {"x":0,"y":1,"z":0}}
  ]
}'
```

`multiPositionType`: `0=SingleSource`, `1=MultiSources`, `2=MultiDirections`.

## Listeners

```powershell
python scripts\waapi.py ak.soundengine.setDefaultListeners '{"listeners":[1]}'
python scripts\waapi.py ak.soundengine.setListeners '{"emitter": 2, "listeners": [1]}'
python scripts\waapi.py ak.soundengine.setListenerSpatialization '{"listener": 1, "spatialized": true}'
```

## Aux send / output bus volume / obstruction

```powershell
python scripts\waapi.py ak.soundengine.setGameObjectAuxSendValues '{
  "gameObject": 1,
  "auxSendValues": [{"listener": 1, "auxBus": "\\Master-Mixer Hierarchy\\Default Work Unit\\Master Audio Bus\\Reverb", "controlValue": 0.5}]
}'

python scripts\waapi.py ak.soundengine.setGameObjectOutputBusVolume '{"emitter": 1, "listener": 1, "controlValue": 0.7}'

python scripts\waapi.py ak.soundengine.setObjectObstructionAndOcclusion '{"gameObject": 1, "listener": 1, "obstructionLevel": 0.4, "occlusionLevel": 0.2}'

python scripts\waapi.py ak.soundengine.setScalingFactor '{"gameObject": 1, "attenuationScalingFactor": 1.5}'
```

## Bank load (mostly for runtime simulation)

```powershell
python scripts\waapi.py ak.soundengine.loadBank '{"soundBank": "MyBank"}'
python scripts\waapi.py ak.soundengine.unloadBank '{"soundBank": "MyBank"}'
```

In Authoring mode, banks are usually loaded automatically; explicit load/unload is for testing what a runtime would see.

## Monitor message (debug print)

```powershell
python scripts\waapi.py ak.soundengine.postMsgMonitor '{"message": "Audition started"}'
```

Appears in the Capture Log of the Profiler — handy as a marker between operations.

## Mute / solo (Authoring-side, not runtime)

For Authoring-side audio routing changes (not the runtime engine), see [import-audio.md](import-audio.md) → Solo / Mute section.
