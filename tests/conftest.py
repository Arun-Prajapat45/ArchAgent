from __future__ import annotations

import socket
from collections.abc import Iterator

import pytest


@pytest.fixture(autouse=True)
def no_network(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Fail fast if an unmocked test attempts a paid/external request."""
    original = socket.socket.connect

    def guarded_connect(self: socket.socket, address: object) -> object:
        host = address[0] if isinstance(address, tuple) else str(address)
        if host not in {"127.0.0.1", "localhost", "testserver"}:
            raise RuntimeError(f"External network disabled in tests: {host}")
        return original(self, address)  # pragma: no cover

    monkeypatch.setattr(socket.socket, "connect", guarded_connect)
    yield
