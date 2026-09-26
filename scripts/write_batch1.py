"""Write Batch 1 campus JSON files from verified official-page facts only."""
from __future__ import annotations

import json
from pathlib import Path

MISSING = "Did not find any info"
ROOT = Path(__file__).resolve().parents[1] / "data"


def rec(
    org: str,
    role: str,
    category: str,
    person: str,
    email: str,
    phone: str,
    source: str,
    notes: str = MISSING,
) -> dict:
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


def dump(filename: str, payload: dict) -> None:
    path = ROOT / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(path)


POLICY = (
    "Only information published on official public pages is recorded. "
    "No invented, guessed, or reused contacts. Missing fields use "
    f"'{MISSING}'."
)


def campus(university, campus, city, officials, orgs, extra=None):
    payload = {
        "university": university,
        "campus": campus,
        "city": city,
        "batch": "1_top_10",
        "policy": POLICY,
        "officials": officials,
        "student_organizations": orgs,
    }
    if extra:
        payload.update(extra)
    return payload


files = {}

files["up_diliman.json"] = campus(
    "University of the Philippines Diliman",
    "Diliman",
    "Quezon City",
    [
        rec(
            "University of the Philippines Diliman — College of Engineering",
            "Dean, College of Engineering",
            "Dean",
            "Maria Antonia N. Tanchuling",
            "upengg@coe.upd.edu.ph",
            "(632) 8981-8500 local 3101 to 3104",
            "https://upd.edu.ph/up-diliman-officials/",
            "College office email and numbers also listed on https://coe.upd.edu.ph/",
        ),
        rec(
            "University of the Philippines Diliman — Office of the Vice Chancellor for Student Affairs",
            "Vice Chancellor for Student Affairs",
            "Student affairs official",
            "Jose Carlo G. de Pano",
            "ovcsa.upd@up.edu.ph",
            "(632) 8981-8500 local 2587, 2588",
            "https://upd.edu.ph/up-diliman-officials/",
        ),
        rec(
            "University of the Philippines Diliman — Office of Student Projects and Activities",
            "Office of Student Projects and Activities (student organizations office)",
            "Student affairs official",
            MISSING,
            "ospa.upd@up.edu.ph",
            "(632) 8981-8671 to 72",
            "https://upd.edu.ph/up-diliman-officials/",
            "Officials page lists the office and contacts but not a named director.",
        ),
    ],
    [
        rec(
            "University of the Philippines Diliman — Association for Computing Machinery Student Chapter (UP ACM)",
            "Tech student organization",
            "Organization focusing on tech",
            MISSING,
            "contactus@upacm.net",
            MISSING,
            "https://upacm.net/contact/",
        ),
        rec(
            "University of the Philippines Diliman — Ugnayan ng Pahinungod / Oblation Corps",
            "University volunteer / community service office",
            "Organization that can help Be Scam Ready (community outreach)",
            "Francis Grace H. Duka-Pante",
            "pahinungod.upd@up.edu.ph",
            "(632) 85463607",
            "https://upd.edu.ph/up-diliman-officials/",
            "Listed as Director, UPD Ugnayan ng Pahinungod/Oblation Corps.",
        ),
    ],
)

