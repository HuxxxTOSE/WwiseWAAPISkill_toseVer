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

The connection is opened lazily and closed (bounded, non-blocking) at process
exit. Library users may call ``disconnect()`` for a deterministic early close.
"""

from __future__ import annotations

import atexit
import json
import os
import sys
import threading
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
_daemonized = False


def _daemonize_waapi_threads() -> None:
    """Make ``waapi-client``'s internal threads daemon so a script that merely
    ``import``s this module can exit promptly.

    ``waapi-client`` runs its WAMP asyncio loop and callback executor on
    non-daemon threads, and ``WaapiClient.disconnect()`` joins them without a
    timeout (and never stops the executor). A plain library script therefore
    hangs forever at interpreter exit waiting on those threads. Daemonising them
    lets the interpreter exit normally (with the real exit code) once the script
    finishes, without resorting to ``os._exit`` in library code.

    Best-effort and version-tolerant: patches by name at call time and swallows
    any error, so a future ``waapi-client`` refactor simply falls back to the
    original behaviour instead of breaking imports.
    """
    global _daemonized
    if _daemonized:
        return
    _daemonized = True

    # 1) The WAMP runner thread that owns the asyncio event loop.
    #    Patch its ``start`` to flag the thread daemon *before* it launches. We
    #    deliberately do NOT rebind ``ak_autobahn._WampClientThread`` because its
    #    own ``__init__`` calls ``super(_WampClientThread, self)`` via that very
    #    module global — rebinding the name would corrupt the MRO lookup.
    try:
        from waapi.wamp import ak_autobahn

        _wamp_cls = ak_autobahn._WampClientThread
        if not getattr(_wamp_cls, "_ak_daemon_patched", False):
            _orig_start = _wamp_cls.start

            def _daemon_start(self, _orig_start=_orig_start):
                try:
                    self.daemon = True
                except Exception:
                    pass
                return _orig_start(self)

            _wamp_cls.start = _daemon_start
            _wamp_cls._ak_daemon_patched = True
    except Exception:
        pass

    # 2) The callback-executor threads (started even for call-only sessions).
    #    Here a subclass is safe: ``threading.Thread`` never resolves the
    #    executor module's ``Thread`` name, so rebinding it breaks nothing.
    try:
        from waapi.client import executor as _executor

        _BaseThread = _executor.Thread
        if not getattr(_BaseThread, "_ak_daemonized", False):
            class _DaemonExecutorThread(_BaseThread):
                _ak_daemonized = True

                def start(self):
                    try:
                        self.daemon = True
                    except Exception:
                        pass
                    return super().start()

            _executor.Thread = _DaemonExecutorThread
    except Exception:
        pass


def _get_client() -> WaapiClient:
    global _client
    if _client is None or not _client.is_connected():
        _daemonize_waapi_threads()
        _client = WaapiClient()
    return _client


def _close_client() -> None:
    """Disconnect the shared client, nulling it so the next call reconnects."""
    global _client
    client, _client = _client, None
    if client is not None:
        try:
            client.disconnect()
        except Exception:
            pass


def _close_client_bounded(timeout: float = 2.0) -> None:
    """Best-effort disconnect that never blocks shutdown for long.

    `WaapiClient.disconnect()` can block (~45s on Windows, or indefinitely while
    Wwise is connected) because the WAMP connection runs on a background thread.
    Run the disconnect on a daemon thread and wait only briefly; if it has not
    finished, let the process exit anyway (the OS reclaims the socket). This
    protects BOTH the CLI path and library importers that rely on the atexit
    handler below.
    """
    worker = threading.Thread(target=_close_client, daemon=True)
    worker.start()
    worker.join(timeout=timeout)


def disconnect() -> None:
    """Public helper: close the shared client promptly (bounded wait).

    Optional for library users — the atexit handler calls this automatically —
    but handy when you want a deterministic, fast close mid-script.
    """
    _close_client_bounded()


atexit.register(_close_client_bounded)


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


def _shutdown(code: int) -> "None":
    """Flush output and terminate promptly, avoiding a hung exit.

    `waapi-client` runs the WAMP connection on a background thread whose
    `disconnect()` can block interpreter exit. We do a bounded best-effort
    disconnect, then force-exit so the CLI returns immediately regardless of the
    background thread's state.
    """
    sys.stdout.flush()
    sys.stderr.flush()
    _close_client_bounded()
    os._exit(code)


if __name__ == "__main__":
    _shutdown(_main(sys.argv))
