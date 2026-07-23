"""Thin wrapper around `waapi-client` for the wwise-waapi-skill.

Two ways to use this file:

1. CLI (called from Bash / PowerShell tool):

       python wwise_waapi.py <procedure-uri> [args-json] [options-json]

   Examples:
       python wwise_waapi.py ak.wwise.core.ping
       python wwise_waapi.py ak.wwise.core.object.get '{"waql":"$ from type Sound take 5"}' '{"return":["id","name"]}'

   stdout: pretty-printed JSON of the WAAPI result.
   stderr: human-readable error message; non-zero exit on failure.

2. Library import (from another Python script):

       from scripts.wwise_waapi import call
       result = call("ak.wwise.core.object.get",
                     args={"waql": "$ from type Sound"},
                     options={"return": ["id", "name"]})

The connection is opened lazily and closed at process exit.
"""

from __future__ import annotations

import atexit
import json
import sys
from typing import Any, Optional

try:
    from waapi import WaapiClient
except ImportError:
    sys.stderr.write(
        "error: `waapi-client` is not installed.\n"
        "Install it with: pip install waapi-client\n"
    )
    sys.exit(2)


_client: Optional[WaapiClient] = None


def _get_client() -> WaapiClient:
    global _client
    if _client is None or not _client.is_connected():
        _client = WaapiClient()
    return _client


def _close_client() -> None:
    global _client
    if _client is not None:
        try:
            _client.disconnect()
        except Exception:
            pass
        _client = None


atexit.register(_close_client)


def call(
    procedure: str,
    args: Optional[dict] = None,
    options: Optional[dict] = None,
) -> Any:
    """Call a WAAPI procedure and return the parsed JSON result.

    `args` is the procedure-specific argument object. `options` becomes the
    `options` field on the call (used for `return`, `platform`, `language`).
    Both may be None. Keys whose value is None are stripped automatically.
    """
    if args:
        args = {k: v for k, v in args.items() if v is not None}
    if options:
        options = {k: v for k, v in options.items() if v is not None}

    try:
        client = _get_client()
        payload = dict(args) if args else {}
        if options:
            payload["options"] = options
        if payload:
            return client.call(procedure, payload)
        return client.call(procedure)
    except Exception as exc:
        raise ConnectionError(
            "Cannot reach Wwise WAAPI. Ensure Wwise is running with "
            "Project > User Preferences > Enable Wwise Authoring API turned on. "
            f"Underlying error: {exc}"
        ) from exc


def _parse_json_arg(label: str, raw: Optional[str]) -> Optional[dict]:
    if raw is None or raw == "":
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        sys.stderr.write(f"error: {label} is not valid JSON: {exc}\n")
        sys.exit(2)


def _main(argv: list[str]) -> int:
    if len(argv) < 2 or argv[1] in ("-h", "--help"):
        sys.stderr.write(__doc__ or "")
        return 0 if len(argv) >= 2 else 2

    procedure = argv[1]
    args = _parse_json_arg("args", argv[2] if len(argv) > 2 else None)
    options = _parse_json_arg("options", argv[3] if len(argv) > 3 else None)

    try:
        result = call(procedure, args=args, options=options)
    except ConnectionError as exc:
        sys.stderr.write(f"error: {exc}\n")
        return 1
    except Exception as exc:
        sys.stderr.write(f"error: WAAPI call failed: {exc}\n")
        return 1

    json.dump(result, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(_main(sys.argv))