files["ateneo_de_manila.json"] = campus(
    "Ateneo de Manila University",
    "Loyola Heights",
    "Quezon City",
    [
        rec(
            "Ateneo de Manila University — School of Science and Engineering",
            "Dean, School of Science and Engineering",
            "Dean",
            "Dr. Raphael A. Guerrero",
            MISSING,
            MISSING,
            "https://www.ateneo.edu/memorandum/2026/05/leadership-appointments-higher-education-cluster-school-year-2026-2027-he",
            "Named in official HE Memo Y4.29 for SY 2026-2027 (term 1 June 2024 to 31 May 2027). No email or phone on that memo.",
        ),
        rec(
            "Ateneo de Manila University — Office of Student Affairs and Formation",
            "Director of Student Affairs and Formation",
            "Student affairs official",
            "Mr. Dennis Ryan V. Cruz",
            MISSING,
            MISSING,
            "https://www.ateneo.edu/memorandum/2026/05/leadership-appointments-higher-education-cluster-school-year-2026-2027-he",
            "Named in official HE Memo Y4.29 (1 June 2026 to 31 May 2029). No email or phone on that memo.",
        ),
        rec(
            "Ateneo de Manila University — Associate Dean for Student Affairs",
            "Associate Dean for Student Affairs",
            "Student affairs official",
            "Atty. Giovanni F. Vallente",
            MISSING,
            MISSING,
            "https://www.ateneo.edu/memorandum/2026/05/leadership-appointments-higher-education-cluster-school-year-2026-2027-he",
            "Named in official HE Memo Y4.29. No email or phone on that memo.",
        ),
        rec(
            "Ateneo de Manila University — Office of Student Affairs and Services",
            "Director, Office of Student Affairs and Services",
            "Student affairs official",
            "Mr. Rene Salvador R. San Andres",
            MISSING,
            MISSING,
            "https://www.ateneo.edu/memorandum/2026/05/leadership-appointments-higher-education-cluster-school-year-2026-2027-he",
            "Named in official HE Memo Y4.29 (1 June 2026 to 31 May 2027). Public student-affairs pages returned HTTP 409 during this pass, so emails were not taken from those pages.",
        ),
    ],
    [
        rec(
            "Ateneo de Manila University — tech / civic student organizations",
            "Student organizations",
            "Organization focusing on tech",
            MISSING,
            MISSING,
            MISSING,
            MISSING,
            "No official non-Facebook org directory with officer emails/phones was verified in this pass. If orgs exist only on Facebook, they were not scraped.",
        )
    ],
)

files["dlsu_manila.json"] = campus(
    "De La Salle University",
    "Taft Avenue, Manila",
    "Manila",
    [
        rec(
            "De La Salle University — College of Computer Studies",
            "Dean, College of Computer Studies",
            "Dean",
            "Dr. Ethel Joy Chua Ong",
            "computerstudies@dlsu.edu.ph",
            "(632) 8536-0276",
            "https://www.dlsu.edu.ph/college-administration/",
            "Dean name from current college-administration page. College email and CCS direct line from https://old.dlsu.edu.ph/colleges/ccs/contact-information/ (DLSU CCS contact page). Current administration list also prints the name as Dr. Ethel Chua Joy Ong.",
        ),
        rec(
            "De La Salle University — Gokongwei College of Engineering",
            "Dean, Gokongwei College of Engineering",
            "Dean",
            "Dr. Kathleen B. Aviso",
            MISSING,
            MISSING,
            "https://www.dlsu.edu.ph/college-administration/",
            "Dean name verified. No GCOE office email or dedicated phone on that page.",
        ),
        rec(
            "De La Salle University — Office of Student Affairs",
            "Dean of Student Affairs",
            "Student affairs official",
            "Dr. Jaymee Abigail K. Pantaleon",
            "dsa@dlsu.edu.ph",
            MISSING,
            "https://www.dlsu.edu.ph/administration/",
            "Name from current university administration list (AY 2026-2027). Email from official OSA staff page https://old.dlsu.edu.ph/offices/osa/staff/. No dedicated OSA phone on those pages.",
        ),
        rec(
            "De La Salle University — Center for Social Concern and Action (COSCA)",
            "Director, Center for Social Concern and Action",
            "Organization that can help Be Scam Ready (community / social action)",
            "Ms. Anna Lyn M. Bandagosa",
            MISSING,
            MISSING,
            "https://www.dlsu.edu.ph/administration/",
            "University community-engagement office, not a student org. No email on the administration page.",
        ),
    ],
    [
        rec(
            "De La Salle University — tech / civic student organizations",
            "Student organizations",
            "Organization focusing on tech",
            MISSING,
            MISSING,
            MISSING,
            MISSING,
            "No official non-Facebook org directory with officer emails/phones was verified in this pass.",
        )
    ],
)

