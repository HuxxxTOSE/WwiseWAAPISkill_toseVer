# `set_objects` Cookbook

Canonical payload shapes for `ak.wwise.core.object.set`. Every example below is what goes into the `objects` field of the call args:

```json
{ "objects": [ <example> ], "options": { "return": ["id","name","path","type"] } }
```

Each entry must include `object` (path or GUID). Optional siblings: `name` (rename), `notes`, `import` (audio assignment), `children` (nested creation list), `platform`, `onNameConflict`, `listMode` (`append` / `replaceAll`).

## 1. Create / set an RTPC list with a curve

```json
{
  "object": "\\Actor-Mixer Hierarchy\\Ambience\\Amb\\Amb_Global\\Amb_None",
  "@RTPC": [
    {
      "name": "rtpc_test",
      "type": "RTPC",
      "@ControlInput": "\\Game Parameters\\Ambience\\Amb_Special_Mus",
      "@PropertyName": "Volume",
      "@Curve": {
        "type": "Curve",
        "points": [
          { "x": 0,   "y": -200, "shape": "Linear" },
          { "x": 100, "y": 10,   "shape": "Linear" }
        ]
      }
    }
  ]
}
```

## 2. Bind an Attenuation by creating it inline (with override switches)

```json
{
  "object": "\\Actor-Mixer Hierarchy\\Ambience\\Amb\\Amb_Global\\Amb_None",
  "name": "New_ambience_Name",
  "@OverridePositioning": true,
  "@EnableAttenuation": true,
  "@Attenuation": {
    "type": "Attenuation",
    "name": "Att_Amb_Cls_Fountain002",
    "@RTPC": [
      {
        "type": "RTPC",
        "name": "rtpc_test",
        "@ControlInput": "\\Game Parameters\\Ambience\\Amb_Special_Mus",
        "@PropertyName": "ConeLowPassFilterValue",
        "@Curve": {
          "type": "Curve",
          "points": [
            { "x": 0,   "y": -200, "shape": "Linear" },
            { "x": 100, "y": 10,   "shape": "Linear" }
          ]
        }
      }
    ]
  }
}
```

The override switch (`@OverridePositioning` / `@EnableAttenuation`) **must** be in the same payload as the values it gates, or the panel will keep the values hidden and inactive.

## 3. Replace just the curve points on an existing Curve object

```json
{
  "object": "{99D5745C-3A70-496F-AE19-2F463DEC7CAF}",
  "@Curve": {
    "type": "Curve",
    "points": [
      { "x": 0,   "y": -200, "shape": "Linear" },
      { "x": 100, "y": 10,   "shape": "Linear" }
    ]
  }
}
```

## 4. Build a Music Switch Container with imported WAV — multiple roots in one call

```json
[
  {
    "object": "\\Switches\\Default Work Unit",
    "children": [
      { "type": "SwitchGroup", "name": "MySwitchGroup",
        "children": [ { "type": "Switch", "name": "Switch1" } ] }
    ]
  },
  {
    "object": "\\Interactive Music Hierarchy\\Default Work Unit",
    "children": [
      {
        "type": "MusicSwitchContainer",
        "name": "MyMusicSwitchContainer",
        "@Arguments": [ "\\Switches\\Default Work Unit\\MySwitchGroup" ],
        "@Entries": [
          {
            "type": "MultiSwitchEntry",
            "name": "",
            "@EntryPath": [ "\\Switches\\Default Work Unit\\MySwitchGroup\\Switch1" ],
            "@AudioNode": "\\Interactive Music Hierarchy\\Default Work Unit\\MyMusicSwitchContainer\\MyMusicPlaylistContainer"
          }
        ],
        "children": [
          {
            "type": "MusicPlaylistContainer",
            "name": "MyMusicPlaylistContainer",
            "@PlaylistRoot": {
              "type": "MusicPlaylistItem", "name": "", "@LoopCount": 0,
              "children": [
                { "type": "MusicPlaylistItem", "name": "",
                  "@Segment": "\\Interactive Music Hierarchy\\Default Work Unit\\MyMusicSwitchContainer\\MyMusicPlaylistContainer\\MySegment",
                  "@PlaylistItemType": 1 }
              ]
            },
            "children": [
              {
                "type": "MusicSegment", "name": "MySegment",
                "children": [
                  {
                    "type": "MusicTrack", "name": "MyMusicTrack",
                    "import": {
                      "files": [ { "audioFile": "C:\\Path\\To\\SFX_400.wav" } ]
                    }
                  }
                ]
              }
            ]
          }
        ]
      }
    ]
  }
]
```

