import importlib
from pathlib import Path
import pytest
import config


@pytest.fixture(autouse=True)
def _restore_config():
    yield
    importlib.reload(config)


def test_stockfish_path_from_env_var(monkeypatch, tmp_path):
    dummy_bin = tmp_path / "dummy_stockfish"
    dummy_bin.write_bytes(b"#!/bin/sh\necho dummy\n")

    monkeypatch.setenv("STOCKFISH_PATH", str(dummy_bin))
    importlib.reload(config)

    assert config.STOCKFISH_PATH == dummy_bin
    assert config.check_system_readiness()["stockfish"] is True


def test_stockfish_path_env_var_no_windows_fallback(monkeypatch, tmp_path):
    custom_missing = tmp_path / "custom_nonexistent_stockfish"
    monkeypatch.setenv("STOCKFISH_PATH", str(custom_missing))
    importlib.reload(config)

    assert config.STOCKFISH_PATH == custom_missing
    assert config.STOCKFISH_PATH.suffix != ".exe"


def test_stockfish_path_default_linux_when_no_binaries_exist(monkeypatch, tmp_path):
    monkeypatch.delenv("STOCKFISH_PATH", raising=False)
    importlib.reload(config)

    assert hasattr(config, "resolve_stockfish_path")
    # Point ROOT_DIR and BIN_DIR to empty tmp_path so no Windows fallback exists
    monkeypatch.setattr(config, "ROOT_DIR", tmp_path / "backend")
    monkeypatch.setattr(config, "BIN_DIR", tmp_path / "backend" / "bin")
    resolved = config.resolve_stockfish_path()
    assert resolved.name == "stockfish"
    assert resolved.suffix != ".exe"
