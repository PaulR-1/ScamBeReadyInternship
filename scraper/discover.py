"""Optional later: ask Gemini / Google Search for more school URLs.

This module is a stub so the foundation can run without API keys.
"""

from __future__ import annotations

import os


def discovery_status() -> str:
    gemini = os.getenv("GEMINI_API_KEY", "").strip()
    cse_key = os.getenv("GOOGLE_CSE_API_KEY", "").strip()
    cse_cx = os.getenv("GOOGLE_CSE_CX", "").strip()
    if gemini and cse_key and cse_cx:
        return "ready_for_grounded_discovery"
    if gemini:
        return "gemini_only_unreliable_urls"
    return "seed_list_only"


def discover_school_urls() -> list[dict[str, str]]:
    """Reserved for a later step. Returns nothing until APIs are wired."""
    return []
