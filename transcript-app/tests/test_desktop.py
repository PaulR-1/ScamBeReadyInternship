"""Desktop shell lifecycle. Fakes stand in for WebView2."""

from __future__ import annotations

import socket

import pytest

from app.desktop import (
    DesktopRefused,
    Failed,
    FailureReason,
    Listening,
    LoopbackOrigin,
    UvicornSession,
    serve_in_window,
)


class FakeSession:
    def __init__(self, origin: LoopbackOrigin, report: Listening | Failed) -> None:
        self.origin = origin
        self._report = report
        self.stop_count = 0
        self._stopped = False

    def wait_until_ready(self, timeout: float = 30.0) -> Listening | Failed:
        return self._report

    def request_stop(self) -> None:
        if self._stopped:
            return
        self._stopped = True
        self.stop_count += 1

    def join(self) -> None:
        self.request_stop()


class RecordingWindow:
    def __init__(self) -> None:
        self.loaded_home = False
        self.failure: FailureReason | None = None

    def show(self, session: FakeSession) -> None:
        report = session.wait_until_ready()
        if isinstance(report, Listening):
            self.loaded_home = True
            return
        self.failure = report.reason


def test_busy_port_paints_the_error_and_does_not_open_home():
    origin = LoopbackOrigin.parse("127.0.0.1", 8756)
    session = FakeSession(origin, Failed(FailureReason.PORT_IN_USE))
    window = RecordingWindow()
    serve_in_window(session, window)
    assert window.loaded_home is False
    assert window.failure is FailureReason.PORT_IN_USE
    assert session.stop_count == 1


def test_close_stops_once_even_if_stop_runs_again():
    origin = LoopbackOrigin.parse("127.0.0.1", 8756)
    session = FakeSession(origin, Listening(origin))
    serve_in_window(session, RecordingWindow())
    assert session.stop_count == 1
    session.request_stop()
    assert session.stop_count == 1


def test_loopback_refuses_wildcard_and_bad_ports():
    with pytest.raises(DesktopRefused):
        LoopbackOrigin.parse("0.0.0.0", 8756)
    with pytest.raises(DesktopRefused):
        LoopbackOrigin.parse("127.0.0.1", 0)
    with pytest.raises(DesktopRefused):
        LoopbackOrigin.parse("127.0.0.1", 70000)


def test_taken_port_reports_port_in_use():
    held = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    held.bind(("127.0.0.1", 0))
    held.listen(1)
    port = held.getsockname()[1]
    session = UvicornSession(LoopbackOrigin.parse("127.0.0.1", port))
    try:
        report = session.wait_until_ready(timeout=2)
    finally:
        session.join()
        held.close()
    assert report == Failed(FailureReason.PORT_IN_USE)
