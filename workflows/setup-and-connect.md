# Setup & Connection Troubleshooting

Read this only if `ak.wwise.core.ping` fails or the user asks about installation.

## Install

The skill needs Python 3.9+ and the `waapi-client` PyPI package. Install once per environment:

```powershell
pip install waapi-client
```

`waapi-client` pulls in `autobahn` and `txaio`. No other dependencies are required.

## Wwise side

1. Launch Wwise Authoring 2024.1 or later.
2. **Project → User Preferences → Enable Wwise Authoring API** must be checked.
3. Confirm the WAAPI port (default 8095). Custom port? Override in `WaapiClient(url="ws://127.0.0.1:<port>/waapi")` — see "Non-default port" below.

Open the project that you intend to operate on. WAAPI will accept calls without a project loaded, but most procedures need one.

## Connection check

```powershell
python scripts\waapi.py ak.wwise.core.ping
```

Expected:

```json
{"isAvailable": true}
```

Any other outcome:

| Symptom | Cause | Fix |
| --- | --- | --- |
| `error: Cannot reach Wwise WAAPI` / `ConnectionRefusedError` | Wwise not running, or WAAPI not enabled. | Launch Wwise; toggle Enable Wwise Authoring API. |
| Hangs, then times out | A modal dialog (e.g. migration prompt, save dialog) is blocking the Authoring app. | Click through the dialog manually; WAAPI does not respond while one is open. |
| `isAvailable: false` | Same modal-dialog reason — WAAPI is reachable but suspended. | Dismiss the dialog. |
| `error: \`waapi-client\` is not installed` | Missing PyPI package. | `pip install waapi-client`. |
| Calls succeed sometimes, then fail with `Connection closed` | Wwise was restarted or the user changed projects. | The wrapper auto-reconnects on the next call; rerun. |

## Non-default port

If the user configured a non-default WAAPI port, edit `scripts/waapi.py`:

```python
def _get_client() -> WaapiClient:
    global _client
    if _client is None or not _client.is_connected():
        _client = WaapiClient(url="ws://127.0.0.1:9999/waapi")  # custom port
    return _client
```

## Multi-call sessions

The wrapper holds a single persistent `WaapiClient` for the lifetime of the Python process and disconnects at exit. Calling `waapi.py` repeatedly from PowerShell creates a new process per call (one connection each). For tighter loops, write a one-off Python script that imports `call` directly and reuses the connection across hundreds of operations.

```python
# tighten_loop.py
from waapi import call
ids = [r["id"] for r in call(
    "ak.wwise.core.object.get",
    args={"waql": "$ from type Sound take 100"},
    options={"return": ["id"]}
)["return"]]

for i in ids:
    call("ak.wwise.core.object.setProperty",
         args={"object": i, "property": "Volume", "value": -3})
```

## Discovering what's available right now

```powershell
python scripts\waapi.py ak.wwise.waapi.getFunctions
python scripts\waapi.py ak.wwise.waapi.getTopics
python scripts\waapi.py ak.wwise.waapi.getSchema '{"uri":"ak.wwise.core.object.get","includeExamples":true}'
```

Always trust the live schema over any static doc — Wwise versions add and rename fields.
