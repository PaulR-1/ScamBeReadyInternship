"""Desktop shell. The window reads one readiness report. It does not stop the server."""

from __future__ import annotations

import asyncio
import ctypes
import html
import logging
import socket
import threading
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Protocol

logger = logging.getLogger("app")

_BACKLOG = 2048
_ICON = Path(__file__).resolve().parent / "web" / "static" / "taglish.ico"
_APP_ID = "ScamBeReady.TaglishTranscriber"


class AppConfig(Protocol):
    """Fields this shell reads. The real AppConfig has more. FastAPI keeps those."""

    host: str
    port: int


class DesktopRefused(Exception):
    """Host is not loopback, or the port is outside 1 to 65535. No socket is opened."""


class WindowUnavailable(Exception):
    """WebView2 did not start.

    serve_in_window joins the session first. It then shows a message box when it
    constructed the window itself. A caller-supplied window lets this propagate
    after that join.
    """


class FailureReason(Enum):
    PORT_IN_USE = "port_in_use"
    TIMED_OUT = "timed_out"
    SERVER_CRASHED = "server_crashed"


FAILURE_TEXT: dict[FailureReason, str] = {
    FailureReason.PORT_IN_USE: "Taglish Transcriber is already open.",
    FailureReason.TIMED_OUT: (
        "Taglish Transcriber did not finish starting. Close this window and try again."
    ),
    FailureReason.SERVER_CRASHED: (
        "Taglish Transcriber stopped. The log is %LOCALAPPDATA%\\TaglishTranscriber\\app.log."
    ),
}


@dataclass(frozen=True)
class LoopbackOrigin:
    """The only address the shell binds or opens. home is derived from these two fields."""

    host: str
    port: int

    def __post_init__(self) -> None:
        if self.host not in {"127.0.0.1", "localhost"} or type(self.port) is not int:
            raise DesktopRefused(f"Refusing {self.host}:{self.port}")
        if self.port < 1 or self.port > 65535:
            raise DesktopRefused(f"Refusing {self.host}:{self.port}")

    @staticmethod
    def parse(host: str, port: int) -> LoopbackOrigin:
        return LoopbackOrigin(host, port)

    @property
    def home(self) -> str:
        return f"http://{self.host}:{self.port}/"


@dataclass(frozen=True)
class Listening:
    origin: LoopbackOrigin


@dataclass(frozen=True)
class Failed:
    reason: FailureReason


class Session(Protocol):
    """Server actor. The window may wait and read. It may not stop the server."""

    origin: LoopbackOrigin

    def wait_until_ready(self, timeout: float = 30.0) -> Listening | Failed:
        """Return the first report. Called once, off the UI thread."""

    def request_stop(self) -> None:
        """Idempotent. Safe before listen, after listen, and after join."""

    def join(self) -> None:
        """Wait until the server thread is gone. No deadline here."""


class Window(Protocol):
    def show(self, session: Session) -> None:
        """Block until the user closes the window. Do not call request_stop."""


class _Life(Enum):
    """One field. JOINED is not also RUNNING."""

    RUNNING = "running"
    STOPPING = "stopping"
    JOINED = "joined"