files["ust.json"] = campus(
    "University of Santo Tomas",
    "España / Sampaloc",
    "Manila",
    [
        rec(
            "University of Santo Tomas — College of Information and Computing Sciences",
            "Dean, College of Information and Computing Sciences",
            "Dean",
            "Asst. Prof. Christopher D. Ladao, MSCS",
            "cics@ust.edu.ph",
            "+63-2-3406-1611 local 8518",
            "https://www.ust.edu.ph/information-and-computing-sciences/",
            "College office email and administration-office number from the official CICS page.",
        ),
        rec(
            "University of Santo Tomas — Faculty of Engineering",
            "Dean, Faculty of Engineering",
            "Dean",
            "Prof. Angelo R. dela Cruz, PECE, PhD",
            "engineering.office@ust.edu.ph",
            "+63-2-3406-1611 local 8275",
            "https://www.ust.edu.ph/engineering/",
            "Page also lists +63-2-8731-4041.",
        ),
        rec(
            "University of Santo Tomas — Office for Student Affairs",
            "Student Formator listed first under The Student Formators",
            "Student affairs official",
            "Asst. Prof. Jaezamie V. Ong, MA",
            "osa@ust.edu.ph",
            "+63-2-3406-1611 local 8267 / 8294",
            "https://www.ust.edu.ph/administrative-offices/office-for-student-affairs/",
            "The current officers block does not print the word Director next to this name. A history list on the same page still says Asst. Prof. Maria Cecilia A. Tio Cuison, MEd, Director (2020-present). Email and phone are the OSA office contacts.",
        ),
        rec(
            "University of Santo Tomas — Office for Student Affairs",
            "Assistant Director for Student Welfare and Discipline",
            "Student affairs official",
            "Asst. Prof. Eleighn Vanessa Grace M. Castro, MIR",
            "osa@ust.edu.ph",
            "+63-2-3406-1611 local 8267 / 8294",
            "https://www.ust.edu.ph/administrative-offices/office-for-student-affairs/",
        ),
        rec(
            "University of Santo Tomas — College of Information and Computing Sciences",
            "Student Welfare and Development Coordinator (CICS)",
            "Student affairs official",
            "Asst. Prof. Krishnamonte M. Balmeo, MMEd",
            MISSING,
            MISSING,
            "https://www.ust.edu.ph/information-and-computing-sciences/",
            "Name and role listed on the CICS administrators page. No personal email or dedicated number for this role.",
        ),
    ],
    [
        rec(
            "University of Santo Tomas — Technovation Society",
            "Tech / innovation student organization (President)",
            "Organization focusing on tech",
            "Wilmargherix M. Castaneda",
            "technovation.ust@ust.edu.ph",
            MISSING,
            "https://www.usttechsoc.org/organization",
            "President and email from the organization's official website. No phone listed.",
        ),
        rec(
            "University of Santo Tomas — AWS Learning Club (AWS UST)",
            "Tech student organization (Chief Executive Officer on org site)",
            "Organization focusing on tech",
            "Josh Kenn Viray",
            MISSING,
            MISSING,
            "https://www.aws-ust.org/",
            "Name listed as Chief Executive Officer on the official org site. No email or phone on that page. Facebook page exists but was not scraped.",
        ),
        rec(
            "University of Santo Tomas — Society of Information Technology Enthusiasts (SITE)",
            "Tech student organization",
            "Organization focusing on tech",
            MISSING,
            MISSING,
            MISSING,
            "https://www.ust.edu.ph/information-and-computing-sciences/",
            "Named on the official CICS page. No officer, email, or phone for SITE on that page.",
        ),
        rec(
            "University of Santo Tomas — Computer Science Society",
            "Tech student organization",
            "Organization focusing on tech",
            MISSING,
            MISSING,
            MISSING,
            "https://www.ust.edu.ph/information-and-computing-sciences/",
            "Named on the official CICS page. No officer, email, or phone on that page.",
        ),
        rec(
            "University of Santo Tomas — Information Systems Society",
            "Tech student organization",
            "Organization focusing on tech",
            MISSING,
            MISSING,
            MISSING,
            "https://www.ust.edu.ph/information-and-computing-sciences/",
            "Named on the official CICS page. Public presence appears to be Facebook (facebook.com/UST.ISSociety); Facebook was not scraped.",
        ),
        rec(
            "University of Santo Tomas — CNAG-IICS / CNAG-CICS",
            "Tech student organization (Cisco)",
            "Organization focusing on tech",
            MISSING,
            MISSING,
            MISSING,
            "https://www.ust.edu.ph/information-and-computing-sciences/",
            "Named on the official CICS page. Public presence appears to be Facebook (facebook.com/cnagics); Facebook was not scraped.",
        ),
        rec(
            "University of Santo Tomas — Engineering Student Council",
            "College student council (Engineering)",
            "Organization focusing on tech",
            MISSING,
            MISSING,
            MISSING,
            "https://www.ust.edu.ph/engineering/",
            "Named on the official Faculty of Engineering page. No officer, email, or phone on that page.",
        ),
        rec(
            "University of Santo Tomas — Cisco Networking Academy Gateway (Engineering)",
            "Tech student organization (Cisco / Engineering)",
            "Organization focusing on tech",
            MISSING,
            MISSING,
            MISSING,
            "https://www.ust.edu.ph/engineering/",
            "Named on the official Faculty of Engineering student-organizations list. No officer, email, or phone on that page. Separate Facebook page facebook.com/USTCNAG was not scraped.",
        ),
        rec(
            "University of Santo Tomas — UST Red Cross Youth Council – Engineering Unit",
            "Socio-civic student organization",
            "Organization that can help Be Scam Ready (community / civic)",
            MISSING,
            MISSING,
            MISSING,
            "https://www.ust.edu.ph/engineering/",
            "Named on the official Faculty of Engineering page. No officer, email, or phone on that page.",
        ),
        rec(
            "University of Santo Tomas — SIMBAHAYAN Community Development Office",
            "University community development office",
            "Organization that can help Be Scam Ready (community / social issues)",
            "Asst. Prof. Froilan A. Alipao, MCD",
            "simbahayan@ust.edu.ph",
            "+63-2-3406-1611 local 8420 / 8368",
            "https://www.ust.edu.ph/community-development/",
            "First name under Administration and Staff on the official community-development page; the page does not print the word Director next to the name.",
        ),
    ],
)

