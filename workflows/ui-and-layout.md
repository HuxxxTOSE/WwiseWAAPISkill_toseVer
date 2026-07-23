# UI Commands, Layouts, and Screen Capture

Procedures under `ak.wwise.ui.*` drive the Authoring UI itself: built-in commands, layout switching, view docking, and pixel-level screen capture.

## Execute a UI command

Wwise exposes its menu/keyboard commands under stable IDs. List them:

```powershell
python scripts\waapi.py ak.wwise.ui.commands.getCommands
```

Then execute:

```powershell
# No-arg command (e.g. SaveAll)
python scripts\waapi.py ak.wwise.ui.commands.execute '{"command": "SaveAll"}'

# Command operating on selected/passed objects
python scripts\waapi.py ak.wwise.ui.commands.execute '{
  "command": "ConvertSelected",
  "objects": ["\\Actor-Mixer Hierarchy\\Default Work Unit\\UI\\Click"],
  "platforms": ["Windows"]
}'

# Command needing a value
python scripts\waapi.py ak.wwise.ui.commands.execute '{
  "command": "FindInProjectExplorerNew",
  "value": "Footstep"
}'
```

## Register custom commands (script integration)

Custom commands launch external programs or Lua scripts and can appear in main menus / context menus. Persist for the Wwise process lifetime; lost on restart.

```powershell
python scripts\waapi.py ak.wwise.ui.commands.register '{
  "commands": [
    {
      "id": "company.tools.normalize_loudness",
      "displayName": "Normalize Loudness",
      "program": "C:\\tools\\normalize.exe",
      "args": "--target -23 ${id}",
      "startMode": "MultipleSelectionMultipleProcesses",
      "redirectOutputs": true,
      "contextMenu": {
        "basePath": "Custom Tools",
        "visibleFor": "Sound,RandomSequenceContainer",
        "enabledFor": "Sound,RandomSequenceContainer"
      }
    }
  ]
}'

python scripts\waapi.py ak.wwise.ui.commands.unregister '{"commands": ["company.tools.normalize_loudness"]}'
```

`startMode` options:

- `SingleSelectionSingleProcess` — runs once, single object only.
- `MultipleSelectionSingleProcessSpaceSeparated` — runs once with all selected items as space-separated args.
- `MultipleSelectionMultipleProcesses` — one process per selected item, parallel.

For Lua scripts, set `luaScript` instead of `program`. `${CurrentCommandDirectory}` resolves to the directory of the Wwise installation's command tools.

## Read selected objects

```powershell
python scripts\waapi.py ak.wwise.ui.getSelectedObjects '{}' '{"return":["id","name","type","path","@Volume"]}'
```

## Project open / close / create

```powershell
python scripts\waapi.py ak.wwise.ui.project.open '{
  "path": "C:\\Projects\\MyGame\\MyGame.wproj",
  "onMigrationRequired": "migrate",
  "bypassSave": true
}'

python scripts\waapi.py ak.wwise.ui.project.close '{"bypassSave": true}'

python scripts\waapi.py ak.wwise.ui.project.create '{
  "path": "C:\\Projects\\NewGame\\NewGame.wproj",
  "platforms": [{"name": "Windows", "basePlatform": "Windows"}],
  "languages": ["English(US)", "French(France)"]
}'
```

`bypassSave: true` skips the "save current project?" prompt — required when running unattended. **Confirm with the user before passing `bypassSave: true` on a project with unsaved edits.**

`onMigrationRequired`: `migrate` (proceed) or `fail` (refuse to open older projects).

## Layouts — switch / read / write

```powershell
python scripts\waapi.py ak.wwise.ui.layout.getLayoutNames
python scripts\waapi.py ak.wwise.ui.layout.getCurrentLayoutName

# Switch to a built-in layout (e.g. "Designer", "Mixer", "Profiler", "SoundBank")
python scripts\waapi.py ak.wwise.ui.layout.switchLayout '{"name":"Profiler"}'

# Serialize current/named layout to JSON
python scripts\waapi.py ak.wwise.ui.layout.getLayout '{"name":"Designer"}'
```

Custom layouts can be registered with `setLayout` and removed with `removeLayout`. The full `Layout` dict is large — capture an existing one with `getLayout`, edit, then push back via:

```powershell
python scripts\waapi.py ak.wwise.ui.layout.setLayout '{"name":"MyLayout","layout":{...full Layout dict...}}'
python scripts\waapi.py ak.wwise.ui.layout.removeLayout '{"name":"MyLayout"}'
```

## View docking, undocking, splitter

```powershell
# What view types exist?
python scripts\waapi.py ak.wwise.ui.layout.getViewTypes

# What's open right now in a layout?
python scripts\waapi.py ak.wwise.ui.layout.getViewInstances '{"name":"Designer"}'

# Ensure a view is open and visible
python scripts\waapi.py ak.wwise.ui.layout.getOrCreateView '{"name":"Property Editor"}'

# Dock a floating view next to another
python scripts\waapi.py ak.wwise.ui.layout.dockView '{
  "name":"Designer",
  "viewID":"{view-guid}",
  "targetID":"{target-guid}",
  "side":"Right"
}'
# `side`: Left, Right, Top, Bottom, Center

python scripts\waapi.py ak.wwise.ui.layout.undockView '{"name":"Designer","viewID":"{view-guid}","posX":100,"posY":100}'

# Move a splitter by relative pixels
python scripts\waapi.py ak.wwise.ui.layout.moveSplitter '{"id":"{splitter-guid}","delta":-50}'

# Get current rectangle (for a screen capture coordinate)
python scripts\waapi.py ak.wwise.ui.layout.getElementRectangle '{"id":"{element-guid}"}'
```

Element IDs come from `getViewInstances` and `getLayout` — they're stable for the layout's lifetime.

## Screen capture

```powershell
# Whole UI
python scripts\waapi.py ak.wwise.ui.captureScreen

# Specific view
python scripts\waapi.py ak.wwise.ui.captureScreen '{"viewName":"Property Editor"}'

# Specific rect (relative to the named view, or to the full window if viewName omitted)
python scripts\waapi.py ak.wwise.ui.captureScreen '{"viewName":"Property Editor","rect":{"x":0,"y":0,"width":400,"height":300}}'
```

Returns `{contentType: "image/png", contentBase64: "..."}`. Decode and save:

```python
import base64, pathlib
data = base64.b64decode(result["contentBase64"])
pathlib.Path("snap.png").write_bytes(data)
```

## WwiseConsole projects

If the user is operating a project opened via `WwiseConsole.exe` (headless mode), use `ak.wwise.console.project.close` instead of `ak.wwise.ui.project.close`. For all other operations, the regular `ak.wwise.*` URIs apply equally.
