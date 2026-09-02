# SoundBank Inclusions & Generation

Three procedures cover the SoundBank lifecycle: inspect, edit, generate.

## Inspect inclusion list

```powershell
python scripts\wwise_waapi.py ak.wwise.core.soundbank.getInclusions '{"soundbank":"\\SoundBanks\\Default Work Unit\\MyBank"}'
```

Returns:

```json
{
  "inclusions": [
    {"object": "{GUID}", "filter": ["events", "structures", "media"]}
  ]
}
```

`filter` items: `events`, `structures`, `media`. Pick a subset to include only events (no structures/media), useful when sharing media across banks.

## Modify inclusion list

```powershell
python scripts\wwise_waapi.py ak.wwise.core.soundbank.setInclusions '{
  "soundbank": "\\SoundBanks\\Default Work Unit\\MyBank",
  "operation": "add",
  "inclusions": [
    {"object": "\\Events\\Default Work Unit\\Play_Click", "filter": ["events","structures","media"]},
    {"object": "\\Events\\Default Work Unit\\Play_Hover", "filter": ["events","structures","media"]}
  ]
}'
```

`operation`:

- `add` — union with existing.
- `remove` — set difference.
- `replace` — wipe and rewrite. **Confirm with the user before using `replace` on a bank with manually curated content.**

## Generate banks

```powershell
# Generate everything for all platforms/languages, write to disk
python scripts\wwise_waapi.py ak.wwise.core.soundbank.generate '{
  "rebuildSoundBanks": true,
  "writeToDisk": true
}'

# Generate a specific bank for one platform
python scripts\wwise_waapi.py ak.wwise.core.soundbank.generate '{
  "soundbanks": [{"name": "MyBank"}],
  "platforms": ["Windows"],
  "writeToDisk": true
}'

# Force a clean rebuild (deletes audio cache - SLOW; confirm first)
python scripts\wwise_waapi.py ak.wwise.core.soundbank.generate '{
  "rebuildSoundBanks": true,
  "clearAudioFileCache": true,
  "writeToDisk": true
}'
```

Argument summary:

| Field | Effect |
| --- | --- |
| `soundbanks` | List of `{name, events?, auxBusses?, inclusions?, rebuild?}`. Empty/omitted ⇒ all user-defined banks. Auto-defined banks always regenerate. |
| `platforms` | Defaults to all configured platforms. |
| `languages` | Defaults to all. |
| `skipLanguages` | True ⇒ skip localized banks entirely. |
| `rebuildSoundBanks` | Force full rebuild. |
| `clearAudioFileCache` | **Wipes the entire converted-media cache for all platforms** before generating. Slow, irreversible. |
| `writeToDisk` | False (default) returns bank data inline (base64) on the `ak.wwise.core.soundbank.generated` topic. True writes `.bnk` files. |
| `rebuildInitBank` | Force-rebuild the Init bank only. |

Response includes a `logs` array — inspect for `Warning` / `Error` / `Fatal Error` entries even when the call returns 200. Banks generate "successfully" with errors that will fail at runtime.

## Channel-only generation log

For just the SoundBank generation log without re-running:

```powershell
python scripts\wwise_waapi.py ak.wwise.core.log.get '{"channel":"soundbankGenerate"}'
```

## Typical pipeline pattern

1. Edit content (`set_objects`, `import_audio`).
2. `save_project`.
3. `generate` with `writeToDisk: true`.
4. Inspect `logs` for issues.
5. Read the `soundbankGenerate` log channel for trailing warnings.

If running unattended (CI / pre-commit hook), prefer `WwiseConsole.exe` with the project path — it has lower overhead than a full Authoring session for headless generation. WAAPI is the right choice when generation has to coexist with other interactive edits in the same Wwise instance.
