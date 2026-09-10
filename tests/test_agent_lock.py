"""Skip-if-busy lock used by the 5-minute continuation loop."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

_LOCK_SRC = Path(__file__).resolve().parents[1] / ".ai" / "agent_lock.py"


@pytest.fixture
def load_lock(monkeypatch):
    def _load(tmp_path: Path, stale_sec: int = 12 * 60):
        monkeypatch.setenv("RESEARCHBENCH_LOCK_PATH", str(tmp_path / "agent.lock"))
        monkeypatch.setenv("RESEARCHBENCH_LOCK_STALE_SEC", str(stale_sec))
        spec = importlib.util.spec_from_file_location("agent_lock", _LOCK_SRC)
        assert spec is not None and spec.loader is not None
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    return _load


def test_acquire_then_busy(tmp_path: Path, load_lock):
    lock = load_lock(tmp_path)
    assert lock.cmd_acquire("loop-a") == 0
    assert lock.cmd_acquire("loop-b") == 2


def test_release_frees_lock(tmp_path: Path, load_lock):
    lock = load_lock(tmp_path)
    assert lock.cmd_acquire("loop-a") == 0
    assert lock.cmd_release() == 0
    assert lock.cmd_acquire("loop-b") == 0


def test_stale_lock_is_stolen(tmp_path: Path, load_lock):
    lock = load_lock(tmp_path, stale_sec=1)
    assert lock.cmd_acquire("old") == 0
    payload = lock._read()
    assert payload is not None
    payload["heartbeat_unix"] = payload["heartbeat_unix"] - 120
    lock._write(payload)
    assert lock.cmd_acquire("new") == 0
    data = lock._read()
    assert data is not None
    assert data["holder"] == "new"


def test_status_free_when_missing(tmp_path: Path, load_lock):
    lock = load_lock(tmp_path)
    assert lock.cmd_status() == 0
