#!/usr/bin/env python3
"""Skip-if-busy lock for overlapping Grok loop fires.

If a 5-minute loop fires while another agent is already editing this tree,
acquire() prints BUSY and exits 2. Stale locks (no heartbeat for STALE_SEC)
are stolen so a crashed holder cannot freeze the queue.

Usage:
  python .ai/agent_lock.py acquire --holder loop
  python .ai/agent_lock.py heartbeat
  python .ai/agent_lock.py release
  python .ai/agent_lock.py status
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCK_PATH = Path(os.environ.get("RESEARCHBENCH_LOCK_PATH") or (ROOT / ".ai" / "agent.lock"))
STALE_SEC = int(os.environ.get("RESEARCHBENCH_LOCK_STALE_SEC") or 12 * 60)


def _now() -> float:
    return time.time()


def _iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read() -> dict | None:
    try:
        data = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict):
        return None
    return data


def _write(payload: dict) -> None:
    LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = LOCK_PATH.with_suffix(".lock.tmp")
    tmp.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    tmp.replace(LOCK_PATH)


def _stale(data: dict) -> bool:
    hb = data.get("heartbeat_unix")
    if not isinstance(hb, (int, float)):
        return True
    return (_now() - float(hb)) > STALE_SEC


def cmd_status() -> int:
    data = _read()
    if data is None:
        print("FREE")
        return 0
    age = _now() - float(data.get("heartbeat_unix") or 0)
    state = "STALE" if _stale(data) else "BUSY"
    holder = data.get("holder", "unknown")
    print(f"{state} holder={holder} age_s={age:.0f}")
    return 0


def cmd_acquire(holder: str) -> int:
    data = _read()
    if data is not None and not _stale(data):
        print(f"BUSY holder={data.get('holder', 'unknown')} since={data.get('acquired_at', '')}")
        return 2
    payload = {
        "holder": holder,
        "pid": os.getpid(),
        "acquired_at": _iso(),
        "heartbeat_at": _iso(),
        "heartbeat_unix": _now(),
        "stale_after_sec": STALE_SEC,
    }
    _write(payload)
    print(f"ACQUIRED holder={holder}")
    return 0


def cmd_heartbeat() -> int:
    data = _read()
    if data is None:
        print("FREE")
        return 1
    data["heartbeat_at"] = _iso()
    data["heartbeat_unix"] = _now()
    _write(data)
    print("HEARTBEAT")
    return 0


def cmd_release() -> int:
    if LOCK_PATH.exists():
        try:
            LOCK_PATH.unlink()
        except OSError as exc:
            print(f"ERROR {exc}")
            return 1
    print("RELEASED")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["acquire", "heartbeat", "release", "status"])
    parser.add_argument("--holder", default="agent")
    args = parser.parse_args()
    if args.command == "acquire":
        return cmd_acquire(args.holder)
    if args.command == "heartbeat":
        return cmd_heartbeat()
    if args.command == "release":
        return cmd_release()
    return cmd_status()


if __name__ == "__main__":
    sys.exit(main())