class UvicornSession:
    """Production Session. Binds on the caller thread. Serves on a non-daemon thread."""

    def __init__(self, origin: LoopbackOrigin) -> None:
        self.origin = origin
        self._life = _Life.RUNNING
        self._report: Listening | Failed | None = None
        self._ready = threading.Event()
        self._lock = threading.Lock()
        self._server: Any = None
        self._sock: socket.socket | None = None
        self._thread: threading.Thread | None = None

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            # Leave SO_REUSEADDR off. On Windows that keeps the port exclusive, so a
            # second process fails here and never enters the FastAPI lifespan.
            sock.bind((origin.host, origin.port))
            sock.listen(_BACKLOG)
        except OSError:
            sock.close()
            self._publish(Failed(FailureReason.PORT_IN_USE))
            return

        self._sock = sock
        # Non-daemon so process exit waits until the lifespan closes SQLite.
        thread = threading.Thread(target=self._serve, name="taglish-http", daemon=False)
        self._thread = thread
        thread.start()

    def wait_until_ready(self, timeout: float = 30.0) -> Listening | Failed:
        report = self._published()
        if report is not None:
            return report
        if self._ready.wait(timeout):
            report = self._published()
            if report is not None:
                return report
        self.request_stop()
        # A late Listening must not replace this return value.
        return Failed(FailureReason.TIMED_OUT)

    def request_stop(self) -> None:
        with self._lock:
            if self._life is not _Life.RUNNING:
                return
            self._life = _Life.STOPPING
            server = self._server
        if server is not None:
            server.should_exit = True

    def join(self) -> None:
        # No deadline. worker.stop inside the lifespan already waits at most 5 seconds,
        # and store.close has to run after that.
        with self._lock:
            if self._life is _Life.JOINED:
                return
            if self._life is _Life.RUNNING:
                self._life = _Life.STOPPING
            server = self._server
            thread = self._thread
        if server is not None:
            server.should_exit = True
        if thread is not None and thread is not threading.current_thread():
            thread.join()
        with self._lock:
            self._life = _Life.JOINED

    def _published(self) -> Listening | Failed | None:
        with self._lock:
            return self._report

    def _publish(self, report: Listening | Failed) -> None:
        with self._lock:
            if self._report is not None:
                return
            self._report = report
            self._ready.set()

    def _running(self) -> bool:
        with self._lock:
            return self._life is _Life.RUNNING

    def _close_sock(self) -> None:
        sock = self._sock
        self._sock = None
        if sock is None:
            return
        try:
            sock.close()
        except OSError:
            pass

    def _serve(self) -> None:
        try:
            if self._sock is None or not self._running():
                return
            import uvicorn

            if not self._running():
                return
            config = uvicorn.Config(
                "app.main:app",
                host=self.origin.host,
                port=self.origin.port,
                log_level="info",
            )
            server = uvicorn.Server(config)
            _disable_signal_handlers(server)
            with self._lock:
                self._server = server
                running = self._life is _Life.RUNNING
            if not running:
                server.should_exit = True
                return
            sock = self._sock
            if sock is None:
                return

            async def _run() -> None:
                task = asyncio.create_task(server.serve(sockets=[sock]))
                while not server.started and not task.done():
                    await asyncio.sleep(0.05)
                if server.started:
                    self._publish(Listening(self.origin))
                await task

            try:
                asyncio.run(_run())
            except (Exception, SystemExit):
                logger.exception("HTTP server failed")
                self._publish(Failed(FailureReason.SERVER_CRASHED))
                return
            if not server.started:
                self._publish(Failed(FailureReason.SERVER_CRASHED))
        finally:
            self._close_sock()


def _disable_signal_handlers(server: object) -> None:
    """The UI thread owns process exit. This thread must not install signal handlers."""

    current = getattr(server, "install_signal_handlers", None)
    if callable(current):
        setattr(server, "install_signal_handlers", lambda: None)
        return
    setattr(server, "install_signal_handlers", False)


class WebViewWindow:
    """Production Window. WebView2 on the main thread. No address bar. No browser chrome."""

    def show(self, session: Session) -> None:
        try:
            import webview
        except ImportError as exc:
            raise WindowUnavailable(
                "Taglish Transcriber could not open a window because pywebview is not installed."
            ) from exc

        claim_app_identity()
        # pywebview cancels downloads unless this is on. The save dialog opens in Downloads.
        webview.settings["ALLOW_DOWNLOADS"] = True
        window = webview.create_window(
            title="Taglish Transcriber",
            html=_holding_page("Starting Taglish Transcriber"),
            width=1120,
            height=760,
            min_size=(800, 600),
            text_select=True,
            background_color="#62844a",
        )

        def _open_when_ready() -> None:
            _apply_window_icon()
            report = session.wait_until_ready()
            if isinstance(report, Listening):
                window.load_url(session.origin.home)
                return
            window.load_html(_holding_page(FAILURE_TEXT[report.reason]))

        try:
            webview.start(_open_when_ready)
        except Exception as exc:
            if _missing_webview(exc):
                raise WindowUnavailable(
                    "Taglish Transcriber needs the Microsoft Edge WebView2 runtime."
                ) from exc
            raise