The `import` block inside a leaf entry is how you attach a WAV without a separate `ak.wwise.core.audio.import` call.

## 5. Batch creation with conflict policies and an Event/Action

```json
[
  { "object": "{7A12D08F-B0D9-4403-9EFA-2E6338C197C1}",
    "children": [ { "type": "Sound", "name": "Boom" } ] },

  { "object": "\\Actor-Mixer Hierarchy\\Default Work Unit",
    "children": [ { "type": "Folder", "name": "Guns" } ],
    "onNameConflict": "rename" },

  { "object": "\\Events\\Default Work Unit",
    "onNameConflict": "merge",
    "children": [
      { "type": "Folder", "name": "WAAPI",
        "children": [
          { "type": "Event", "name": "Play_SFX",
            "children": [
              { "name": "", "type": "Action",
                "@ActionType": 1,
                "@Target": "\\Actor-Mixer Hierarchy\\Default Work Unit\\SFX" }
            ] }
        ] }
    ] },

  { "object": "{7A12D08F-B0D9-4403-9EFA-2E6338C197C1}",
    "children": [
      { "type": "RandomSequenceContainer", "name": "Boom",
        "@RandomOrSequence": 1,
        "children": [
          { "type": "Sound", "name": "A" },
          { "type": "Sound", "name": "B" }
        ] }
    ] },

  { "object": "\\Interactive Music Hierarchy\\Default Work Unit\\My Segment",
    "@Cues": [
      { "name": "My Music Cue", "type": "MusicCue",
        "@TimeMs": 1200, "@CueType": 2 }
    ] }
]
```

`onNameConflict` values: `fail` (default), `rename`, `replace`, `merge`. `merge` is what you want when re-running an idempotent setup script.

## 6. Insert an effect plug-in into an EffectSlot

```json
{
  "object": "\\Actor-Mixer Hierarchy\\Default Work Unit\\MySound",
  "@Effects": [
    {
      "type": "EffectSlot",
      "name": "",
      "@Effect": {
        "type": "Effect",
        "name": "myCustomEffect",
        "classId": 7733251,
        "@PreDelay": 24,
        "@RoomShape": 99
      }
    }
  ]
}
```

`classId` identifies the plug-in. Discover the value with `ak.wwise.core.object.getTypes` or by reading `classId` off an existing instance.

## 7. Create a Sound with a SourcePlugin (Wwise SynthOne)

```json
{
  "object": "\\Actor-Mixer Hierarchy\\Default Work Unit",
  "children": [
    {
      "type": "Sound",
      "name": "MySynthOne",
      "children": [
        {
          "type": "SourcePlugin",
          "name": "SynthOne",
          "classId": 9699330,
          "@BaseFrequency": 100,
          "@Osc1Waveform": 0,
          "@Osc2Waveform": 1
        }
      ]
    }
  ]
}
```

## Key ergonomics

- **One call > many calls.** `set_objects` accepts a list — batch related edits to keep undo grouping coherent and avoid partial states.
- **`listMode`**: default `append`. Pass `"listMode": "replaceAll"` on the parent entry to wipe a list before assignment.
- **`return` option** is shared across the whole call — pick the smallest set of fields you actually need.
- **Logs come back in the response** (`logs` array) when individual sub-operations warn or fail. Always inspect them; absence of an exception is *not* sufficient.
