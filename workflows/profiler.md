# Profiler — Capture & Inspect

The Profiler exposes everything visible in the Wwise Profiler view: voices, busses, audio objects, RTPCs, game objects, CPU, memory, streamed/loaded media, meters. All retrieval procedures take a `time` argument that is either an integer (ms) or one of the strings `"user"` / `"capture"` (the two global cursors).

## Start / stop / save

```powershell
python scripts\waapi.py ak.wwise.core.profiler.startCapture
# … work happens, events get posted, etc. …
python scripts\waapi.py ak.wwise.core.profiler.stopCapture
python scripts\waapi.py ak.wwise.core.profiler.saveCapture '{"file": "C:\\captures\\session1.prof"}'
```

`startCapture` and `stopCapture` both return the time cursor in ms.

## Decide what to capture

```powershell
python scripts\waapi.py ak.wwise.core.profiler.enableProfilerData '{
  "dataTypes": [
    {"dataType": "cpu",          "enable": true},
    {"dataType": "voices",       "enable": true},
    {"dataType": "audioObjects", "enable": true},
    {"dataType": "meter",        "enable": false}
  ]
}'
```

Available `dataType` values: `cpu`, `memory`, `stream`, `voices`, `listener`, `obstructionOcclusion`, `markersNotification`, `soundbanks`, `loadedMedia`, `preparedObjects`, `preparedGameSyncs`, `interactiveMusic`, `streamingDevice`, `meter`, `auxiliarySends`, `apiCalls`, `spatialAudio`, `spatialAudioRaycasting`, `voiceInspector`, `audioObjects`, `gameSyncs`.

This call **overrides the user's Profiler settings** for the session — disable everything you don't need, especially `meter` and `voiceInspector`, to keep capture cost low.

## Read the cursor

```powershell
python scripts\waapi.py ak.wwise.core.profiler.getCursorTime '{"cursor": "capture"}'
python scripts\waapi.py ak.wwise.core.profiler.getCursorTime '{"cursor": "user"}'
```

`capture` = latest captured frame. `user` = wherever the user dragged the cursor in the timeline.

## Sampling at a given time

All `get*` queries below accept `time` as an int (ms) or `"user"` / `"capture"`.

```powershell
# Performance counters
python scripts\waapi.py ak.wwise.core.profiler.getPerformanceMonitor '{"time":"capture"}'

# Per-element CPU
python scripts\waapi.py ak.wwise.core.profiler.getCpuUsage '{"time":"capture"}'

# Voices (defaults: pipelineID, gameObjectID, objectGUID)
python scripts\waapi.py ak.wwise.core.profiler.getVoices '{"time":"capture"}' '{"return":["pipelineID","objectName","gameObjectName","baseVolume","priority","isVirtual"]}'

# Voice contributions for one voice
python scripts\waapi.py ak.wwise.core.profiler.getVoiceContributions '{"voicePipelineID": 12345, "time":"capture"}'

# Busses
python scripts\waapi.py ak.wwise.core.profiler.getBusses '{"time":"capture"}' '{"return":["pipelineID","objectName","volume","voiceCount","effectCount"]}'

# Audio Objects (Wwise Audio Objects pipeline)
python scripts\waapi.py ak.wwise.core.profiler.getAudioObjects '{"time":"capture"}' '{"return":["audioObjectID","busName","x","y","z","spread","focus"]}'

# Game Objects
python scripts\waapi.py ak.wwise.core.profiler.getGameObjects '{"time":"capture"}'

# RTPCs
python scripts\waapi.py ak.wwise.core.profiler.getRTPCs '{"time":"capture"}'

# Loaded / streamed media
python scripts\waapi.py ak.wwise.core.profiler.getLoadedMedia '{"time":"capture"}'
python scripts\waapi.py ak.wwise.core.profiler.getStreamedMedia '{"time":"capture"}'
```

## Meters

Only the master audio bus has metering enabled by default — register additional busses first:

```powershell
python scripts\waapi.py ak.wwise.core.profiler.registerMeter '{"object": "\\Master-Mixer Hierarchy\\Default Work Unit\\Master Audio Bus\\SFX"}'

python scripts\waapi.py ak.wwise.core.profiler.getMeters '{"time":"capture"}'

python scripts\waapi.py ak.wwise.core.profiler.unregisterMeter '{"object": "\\Master-Mixer Hierarchy\\Default Work Unit\\Master Audio Bus\\SFX"}'
```

Pair every `registerMeter` with an eventual `unregisterMeter`.

## Typical capture workflow

```python
from waapi import call

# 1. Pick what to record
call("ak.wwise.core.profiler.enableProfilerData", args={
    "dataTypes": [
        {"dataType": "cpu", "enable": True},
        {"dataType": "voices", "enable": True},
    ],
})

# 2. Start
t0 = call("ak.wwise.core.profiler.startCapture")["return"]

# 3. Drive audio (post events, set RTPCs, etc.)
call("ak.soundengine.postEvent", args={"event": "Play_Stress_Test", "gameObject": 1})

# 4. Sample over time
import time
for _ in range(10):
    time.sleep(0.5)
    voices = call(
        "ak.wwise.core.profiler.getVoices",
        args={"time": "capture"},
        options={"return": ["pipelineID", "objectName", "baseVolume"]},
    )
    print(len(voices.get("return", [])), "voices live")

# 5. Stop and save
t1 = call("ak.wwise.core.profiler.stopCapture")["return"]
call("ak.wwise.core.profiler.saveCapture", args={"file": "C:\\captures\\stress.prof"})
print(f"captured {t1 - t0} ms")
```

The `.prof` file can be reopened in Wwise's Profiler view for offline analysis.
