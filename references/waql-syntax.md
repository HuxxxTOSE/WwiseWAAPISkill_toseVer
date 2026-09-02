# WAQL Syntax Reference

WAQL is the query language used by `ak.wwise.core.object.get`. Every query starts with `$ from <source>` and is composed by chaining transforms.

## Sources — pick the starting set

| Form | Returns |
| --- | --- |
| `$ from object "<path>"` | The single object at this project path. |
| `$ from object "{GUID}"` | The single object with this GUID. |
| `$ from type <Type>` | All objects of `<Type>` (e.g. `Sound`, `Event`, `Bus`, `RandomSequenceContainer`). |
| `$ from search "<text>"` | All objects whose name contains `<text>`. Multiple words are space-separated AND. |
| `$ from project` | Every object in the project. **Almost always too large — pair with `take`.** |

Examples:

```
$ from object "\Actor-Mixer Hierarchy\Default Work Unit\Shot_01"
$ from object "{1514A4D8-1DA6-412A-A17E-75CA0C2149F3}"
$ from search "gun"
$ from search "foot walk"
```

## Transforms — narrow / sort / project

| Form | Effect |
| --- | --- |
| `where <property> = <number\|bool>` | Filter by literal value. |
| `where <property> = "<string>"` | Filter by string value (always double-quoted). |
| `take <N>` | Keep the first N. **Use this on every query that isn't already bounded.** |
| `skip <N>` | Drop the first N. Pair with `take` for pagination. |
| `select <reference>` | Replace the working set with the targets of a reference (e.g. `select parent`, `select descendants`). |
| `orderby <property>` | Ascending sort. |
| `orderby <property> reverse` | Descending sort. |

Examples:

```
$ from search "gun" where volume = 0
$ from search "gun" where volume > 0
$ from search "gun" where notes = "This is a gun"
$ from object "\Actor-Mixer Hierarchy" select descendants, this where name = "Shot_01"
$ from type Sound select parent.Attenuation
$ from type Sound orderby name
$ from type Sound where parent.childrenCount > 1 select descendants where audioSourceTrimValues.trimBegin > 0 where audioSourceTrimValues.trimEnd < 3.1
```

## Operators

`=`, `!=`, `>`, `<`, `>=`, `<=`, `and`, `or`, `()` for grouping.

```
$ from type Sound where volume >= 0 and volume < 6
$ from type Sound where (volume = -3 or volume = 0) and (name = "Hello" and name != "Hi")
```

## Property / reference accessors used in queries

The accessor surface is the same one you pass in the `return` option. See [object-accessors.md](object-accessors.md) for the catalogue.

For type-specific properties not listed there, query Wwise live:

```powershell
python scripts\wwise_waapi.py ak.wwise.core.object.getPropertyAndReferenceNames '{"object":"<path-or-guid>"}'
```

## Pitfalls

- **There is no `limit` keyword.** Pagination is `take` / `skip`.
- **Avoid bare `$ from type Event` / `$ from project`** on real projects — they can return tens of thousands of rows.
- **GUIDs > paths** for stability. Resolve names to GUIDs once, then reuse them.
- The `return` option (passed in the call's `options`, not the WAQL) decides which fields come back. It is independent of the WAQL itself: `return: ["id", "name", "path", "type"]` is a sensible default.
