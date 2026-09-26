"""Update student_organizations with verified AWS / Google / tech orgs. Officials unchanged."""
from __future__ import annotations

import json
from pathlib import Path

MISSING = "Did not find any info"
ROOT = Path(__file__).resolve().parents[1] / "data"
BENILDE_LIST = (
    "https://www.benilde.edu.ph/wp-content/uploads/2024/11/"
    "List-of-Accredited-Student-Org-and-Recognized-Student-Groups-AY-24-25.docx.pdf"
)
NO_AWS_GOOGLE = (
    "No AWS Learning Club / AWS Student Builder Group or GDG/GDSC chapter with a "
    "public officer email or phone was found on official school pages or gdg.community.dev "
    "for this campus. Social-only mentions were not used."
)


def rec(org, role, category, person, email, phone, source, notes=MISSING):
    return {
        "Organization + School": org,
        "Role": role,
        "Category": category,
        "Contact person": person,
        "Email": email,
        "A possible contact number": phone,
        "Source URL": source,
        "Notes": notes,
    }


def patch(filename: str, orgs: list[dict]) -> None:
    path = ROOT / filename
    data = json.loads(path.read_text(encoding="utf-8"))
    data["student_organizations"] = orgs
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(path)


TECH = "Organization focusing on tech"
CIVIC = "Organization that can help Be Scam Ready (community outreach)"

patch(
    "dls_csb_manila.json",
    [
        rec(
            "De La Salle-College of Saint Benilde — BASTION",
            "Cybersecurity student organization (accredited academic cluster)",
            TECH,
            MISSING,
            "bastion@benilde.edu.ph",
            MISSING,
            BENILDE_LIST,
            "Named with this email on the official Center for Student Life accredited-org list (AY 2024-2025). "
            "The PDF does not print the word cybersecurity next to the name. Benilde's official BeSPARK Engage listing "
            "(https://dlscsb-ph.campuslabs.com/engage/organization/bastion) describes BASTION as the student organization "
            "focused on cybersecurity awareness. No officer name or phone on those pages.",
        ),
        rec(
            "De La Salle-College of Saint Benilde — Google Developers Student Club in Benilde",
            "Google Developers Student Club (accredited special-interest cluster)",
            TECH,
            MISSING,
            "gdscbenilde@benilde.edu.ph",
            MISSING,
            BENILDE_LIST,
            "Official accredited-org list (AY 2024-2025). No officer name or phone. No matching gdg.community.dev campus page was verified in this pass.",
        ),
        rec(
            "De La Salle-College of Saint Benilde — Association of Information Management (AIM)",
            "Tech / information-management student organization",
            TECH,
            MISSING,
            "aim@benilde.edu.ph",
            MISSING,
            BENILDE_LIST,
            "Official accredited-org list (AY 2024-2025). No officer name or phone.",
        ),
        rec(
            "De La Salle-College of Saint Benilde — Computer Business Association (CBA)",
            "Tech / computer-business student organization",
            TECH,
            MISSING,
            "cba@benilde.edu.ph",
            MISSING,
            BENILDE_LIST,
            "Official accredited-org list (AY 2024-2025). No officer name or phone.",
        ),
        rec(
            "De La Salle-College of Saint Benilde — Society of Analytics and Business Intelligence (SABI)",
            "Analytics / tech student organization",
            TECH,
            MISSING,
            "sabi@benilde.edu.ph",
            MISSING,
            BENILDE_LIST,
            "Official accredited-org list (AY 2024-2025). No officer name or phone.",
        ),
        rec(
            "De La Salle-College of Saint Benilde — AWS student organizations",
            "AWS Learning Club / AWS Student Builder Group",
            TECH,
            MISSING,
            MISSING,
            MISSING,
            BENILDE_LIST,
            "AWS is not named on the official AY 2024-2025 accredited-org list.",
        ),
    ],
)