def claim_app_identity() -> None:
    """Tell Windows this process is Taglish Transcriber, not pythonw.exe."""

    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(_APP_ID)


def _apply_window_icon() -> None:
    """Put the cutting-mat icon on every visible window of this process.

    LoadImage only accepts a classic bitmap icon. A 64-bit HICON must stay pointer-sized.
    """

    if not _ICON.is_file():
        return
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32
    user32.LoadImageW.restype = ctypes.c_void_p
    user32.SendMessageW.argtypes = [
        ctypes.c_void_p,
        ctypes.c_uint,
        ctypes.c_size_t,
        ctypes.c_void_p,
    ]
    user32.GetWindowThreadProcessId.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_ulong)]
    image_icon = 1
    load_from_file = 0x10
    icons = []
    for size in (32, 16):
        handle = user32.LoadImageW(None, str(_ICON), image_icon, size, size, load_from_file)
        if handle:
            icons.append((32 if size == 32 else 16, handle))
    if not icons:
        return
    pid = kernel32.GetCurrentProcessId()
    hwnds: list[int] = []

    @ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
    def visit(hwnd: int, _lparam: int) -> bool:
        owner = ctypes.c_ulong()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(owner))
        if owner.value == pid and user32.IsWindowVisible(hwnd):
            hwnds.append(hwnd)
        return True

    user32.EnumWindows(visit, 0)
    for hwnd in hwnds:
        for size, handle in icons:
            user32.SendMessageW(hwnd, 0x80, 1 if size == 32 else 0, handle)


def _missing_webview(exc: BaseException) -> bool:
    if type(exc).__name__ in {"WebViewException", "BrowserNotFound"}:
        return True
    text = str(exc).lower()
    return "webview2" in text or "edge chromium" in text


_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Taglish Transcriber</title>
<style>
html, body {
  margin: 0;
  height: 100%;
  background: #62844a;
  color: #f6f1e6;
}
body {
  min-height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  padding: 48px;
  box-sizing: border-box;
}
h1 {
  margin: 0 0 16px;
  font-family: Impact, Haettenschweiler, "Arial Narrow Bold", sans-serif;
  font-size: 48px;
  font-weight: 400;
  letter-spacing: 0.02em;
}
p {
  margin: 0;
  max-width: 36rem;
  font-family: "Segoe UI", sans-serif;
  font-size: 20px;
  line-height: 1.45;
}
</style>
</head>
<body>
<h1>Taglish Transcriber</h1>
<p>__MESSAGE__</p>
</body>
</html>
"""


def _holding_page(message: str) -> str:
    """Inline document. Background #62844a, text #f6f1e6, Impact title, Segoe UI message."""

    return _PAGE.replace("__MESSAGE__", html.escape(message, quote=True))


def _tell_the_user(message: str) -> None:
    """Windows message box. Used only when no WebView2 window exists to paint the error."""

    import ctypes

    ctypes.windll.user32.MessageBoxW(0, message, "Taglish Transcriber", 0x10)


def serve_in_window(session: Session, window: Window | None = None) -> None:
    """Show the session, then stop it, including when show raises."""

    supplied = window is not None
    try:
        try:
            if window is None:
                window = WebViewWindow()
            window.show(session)
        finally:
            session.request_stop()
            session.join()
    except WindowUnavailable as exc:
        if supplied:
            raise
        _tell_the_user(str(exc))


def run_desktop(config: AppConfig) -> None:
    """Block until the window is closed and the server thread has joined."""

    origin = LoopbackOrigin.parse(config.host, config.port)
    serve_in_window(UvicornSession(origin))


def run_headless_server() -> None:
    """Terminal entry. Uvicorn only. No window and no system browser."""

    import uvicorn

    from app.core.config import get_config

    config = get_config()
    url = f"http://{config.host}:{config.port}"
    print(f"Taglish Transcriber running at {url}  (Ctrl+C to stop)")
    uvicorn.run("app.main:app", host=config.host, port=config.port, log_level="info")
