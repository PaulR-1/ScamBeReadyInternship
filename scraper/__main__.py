from __future__ import annotations

import argparse

from dotenv import load_dotenv

from scraper.discover import discovery_status
from scraper.extract import parse_page
from scraper.fetch import Fetcher
from scraper.io_utils import load_json, save_json
from scraper.models import MISSING, PartnerRecord


def scrape_target(target: dict, fetcher: Fetcher, settings: dict) -> PartnerRecord:
    missing = settings["missing_value"]
    record = PartnerRecord(
        organization_school=target.get("organization_school", missing),
        contact_person=missing,
        email=missing,
        contact_number=missing,
        role=target.get("role", missing),
        category=target.get("category", missing),
        city=settings.get("city", "Manila"),
        country=settings.get("country", "Philippines"),
        source_url=missing,
        notes=missing,
    )
    prefix = target.get("preferred_email_prefix", "")
    keywords = target.get("person_keywords", [])

    facebook_blocked = False
    for url in target.get("urls", []):
        if "facebook.com" in url.lower():
            facebook_blocked = True
            if record.source_url == missing:
                record.source_url = url
            continue
        html = fetcher.get_text(url)
        if not html:
            continue
        parsed = parse_page(html, preferred_email_prefix=prefix, person_keywords=keywords)
        if record.source_url == missing:
            record.source_url = url
        if record.contact_person == missing and parsed["contact_person"] != MISSING:
            record.contact_person = parsed["contact_person"]
            record.source_url = url
        collect_email = target.get("collect_email", True)
        if collect_email and record.email == missing and parsed["email"] != MISSING:
            record.email = parsed["email"]
            record.source_url = url
        if target.get("collect_phone") and record.contact_number == missing and parsed["contact_number"] != MISSING:
            record.contact_number = parsed["contact_number"]
        if record.email != missing and record.contact_person != missing:
            break

    if record.email == missing and record.contact_number == missing and record.contact_person == missing:
        if facebook_blocked:
            record.notes = "Facebook page exists but was not scraped (Meta blocks automated collection); no public non-Facebook contact found"
        else:
            record.notes = "Public page fetched, but no matching contact fields"
    elif facebook_blocked:
        record.notes = "Facebook page was not scraped (Meta blocks automated collection)"
    return record.fill_missing(missing)


def run(limit: int | None = None) -> None:
    load_dotenv()
    settings = load_json("config/settings.json")
    config = load_json("config/targets.json")
    targets = config["targets"]
    if limit is not None:
        targets = targets[:limit]
    fetcher = Fetcher()
    rows = [scrape_target(target, fetcher, settings).to_json_row() for target in targets]
    payload = {
        "project": "Be Scam Ready / Scam Ready ASEAN school partnership research",
        "scope": config.get("scope", {}),
        "discovery_mode": discovery_status(),
        "missing_value": settings["missing_value"],
        "count": len(rows),
        "partners": rows,
    }
    path = save_json(settings["output_path"], payload)
    print(f"Wrote {len(rows)} records to {path}")
    print(f"Discovery mode: {payload['discovery_mode']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Scrape Manila university public contacts for Be Scam Ready outreach."
    )
    parser.add_argument("--limit", type=int, default=None, help="Only scrape the first N targets.")
    args = parser.parse_args()
    run(limit=args.limit)
