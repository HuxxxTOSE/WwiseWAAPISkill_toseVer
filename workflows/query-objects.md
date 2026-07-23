# Query Wwise Objects (WAQL)

The single read primitive is `ak.wwise.core.object.get`. It accepts a WAQL string and returns the requested fields for the matched objects. For grammar details, load [../references/waql-syntax.md](../references/waql-syntax.md). For the property/reference catalogue, [../references/object-accessors.md](../references/object-accessors.md).

## The basic call

```powershell
python scripts\waapi.py ak.wwise.core.object.get `
  '{"waql":"$ from type Sound take 5"}' `
  '{"return":["id","name","path","type"]}'
```

Two positional JSON blobs:

1. `args` — `{"waql": "..."}`
2. `options` — `{"return": [...accessors...], "platform": "...", "language": "..."}`. Both `platform` and `language` are optional.

## Resolve a name to a GUID (most common starter step)

```json
{ "waql": "$ from search \"footstep\" take 1" }
```

with options `{"return": ["id", "name", "path", "type"]}`. Take the `id` and reuse it for the next call — paths break when objects are renamed or moved.

## Filter on a property

```json
{ "waql": "$ from type Sound where volume < -6 take 50" }
{ "waql": "$ from type Sound where (notes = \"deprecated\" or notes = \"old\")" }
```

The right-hand side is a literal: numbers and booleans bare, strings double-quoted (and the JSON layer escapes them again).

## Walk the hierarchy

```json
{ "waql": "$ from object \"\\\\Actor-Mixer Hierarchy\\\\Default Work Unit\" select descendants where type = \"Sound\"" }
```

Note the quadruple backslashes inside JSON strings — `\\\\` becomes `\\` in the WAQL, which Wwise interprets as a literal `\`.

## Return shape

The response is `{"return": [<row>, ...]}`. Each row is a dict keyed by the accessors you requested. Nested accessors (`parent.name`, `audioSourceTrimValues.trimBegin`) come back flattened to the same keys you asked for.

## Pagination on large queries

```powershell
python scripts\waapi.py ak.wwise.core.object.get '{"waql":"$ from type Event skip 0 take 100"}' '{"return":["id","name"]}'
python scripts\waapi.py ak.wwise.core.object.get '{"waql":"$ from type Event skip 100 take 100"}' '{"return":["id","name"]}'
```

There is **no `limit` keyword**. WAQL uses `take` and `skip`.

## Discovering accessors for an unfamiliar type

```powershell
python scripts\waapi.py ak.wwise.core.object.getPropertyAndReferenceNames '{"object":"\\Effects\\Default Work Unit\\MyReverb"}'
python scripts\waapi.py ak.wwise.core.object.getPropertyInfo '{"property":"PreDelay","object":"\\Effects\\Default Work Unit\\MyReverb"}'
```

## Selected objects (Wwise UI)

To read what the user has currently selected in the Authoring UI:

```powershell
python scripts\waapi.py ak.wwise.ui.getSelectedObjects '{}' '{"return":["id","name","type","path"]}'
```

Useful when the user says "set the volume of the selected sounds to -6" — fetch IDs, then iterate.

## Common WAQL recipes

```text
# All sounds louder than 0 dB
$ from type Sound where volume > 0

# Sounds whose Attenuation has the largest radius among descendants
$ from type Sound select maxRadiusAttenuationObject

# Events that target a deleted/missing object (validity check)
$ from type Action where validity.isValid = false

# Music tracks longer than 30 s
$ from type MusicTrack where duration.max > 30

# Voice sounds in French
$ from type Sound where audioSourceLanguage.name = "French(France)"

# All objects under a Work Unit, paginated 200 at a time
$ from object "\Actor-Mixer Hierarchy\Default Work Unit" select descendants skip 0 take 200
```
