"""Entry point: python -m app"""

from __future__ import annotations

import webbrowser

import uvicorn

from app.core.config import get_config, load_dotenv


def main() -> None:
    load_dotenv()
    config = get_config()
    url = f"http://{config.host}:{config.port}"
    print(f"Taglish Transcriber running at {url}  (Ctrl+C to stop)")
    try:
        webbrowser.open(url)
    except Exception:
        pass
    uvicorn.run("app.main:app", host=config.host, port=config.port, log_level="info")


if __name__ == "__main__":
    main()