patch(
    "dlsu_manila.json",
    [
        rec(
            "De La Salle University — La Salle Computer Society (LSCS)",
            "Professional organization of the College of Computer Studies",
            TECH,
            MISSING,
            MISSING,
            MISSING,
            "https://old.dlsu.edu.ph/student-organizations/",
            "Named on the official DLSU student-organizations page as the only professional organization of CCS. No LSCS officer email or phone on that page. College office email computerstudies@dlsu.edu.ph was not copied as the org inbox.",
        ),
        rec(
            "De La Salle University — GDG on Campus",
            "Google Developer Groups on Campus",
            TECH,
            "Aebrahm Clyde Ramos (Chief Executive Officer)",
            MISSING,
            MISSING,
            "https://gdg.community.dev/gdg-on-campus-de-la-salle-university-manila-philippines/",
            "Official GDG on Campus chapter page (also indexed via event listings). No organizer email or phone published there. Direct fetch of the chapter URL returned 404 during this pass.",
        ),
        rec(
            "De La Salle University — AWS student organizations",
            "AWS Learning Club / AWS Student Builder Group",
            TECH,
            MISSING,
            MISSING,
            MISSING,
            MISSING,
            "No AWS student club with a public officer contact was found on official DLSU pages. A DLSU School of Lifelong Learning AWS mentorship course is not a student org.",
        ),
    ],
)

patch(
    "ateneo_de_manila.json",
    [
        rec(
            "Ateneo de Manila University — Computer Society of the Ateneo (CompSAt)",
            "Tech student organization",
            TECH,
            MISSING,
            "hello@compsat.org",
            MISSING,
            "https://compsat.org/contact-us",
            "Official CompSAt site. Address listed as Room 303, MVP Center for Student Leadership. No phone on that page.",
        ),
        rec(
            "Ateneo de Manila University — GDG on Campus",
            "Google Developer Groups on Campus",
            TECH,
            "Samantha Athea Serrano (Chapter Lead)",
            MISSING,
            MISSING,
            "https://gdg.community.dev/gdg-on-campus-ateneo-de-manila-university-quezon-city-philippines/",
            "Official GDG on Campus chapter page. No organizer email or phone. Direct fetch returned 404 during this pass; listing is from that official community URL.",
        ),
        rec(
            "Ateneo de Manila University — AWS student organizations",
            "AWS Learning Club / AWS Student Builder Group",
            TECH,
            MISSING,
            MISSING,
            MISSING,
            MISSING,
            "No AWS student club with a public officer contact was found on official Ateneo de Manila pages.",
        ),
    ],
)

patch(
    "up_diliman.json",
    [
        rec(
            "University of the Philippines Diliman — Association for Computing Machinery Student Chapter (UP ACM)",
            "Tech student organization",
            TECH,
            MISSING,
            "contactus@upacm.net",
            MISSING,
            "https://upacm.net/contact/",
        ),
        rec(
            "University of the Philippines Diliman — GDG on Campus / AWS student organizations",
            "GDG/GDSC or AWS campus chapter",
            TECH,
            MISSING,
            MISSING,
            MISSING,
            MISSING,
            "No GDG on Campus chapter page for UP Diliman and no AWS Learning Club with a public officer contact were verified.",
        ),
        rec(
            "University of the Philippines Diliman — Ugnayan ng Pahinungod / Oblation Corps",
            "University volunteer / community service office",
            CIVIC,
            "Francis Grace H. Duka-Pante",
            "pahinungod.upd@up.edu.ph",
            "(632) 85463607",
            "https://upd.edu.ph/up-diliman-officials/",
            "Listed as Director, UPD Ugnayan ng Pahinungod/Oblation Corps.",
        ),
    ],
)