files["up_manila.json"] = campus(
    "University of the Philippines Manila",
    "Ermita",
    "Manila",
    [
        rec(
            "University of the Philippines Manila — College of Arts and Sciences",
            "Dean, College of Arts and Sciences (computer science is under CAS; UP Manila has no College of Engineering)",
            "Dean",
            "Ma. Teresa G. De Guzman, PhD",
            "upm-cas-dean@up.edu.ph",
            "(632) 88141-282 & 283; 264",
            "https://www.upm.edu.ph/about-administration-officials-deans/",
            "Also listed: upm-cas@up.edu.ph. Confirmed on https://cas.upm.edu.ph/administration/.",
        ),
        rec(
            "University of the Philippines Manila — College of Arts and Sciences Office of Student Services",
            "Coordinator (OIC) for Office of Student Services",
            "Student affairs official",
            "Gaea Marelle J. Miranda, M.Sc., RPm",
            MISSING,
            MISSING,
            "https://cas.upm.edu.ph/administration/",
            "Role and name listed. No email or phone for this role on that page.",
        ),
    ],
    [
        rec(
            "University of the Philippines Manila — tech / civic student organizations",
            "Student organizations",
            "Organization focusing on tech",
            MISSING,
            MISSING,
            MISSING,
            MISSING,
            "No official non-Facebook org directory with officer emails/phones was verified in this pass.",
        )
    ],
)

