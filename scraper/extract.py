from __future__ import annotations

import re

from bs4 import BeautifulSoup

from scraper.models import MISSING


EMAIL_RE = re.compile(r"[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}", re.IGNORECASE)
PHONE_RE = re.compile(
    r"(?:\+63|0)\s*[-.]?\s*2?\s*[-.]?\s*\d{3,4}\s*[-.]?\s*\d{3,4}(?:\s*(?:local|loc\.?)\s*\d{3,5}(?:\s*/\s*\d{3,5})?)?",
    re.IGNORECASE,
)
ACADEMIC_NAME_RE = re.compile(
    r"((?:Asst\.|Assoc\.|Inst\.|Rev\.|Prof\.|Senior Teacher|Ms\.|Mr\.)\s+"
    r"(?:Prof\.\s+)?[A-Z][A-Za-z.'\-]+(?:\s+[A-Z][A-Za-z.'\-]+){1,5}"
    r"(?:,\s*[A-Za-z./ ]{1,40})?)"
)
SKIP_EMAIL_PARTS = ("noreply", "no-reply", "example.com", "sentry", "wixpress", ".png", ".jpg")
CF_EMAIL_RE = re.compile(r"data-cfemail=[\"']([0-9a-fA-F]+)[\"']")
CF_HREF_RE = re.compile(r"/cdn-cgi/l/email-protection#([0-9a-fA-F]+)")


def decode_cloudflare_email(encoded: str) -> str:
    key = int(encoded[:2], 16)
    chars = [chr(int(encoded[i : i + 2], 16) ^ key) for i in range(2, len(encoded), 2)]
    return "".join(chars)


def extract_cloudflare_emails(html: str) -> list[str]:
    found: list[str] = []
    for encoded in CF_EMAIL_RE.findall(html) + CF_HREF_RE.findall(html):
        try:
            email = decode_cloudflare_email(encoded).lower()
        except ValueError:
            continue
        if "@" not in email:
            continue
        if any(part in email for part in SKIP_EMAIL_PARTS):
            continue
        if email not in found:
            found.append(email)
    return found


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def extract_emails(text: str) -> list[str]:
    found: list[str] = []
    for match in EMAIL_RE.findall(text):
        email = match.lower()
        if any(part in email for part in SKIP_EMAIL_PARTS):
            continue
        if email not in found:
            found.append(email)
    return found


def extract_phones(text: str) -> list[str]:
    found: list[str] = []
    for match in PHONE_RE.findall(text):
        candidate = _clean(match)
        digits = re.sub(r"\D", "", candidate)
        if len(digits) < 8:
            continue
        if candidate not in found:
            found.append(candidate)
    return found


def pick_email(emails: list[str], preferred_prefix: str) -> str:
    if preferred_prefix:
        prefix = preferred_prefix.lower()
        for email in emails:
            if email.startswith(prefix) or prefix in email:
                return email
        return MISSING
    return emails[0] if emails else MISSING


PLAIN_NAME_RE = re.compile(
    r"([A-Z][A-Za-z.'\-]+(?:\s+[A-Z][A-Za-z.'\-]+){1,5})"
)


JUNK_NAME_TOKENS = {
    "and",
    "the",
    "our",
    "board",
    "executive",
    "organization",
    "excellence",
    "technological",
    "committees",
    "more",
    "news",
    "student",
    "organizations",
    "society",
    "computer",
    "science",
    "information",
    "systems",
    "central",
    "hiraya",
    "earth",
    "unicef",
    "unesco",
}


def _name_immediately_before(text: str, keyword: str) -> str:
    pattern = re.compile(rf"{re.escape(keyword)}\b", re.IGNORECASE)
    for match in pattern.finditer(text):
        tokens = re.findall(r"[A-Za-z][A-Za-z.'\-]*", text[: match.start()])
        for count in (3, 2, 4):
            if len(tokens) < count:
                continue
            parts = tokens[-count:]
            if any(part.lower() in JUNK_NAME_TOKENS for part in parts):
                continue
            if not all(part[0].isupper() for part in parts):
                continue
            return " ".join(parts)
    return MISSING


def extract_person(text: str, keywords: list[str]) -> str:
    collapsed = _clean(text)
    for keyword in keywords:
        glued = re.compile(
            rf"({ACADEMIC_NAME_RE.pattern})\s*{re.escape(keyword)}\b",
            re.IGNORECASE,
        )
        match = glued.search(collapsed)
        if match:
            return _clean(match.group(1))

        nearby = _name_immediately_before(collapsed, keyword)
        if nearby != MISSING:
            return nearby
    return MISSING


def parse_page(html: str, preferred_email_prefix: str = "", person_keywords: list[str] | None = None) -> dict[str, str]:
    soup = BeautifulSoup(html, "lxml")
    text = soup.get_text(" ", strip=True)
    mailto = " ".join(a.get("href", "")[7:] for a in soup.select('a[href^="mailto:"]'))
    emails = extract_emails(f"{text} {mailto}")
    for extra in extract_cloudflare_emails(html):
        if extra not in emails:
            emails.append(extra)
    tel = " ".join(a.get("href", "")[4:] for a in soup.select('a[href^="tel:"]'))
    phones = extract_phones(f"{text} {tel}")
    person = extract_person(text, person_keywords or [])
    return {
        "contact_person": person,
        "email": pick_email(emails, preferred_email_prefix),
        "contact_number": phones[0] if phones else MISSING,
    }
