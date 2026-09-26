from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


MISSING = "Did not find any info"


@dataclass
class PartnerRecord:
    organization_school: str
    contact_person: str
    email: str
    contact_number: str
    role: str = MISSING
    category: str = MISSING
    city: str = "Manila"
    country: str = "Philippines"
    source_url: str = MISSING
    notes: str = MISSING

    def fill_missing(self, missing: str = MISSING) -> "PartnerRecord":
        for field_name, value in asdict(self).items():
            if value is None or (isinstance(value, str) and not value.strip()):
                setattr(self, field_name, missing)
        return self

    def to_json_row(self) -> dict[str, Any]:
        self.fill_missing()
        return {
            "Organization + School": self.organization_school,
            "Contact person": self.contact_person,
            "Email": self.email,
            "A possible contact number": self.contact_number,
            "Role": self.role,
            "Category": self.category,
            "City": self.city,
            "Country": self.country,
            "Source URL": self.source_url,
            "Notes": self.notes,
        }