# UST already has a full tech-org set including AWS UST; keep existing by merging a GDG check only if missing.
ust = json.loads((ROOT / "ust.json").read_text(encoding="utf-8"))
if not any("GDG" in o.get("Organization + School", "") for o in ust["student_organizations"]):
    ust["student_organizations"].append(
        rec(
            "University of Santo Tomas — GDG on Campus",
            "Google Developer Groups on Campus",
            TECH,
            MISSING,
            MISSING,
            MISSING,
            MISSING,
            "No GDG on Campus chapter page for UST was verified. AWS Learning Club is already listed from https://www.aws-ust.org/.",
        )
    )
    (ROOT / "ust.json").write_text(json.dumps(ust, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(ROOT / "ust.json")

patch(
    "pup_sta_mesa.json",
    [
        rec(
            "Polytechnic University of the Philippines — AWS Cloud Club PUP",
            "AWS Cloud Club (university-wide)",
            TECH,
            MISSING,
            "awscloudclub.pupmnl@gmail.com",
            MISSING,
            "https://awsccpup.cloud/",
            "Official AWS Cloud Club PUP site Contact Us block. No officer name or phone on that page.",
        ),
        rec(
            "Polytechnic University of the Philippines — GDG on Campus",
            "Google Developer Groups on Campus",
            TECH,
            "Shunrenn Locaylocay (Chief Executive Officer); Salvador Vincent Javier (Chief Executive Officer)",
            MISSING,
            MISSING,
            "https://gdg.community.dev/gdg-on-campus-polytechnic-university-of-the-philippines-manila-philippines/",
            "Official GDG on Campus chapter page. Two people are labeled Chief Executive Officer. No organizer email or phone.",
        ),
    ],
)

patch(
    "plm.json",
    [
        rec(
            "Pamantasan ng Lungsod ng Maynila — GDG on Campus",
            "Google Developer Groups on Campus",
            TECH,
            "Mariebethel Roussamiere E. Miranda (Chief Executive Officer)",
            MISSING,
            MISSING,
            "https://gdg.community.dev/gdg-on-campus-pamantasan-ng-lungsod-ng-maynila-manila-philippines/",
            "Official GDG on Campus chapter page. No organizer email or phone.",
        ),
        rec(
            "Pamantasan ng Lungsod ng Maynila — AWS student organizations",
            "AWS Learning Club / AWS Student Builder Group",
            TECH,
            MISSING,
            MISSING,
            MISSING,
            MISSING,
            NO_AWS_GOOGLE.replace("GDG/GDSC chapter with a public officer email or phone was found on official school pages or gdg.community.dev for this campus. ", "AWS club "),
        ),
    ],
)

patch(
    "mapua_intramuros.json",
    [
        rec(
            "Mapúa University — GDG on Campus",
            "Google Developer Groups on Campus",
            TECH,
            "AG Aparece (Chief Executive Officer); John Michael Elaurza (Chief Executive Officer)",
            MISSING,
            MISSING,
            "https://gdg.community.dev/gdg-on-campus-mapua-university-manila-philippines/",
            "Official GDG on Campus chapter page. Two people are labeled Chief Executive Officer. No organizer email or phone.",
        ),
        rec(
            "Mapúa University — other tech / AWS student organizations",
            "College computing orgs / AWS campus chapter",
            TECH,
            MISSING,
            MISSING,
            MISSING,
            MISSING,
            "No Mapúa student-org directory with computing-society emails was verified. No AWS club with a public officer contact was found on official Mapúa pages.",
        ),
    ],
)

patch(
    "ue_manila.json",
    [
        rec(
            "University of the East Manila — Computer Students Society (COMSSO)",
            "CCSS student organization",
            TECH,
            MISSING,
            MISSING,
            MISSING,
            "https://www.ue.edu.ph/mla/organization-2/",
            "Named on the official recognized-student-organizations page. No officer, email, or phone for COMSSO on that page.",
        ),
        rec(
            "University of the East Manila — Society of Computer Engineering Students (SCpES)",
            "Computer engineering student organization",
            TECH,
            MISSING,
            MISSING,
            MISSING,
            "https://www.ue.edu.ph/mla/organization-2/",
            "Named on the official recognized-student-organizations page. No officer, email, or phone on that page.",
        ),
        rec(
            "University of the East Manila — AWS / Google student organizations",
            "AWS Learning Club or GDG/GDSC on campus",
            TECH,
            MISSING,
            MISSING,
            MISSING,
            MISSING,
            NO_AWS_GOOGLE,
        ),
    ],
)

patch(
    "ue_caloocan.json",
    [
        rec(
            "University of the East Caloocan — Association of Computer Studies and Systems Students (ACSS)",
            "Computer studies student organization",
            TECH,
            MISSING,
            MISSING,
            MISSING,
            "https://www.ue.edu.ph/cal/student-organization/",
            "Named on the official recognized-org list. That page is labeled 2020-2021. No officer, email, or phone.",
        ),
        rec(
            "University of the East Caloocan — League of Information Technology Students (LITS)",
            "IT student organization",
            TECH,
            MISSING,
            MISSING,
            MISSING,
            "https://www.ue.edu.ph/cal/student-organization/",
            "Named on the official recognized-org list (labeled 2020-2021). No officer, email, or phone.",
        ),
        rec(
            "University of the East Caloocan — Computer Engineering Students Society (COESS)",
            "Computer engineering student organization",
            TECH,
            MISSING,
            MISSING,
            MISSING,
            "https://www.ue.edu.ph/cal/student-organization/",
            "Named on the official recognized-org list (labeled 2020-2021). No officer, email, or phone.",
        ),
        rec(
            "University of the East Caloocan — IEEE University of the East Student Branch (IEEE-UESB)",
            "IEEE student branch",
            TECH,
            MISSING,
            MISSING,
            MISSING,
            "https://www.ue.edu.ph/cal/student-organization/",
            "Named on the official recognized-org list (labeled 2020-2021). No officer, email, or phone.",
        ),
        rec(
            "University of the East Caloocan — AWS / Google student organizations",
            "AWS Learning Club or GDG/GDSC on campus",
            TECH,
            MISSING,
            MISSING,
            MISSING,
            MISSING,
            NO_AWS_GOOGLE,
        ),
    ],
)

patch(
    "nu_manila.json",
    [
        rec(
            "National University Manila — College of Computing and Information Technologies Student Council",
            "College student council (tech)",
            TECH,
            "Mapanao, Jessy Cassandra M.",
            MISSING,
            MISSING,
            "https://national-u.edu.ph/nu-manila/student-organizations/nucsg-college-student-council-2024-2025/",
            "President named on the official 2024-2025 student council page. Current term was not reconfirmed. No email or phone.",
        ),
        rec(
            "National University Manila — GDG on Campus",
            "Google Developer Groups on Campus",
            TECH,
            "Gwyenth Lim (Campus Organizer); Franze Young (President)",
            MISSING,
            MISSING,
            "https://gdg.community.dev/gdg-on-campus-national-university-manila-campus-manila-philippines/",
            "Official GDG on Campus chapter page. No organizer email or phone. An AWS Student Builder Group listing exists for NU Baliwag, which is a different campus and was not copied here.",
        ),
    ],
)

patch(
    "lpu_intramuros.json",
    [
        rec(
            "Lyceum of the Philippines University Manila — College of Technology Student Government (COT SG)",
            "College student government (technology)",
            TECH,
            MISSING,
            MISSING,
            MISSING,
            "https://manila.lpu.edu.ph/campus-life/student-organizations/",
            "Named on the official student-organizations page. No officer, email, or phone on that listing.",
        ),
        rec(
            "Lyceum of the Philippines University Manila — AWS / Google student organizations",
            "AWS Learning Club or GDG/GDSC on campus",
            TECH,
            MISSING,
            MISSING,
            MISSING,
            MISSING,
            NO_AWS_GOOGLE,
        ),
    ],
)

# Remaining campuses: keep existing tech rows if already specific; otherwise keep a clear missing AWS/Google + any known tech row.
# TUP already has COMPASS / Tech Guild / GDG — leave as-is except add AWS missing if absent.
tup = json.loads((ROOT / "tup_ermita.json").read_text(encoding="utf-8"))
if not any("AWS" in o.get("Organization + School", "") for o in tup["student_organizations"]):
    tup["student_organizations"].append(
        rec(
            "Technological University of the Philippines — AWS student organizations",
            "AWS Learning Club / AWS Student Builder Group",
            TECH,
            MISSING,
            MISSING,
            MISSING,
            MISSING,
            "No AWS campus club with a public officer contact was found on official TUP pages. GDG on Campus is already listed.",
        )
    )
    (ROOT / "tup_ermita.json").write_text(json.dumps(tup, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(ROOT / "tup_ermita.json")

for fname, school in [
    ("tip_manila.json", "Technological Institute of the Philippines Manila"),
    ("tip_quezon_city.json", "Technological Institute of the Philippines Quezon City"),
    ("san_beda_manila.json", "San Beda University"),
    ("pnu.json", "Philippine Normal University"),
    ("ceu_mendiola.json", "Centro Escolar University Manila"),
    ("miriam_college.json", "Miriam College"),
    ("umak.json", "University of Makati"),
    ("rtu_mandaluyong.json", "Rizal Technological University"),
    ("feu_manila.json", "Far Eastern University Manila"),
    ("adamson.json", "Adamson University"),
    ("up_manila.json", "University of the Philippines Manila"),
]:
    data = json.loads((ROOT / fname).read_text(encoding="utf-8"))
    existing = data["student_organizations"]
    # Keep non-placeholder civic / named orgs; replace generic AWS/Google or "tech / civic" stubs.
    keep = [
        o
        for o in existing
        if "AWS / Google" not in o.get("Organization + School", "")
        and "tech / civic" not in o.get("Organization + School", "").lower()
        and "tech student organizations" not in o.get("Organization + School", "").lower()
    ]
    keep.append(
        rec(
            f"{school} — AWS / Google / other tech student organizations",
            "AWS, GDG/GDSC, or computing student organizations",
            TECH,
            MISSING,
            MISSING,
            MISSING,
            MISSING,
            NO_AWS_GOOGLE
            + " No official non-Facebook computing-society directory with officer emails was verified for this campus in this pass.",
        )
    )
    data["student_organizations"] = keep
    (ROOT / fname).write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(ROOT / fname)