files["pup_sta_mesa.json"] = campus(
    "Polytechnic University of the Philippines",
    "A. Mabini Campus, Sta. Mesa",
    "Manila",
    [
        rec(
            "Polytechnic University of the Philippines — College of Computer and Information Sciences",
            "Dean, College of Computer and Information Sciences",
            "Dean",
            "Melvin C. Roxas, MSGITS",
            "ccis@pup.edu.ph",
            "(+63 2) 5335-1787 or 5335-1777 local 272",
            "https://www.pup.edu.ph/ccis/personnel",
            "Dean name from CCIS officials page. Email and dean/chairpersons local from https://www.pup.edu.ph/ccis/contactinfo. Official university directory also lists 8716-4032 / 5335-1768 locals 3264 3272: https://www.pup.edu.ph/about/contactinformation",
        ),
        rec(
            "Polytechnic University of the Philippines — College of Engineering",
            "Dean, College of Engineering",
            "Dean",
            "Remedios G. Ado, DEM",
            MISSING,
            "8716-6273 / local 3236",
            "https://www.pup.edu.ph/about/contactinformation",
            "Name and numbers from the official PUP contact-information directory. No college email listed there.",
        ),
        rec(
            "Polytechnic University of the Philippines — Office of the Vice President for Student Affairs and Services",
            "Vice President for Student Affairs and Services",
            "Student affairs official",
            "Tomas O. Testor, MPA",
            MISSING,
            "(63 2) 5335-1787 or 5335-1777 local 6209 or 6210",
            "https://www.pup.edu.ph/about/contactinformation",
            "Name from official contact-information directory. Phone also on https://www.pup.edu.ph/studentservices/contactinfo. The officials page https://www.pup.edu.ph/studentservices/officials was under construction.",
        ),
    ],
    [
        rec(
            "Polytechnic University of the Philippines — CCIS student organizations",
            "Student organizations",
            "Organization focusing on tech",
            MISSING,
            MISSING,
            MISSING,
            MISSING,
            "CCIS official pages list personnel and office contacts but not named student-org officers or org emails.",
        )
    ],
)

files["mapua_intramuros.json"] = campus(
    "Mapúa University",
    "Intramuros",
    "Manila",
    [
        rec(
            "Mapúa University — School of Information Technology / computing and engineering deans",
            "Dean, computing / IT / engineering",
            "Dean",
            MISSING,
            MISSING,
            MISSING,
            "https://www.mapua.edu.ph/pages/school-of-information-technology",
            "SOIT program page loaded; it does not name a dean or give a dean email. The administration page did not load (HTTP 422). No dean contact was recorded.",
        ),
        rec(
            "Mapúa University — Office of Student Affairs",
            "Student affairs official",
            "Student affairs official",
            MISSING,
            MISSING,
            MISSING,
            "https://www.mapua.edu.ph/pages/school-of-information-technology",
            "No student-affairs officer name or email was verified on the live mapua.edu.ph pages in this pass. Campus trunk +63(2) 8247-5000 is the university number, not a dedicated OSA line, so it was not copied here.",
        ),
    ],
    [
        rec(
            "Mapúa University — tech student organizations",
            "Student organizations",
            "Organization focusing on tech",
            MISSING,
            MISSING,
            MISSING,
            MISSING,
            "No official non-Facebook org directory with officer emails/phones was verified in this pass.",
        )
    ],
)

files["feu_manila.json"] = campus(
    "Far Eastern University",
    "Nicanor Reyes Street, Sampaloc",
    "Manila",
    [
        rec(
            "Far Eastern University Manila — computing / IT / engineering dean",
            "Dean, computing / IT / engineering",
            "Dean",
            MISSING,
            MISSING,
            MISSING,
            "https://www.feu.edu.ph/",
            "FEU Manila official pages checked in this pass do not list a computing/IT/engineering dean. Computing and engineering programs in the FEU Group are under FEU Institute of Technology, a separate school, and were not mixed into this Manila campus file.",
        ),
        rec(
            "Far Eastern University — Office of Student Involvement",
            "Director, Office of Student Involvement",
            "Student affairs official",
            "Jhonalyn M. Concha",
            MISSING,
            "(02) 8849-4000 local 287",
            "https://www.feu.edu.ph/student-involvement/",
            "Also lists Samantha Mae L. Fabellon as Program Lead, FEU Manila. No OSI email on that page. Hub number +63 (2)-87777-338 is a general assist line, not copied as this office's private number.",
        ),
        rec(
            "Far Eastern University — Office of Student Discipline",
            "Office of Student Discipline",
            "Student affairs official",
            "Joseph Ryann J. Jalagat",
            "studentdiscipline@feu.edu.ph",
            "88494000 Loc. 288",
            "https://www.feu.edu.ph/student-discipline/",
            "Page lists Jalagat as Coordinator, Office of Student Discipline.",
        ),
    ],
    [
        rec(
            "Far Eastern University Manila — tech / civic student organizations",
            "Student organizations",
            "Organization focusing on tech",
            MISSING,
            MISSING,
            MISSING,
            "https://www.feu.edu.ph/student-involvement/",
            "OSI page describes student-org accreditation but does not name tech orgs or give org emails.",
        )
    ],
)

