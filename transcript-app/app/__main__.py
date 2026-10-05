"""Entry point: python -m app"""

from __future__ import annotations

import sys

from app.core.config import get_config, load_dotenv
from app.desktop import claim_app_identity, run_desktop, run_headless_server


def main() -> None:
    load_dotenv()
    claim_app_identity()
    if "--server" in sys.argv:
        run_headless_server()
        return
    run_desktop(get_config())


if __name__ == "__main__":
    main()