files["plm.json"] = campus(
    "Pamantasan ng Lungsod ng Maynila",
    "Intramuros",
    "Manila",
    [
        rec(
            "Pamantasan ng Lungsod ng Maynila — College of Engineering and Technology",
            "Dean, College of Engineering and Technology",
            "Dean",
            MISSING,
            MISSING,
            MISSING,
            "https://plm.edu.ph/",
            "No dean name, email, or dedicated phone was verified on accessible official pages in this pass. Parts of plm.edu.ph were blocked or required extra verification.",
        ),
        rec(
            "Pamantasan ng Lungsod ng Maynila — student affairs",
            "Student affairs official",
            "Student affairs official",
            MISSING,
            MISSING,
            MISSING,
            "https://plm.edu.ph/",
            "No student-affairs officer name or email was verified on accessible official pages in this pass.",
        ),
    ],
    [
        rec(
            "Pamantasan ng Lungsod ng Maynila — tech / civic student organizations",
            "Student organizations",
            "Organization focusing on tech",
            MISSING,
            MISSING,
            MISSING,
            MISSING,
            "No official non-Facebook org directory with officer emails/phones was verified in this pass.",
        )
    ],
)

files["adamson.json"] = campus(
    "Adamson University",
    "San Marcelino, Ermita",
    "Manila",
    [
        rec(
            "Adamson University — College of Computing and Information Technology",
            "Dean, College of Computing and Information Technology",
            "Dean",
            "Dr. Leonard L. Alejandro",
            MISSING,
            MISSING,
            "https://www.adamson.edu.ph/?page=administrators",
            "Name from official administrators page. Footer email is obfuscated and the visible webmaster address was not treated as this dean's email. University trunk 8524-20-11 was not copied as a dean number.",
        ),
        rec(
            "Adamson University — College of Engineering",
            "Dean, College of Engineering",
            "Dean",
            "Dr. Antonio P. Doroliat",
            MISSING,
            MISSING,
            "https://www.adamson.edu.ph/?page=administrators",
            "Name from official administrators page. No dean email or dedicated phone on that page.",
        ),
        rec(
            "Adamson University — Office of the Vice President for Student Affairs",
            "Vice-President for Student Affairs",
            "Student affairs official",
            "Fr. Aldrin R. Suan, CM",
            MISSING,
            MISSING,
            "https://www.adamson.edu.ph/?page=administrators",
        ),
        rec(
            "Adamson University — Office for Student Life",
            "Director, Office for Student Life",
            "Student affairs official",
            "Atty. Jan Nelin M. Navallasca",
            MISSING,
            MISSING,
            "https://www.adamson.edu.ph/?page=administrators",
        ),
        rec(
            "Adamson University — Integrated Community Extension Services",
            "Director, Integrated Community Extension Services",
            "Organization that can help Be Scam Ready (community extension)",
            "Fr. Rowen Z. Carlos, CM",
            MISSING,
            MISSING,
            "https://www.adamson.edu.ph/?page=administrators",
        ),
    ],
    [
        rec(
            "Adamson University — tech / civic student organizations",
            "Student organizations",
            "Organization focusing on tech",
            MISSING,
            MISSING,
            MISSING,
            MISSING,
            "Administrators page does not list student-org officers. No official non-Facebook org directory with emails/phones was verified in this pass.",
        )
    ],
)


if __name__ == "__main__":
    for name, payload in files.items():
        dump(name, payload)
