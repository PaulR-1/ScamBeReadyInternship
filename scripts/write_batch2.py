"""Write Batch 2 campus JSON files from verified official-page facts only."""
from __future__ import annotations

import json
from pathlib import Path

MISSING = "Did not find any info"
ROOT = Path(__file__).resolve().parents[1] / "data"
POLICY = (
    "Only information published on official public pages is recorded. "
    "No invented, guessed, or reused contacts. Facebook was not scraped. "
    f"Missing fields use '{MISSING}'."
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


def campus(university, campus_name, city, officials, orgs):
    return {
        "university": university,
        "campus": campus_name,
        "city": city,
        "batch": "2_schools_11_to_22",
        "policy": POLICY,
        "officials": officials,
        "student_organizations": orgs,
    }


def dump(filename, payload):
    path = ROOT / filename
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(path)


NO_AWS_GOOGLE = (
    "No AWS Learning Club / AWS Student Builder Group or Google Developer Groups on Campus "
    "(GDG/GDSC) listing with officer email or phone was found on this school's official public pages. "
    "Social-only mentions were not used."
)

files = {}

files["dls_csb_manila.json"] = campus(
    "De La Salle-College of Saint Benilde",
    "Taft Avenue / Malate",
    "Manila",
    [
        rec(
            "De La Salle-College of Saint Benilde — School of Management and Information Technology",
            "Dean, School of Management and Information Technology",
            "Dean",
            "Joana M. Diñoso, DBA",
            "management@benilde.edu.ph",
            "+63 2 8230 5100 local 1701 / 1703",
            "https://www.benilde.edu.ph/about-benilde/who-we-are/",
            "Dean name from official administrators list. School email and locals from https://www.benilde.edu.ph/directory/.",
        ),
        rec(
            "De La Salle-College of Saint Benilde — Student Life",
            "Dean, Student Life",
            "Student affairs official",
            "Levi V. Albania",
            "student.life@benilde.edu.ph",
            "+63 2 8230 5100 local 1501 / 1502",
            "https://www.benilde.edu.ph/about-benilde/who-we-are/",
            "Dean of Student Life from administrators list. Center for Student Life email and locals from the official directory.",
        ),
        rec(
            "De La Salle-College of Saint Benilde — Center for Partnership Advancement",
            "Partnership office",
            "Partnership contact",
            MISSING,
            "partnership@benilde.edu.ph",
            "+63 2 8230 5100 local 3843",
            "https://www.benilde.edu.ph/directory/",
        ),
        rec(
            "De La Salle-College of Saint Benilde — Center for Academic Linkages",
            "Academic linkages / partnership office",
            "Partnership contact",
            MISSING,
            "oc.academiclinkages@benilde.edu.ph",
            "+63 2 8230 5100 local 1136",
            "https://www.benilde.edu.ph/directory/",
        ),
        rec(
            "De La Salle-College of Saint Benilde — Center for Social Action",
            "Community / social action office",
            "Organization that can help Be Scam Ready (community)",
            MISSING,
            "social.action@benilde.edu.ph",
            "+63 2 8230 5100 local 7077 / 7078",
            "https://www.benilde.edu.ph/directory/",
        ),
    ],
    [
        rec(
            "De La Salle-College of Saint Benilde — AWS / Google student organizations",
            "AWS Learning Club or GDG/GDSC on campus",
            "Organization focusing on tech",
            MISSING,
            MISSING,
            MISSING,
            MISSING,
            NO_AWS_GOOGLE,
        )
    ],
)

files["ue_manila.json"] = campus(
    "University of the East",
    "C.M. Recto, Sampaloc",
    "Manila",
    [
        rec(
            "University of the East Manila — College of Computer Studies and Systems",
            "Dean, College of Computer Studies and Systems",
            "Dean",
            "Prof. Ma. Teresa F. Borebor",
            "ccss@ue.edu.ph",
            "(632) 8735-5471 locals 382 and 383 / direct (632) 8735-6975",
            "https://www.ue.edu.ph/mla/ccss-contact-details/",
            "Also listed on https://www.ue.edu.ph/mla/administration/.",
        ),
        rec(
            "University of the East Manila — College of Engineering",
            "Dean, College of Engineering – Manila",
            "Dean",
            "Rogelio B. Aniez Jr",
            "jasmin.salazar@ue.edu.ph",
            "(632) 8735-5471 local 397 / direct 8735-1354",
            "https://www.ue.edu.ph/mla/administration/",
            "Dean name from administration page. College inquiry email from https://www.ue.edu.ph/mla/email-directory/. Phone from https://www.ue.edu.ph/mla/telephone-directory/ (College of Engineering / ITE).",
        ),
        rec(
            "University of the East Manila — Student Affairs Office",
            "Director, Student Affairs Office – Manila",
            "Student affairs official",
            "Edilina B. Baldoza",
            "sao@ue.edu.ph",
            "(632) 8735-5471 local 353 / direct 5338-1444",
            "https://www.ue.edu.ph/mla/administration/",
            "Name from administration page. Email from official email directory. Phone from official telephone directory.",
        ),
        rec(
            "University of the East — Office for International Affairs and External Linkages",
            "Director, Office for International Affairs and External Linkages",
            "Partnership contact",
            "Darwin M. Guianan",
            MISSING,
            MISSING,
            "https://www.ue.edu.ph/mla/administration/",
            "Named on the administration page. No OIA email on the public email directory.",
        ),
        rec(
            "University of the East Manila — Office of Extension and Community Outreach",
            "Director, Office of Extension and Community Outreach",
            "Organization that can help Be Scam Ready (community)",
            "Rogelio I. Espiritu",
            "uenstp.manila@ue.edu.ph",
            "(632) 8735-5471 local 379",
            "https://www.ue.edu.ph/mla/administration/",
            "Director named on the administration page. Email from https://www.ue.edu.ph/mla/email-directory/. Local from https://www.ue.edu.ph/mla/telephone-directory/ (OECO or NSTP).",
        ),
    ],
    [
        rec(
            "University of the East Manila — AWS / Google student organizations",
            "AWS Learning Club or GDG/GDSC on campus",
            "Organization focusing on tech",
            MISSING,
            MISSING,
            MISSING,
            MISSING,
            NO_AWS_GOOGLE,
        )
    ],
)

files["ue_caloocan.json"] = campus(
    "University of the East",
    "Samson Road",
    "Caloocan",
    [
        rec(
            "University of the East Caloocan — College of Engineering",
            "Dean, College of Engineering-Caloocan",
            "Dean",
            "Angelita D. Guia",
            "ceng.cal@ue.edu.ph",
            "(632) 8-367-4572 local 166 / direct (632) 8-365-4121",
            "https://www.ue.edu.ph/cal/college-of-engineering-2/",
            "Also listed on https://www.ue.edu.ph/mla/administration/. Computer Science and IT sit under this college at Caloocan (CS/IT Department local 200 on the same page).",
        ),
        rec(
            "University of the East Caloocan — College of Engineering",
            "Associate Dean-Computer Studies and Systems",
            "Dean",
            "Dr. Maria Amelia E. Damian",
            "ceng.cal@ue.edu.ph",
            "(632) 8-367-4572 local 167",
            "https://www.ue.edu.ph/cal/college-of-engineering-2/",
            "Associate Dean for Computer Studies and Systems. College office email is the only public engineering email listed.",
        ),
        rec(
            "University of the East Caloocan — Student Affairs Office",
            "Director, Student Affairs Office – Caloocan",
            "Student affairs official",
            "Clemente A. Diwas",
            "sao.cal@ue.edu.ph",
            "Trunkline 8-367-45-72 loc 176 / direct 8-364-2499",
            "https://www.ue.edu.ph/mla/administration/",
            "Name from administration page. Email from https://www.ue.edu.ph/cal/email-directory/. Phone from https://www.ue.edu.ph/cal/student-affairs-office/.",
        ),
        rec(
            "University of the East Caloocan — Office of Extension and Community Outreach",
            "Community outreach / NSTP",
            "Organization that can help Be Scam Ready (community)",
            MISSING,
            "uenstp.caloocan@ue.edu.ph",
            MISSING,
            "https://www.ue.edu.ph/cal/email-directory/",
        ),
    ],
    [
        rec(
            "University of the East Caloocan — AWS / Google student organizations",
            "AWS Learning Club or GDG/GDSC on campus",
            "Organization focusing on tech",
            MISSING,
            MISSING,
            MISSING,
            MISSING,
            NO_AWS_GOOGLE,
        )
    ],
)

files["tip_manila.json"] = campus(
    "Technological Institute of the Philippines",
    "Quiapo (P. Casal / Arlegui)",
    "Manila",
    [
        rec(
            "Technological Institute of the Philippines Manila — computing / engineering dean",
            "Dean, College of Computer Studies / Engineering",
            "Dean",
            MISSING,
            MISSING,
            MISSING,
            "https://dru.tip.edu.ph/best-of-tip/ched/",
            "Official T.I.P. pages confirm ITE and engineering programs at Manila but do not name a current dean or give a dean/partnership email. General campus email info@tip.edu.ph is a catch-all, not a dean or partnership inbox, so it was not copied as those roles.",
        ),
        rec(
            "Technological Institute of the Philippines Manila — student affairs",
            "Student affairs official",
            "Student affairs official",
            MISSING,
            MISSING,
            MISSING,
            "https://dru.tip.edu.ph/best-of-tip/ched/",
            "No named Student Affairs officer or OSA email was found on official T.I.P. pages in this pass. Campus phone (+632) 8733-9117 is the school trunk, not a dedicated OSA line.",
        ),
    ],
    [
        rec(
            "Technological Institute of the Philippines Manila — AWS / Google student organizations",
            "AWS Learning Club or GDG/GDSC on campus",
            "Organization focusing on tech",
            MISSING,
            MISSING,
            MISSING,
            MISSING,
            NO_AWS_GOOGLE,
        )
    ],
)

files["tip_quezon_city.json"] = campus(
    "Technological Institute of the Philippines",
    "Aurora Boulevard, Cubao",
    "Quezon City",
    [
        rec(
            "Technological Institute of the Philippines Quezon City — computing / engineering dean",
            "Dean, College of Computer Studies / Engineering",
            "Dean",
            MISSING,
            MISSING,
            MISSING,
            "https://dru.tip.edu.ph/best-of-tip/ched/",
            "Official T.I.P. pages confirm ITE and engineering programs at QC but do not name a current dean or give a dean/partnership email.",
        ),
        rec(
            "Technological Institute of the Philippines Quezon City — student affairs",
            "Student affairs official",
            "Student affairs official",
            MISSING,
            MISSING,
            MISSING,
            "https://dru.tip.edu.ph/best-of-tip/ched/",
            "No named Student Affairs officer or OSA email was found on official T.I.P. pages in this pass.",
        ),
    ],
    [
        rec(
            "Technological Institute of the Philippines Quezon City — AWS / Google student organizations",
            "AWS Learning Club or GDG/GDSC on campus",
            "Organization focusing on tech",
            MISSING,
            MISSING,
            MISSING,
            MISSING,
            NO_AWS_GOOGLE,
        )
    ],
)

files["nu_manila.json"] = campus(
    "National University",
    "Sampaloc",
    "Manila",
    [
        rec(
            "National University Manila — College of Computing and Information Technologies",
            "Dean, College of Computing and Information Technologies",
            "Dean",
            MISSING,
            MISSING,
            MISSING,
            "https://www.national-u.edu.ph/contact-us/",
            "Dean names on NU pages conflict across years (Nov 2024 news named Emeliza R. Yabut as OIC Dean; a Dec 2023 news item named Avonn C. Nova; an MIT program page still prints aotrillanes@national-u.edu.ph as Dean). No current dean was recorded. The contact-us page is Cloudflare-blocked in this pass, so college locals were not copied. The MIT program page local 1456 belongs to graduate-program inquiries and was not reused as a dean number.",
        ),
        rec(
            "National University Manila — Student Development and Activities Office",
            "Director, Student Development and Activities Office",
            "Student affairs official",
            "Marc Rey D. Galido",
            MISSING,
            MISSING,
            "https://www.national-u.edu.ph/nu-manila/student-organizations/",
            "Name listed on the official Student Organizations page. No SDAO email was published there. Live fetch of NU pages hit Cloudflare during this pass.",
        ),
    ],
    [
        rec(
            "National University Manila — College of Computing and Information Technologies Student Council",
            "College student council (tech)",
            "Organization focusing on tech",
            "Mapanao, Jessy Cassandra M.",
            MISSING,
            MISSING,
            "https://national-u.edu.ph/nu-manila/student-organizations/nucsg-college-student-council-2024-2025/",
            "President named on the official 2024-2025 student council page. That page is labeled 2024-2025; the current term was not reconfirmed. No email or phone on that listing.",
        ),
        rec(
            "National University Manila — GDG on Campus",
            "Google Developer Groups on Campus (official Google community page)",
            "Organization focusing on tech",
            "Gwyenth Lim (Campus Organizer); Franze Young (President)",
            MISSING,
            MISSING,
            "https://gdg.community.dev/gdg-on-campus-national-university-manila-campus-manila-philippines/",
            "Official GDG on Campus chapter page. No organizer email or phone is published there. AWS Learning Club was not found on official NU pages.",
        ),
    ],
)

files["san_beda_manila.json"] = campus(
    "San Beda University",
    "Mendiola",
    "Manila",
    [
        rec(
            "San Beda University — College of Arts and Sciences",
            "Dean, College of Arts and Sciences (computing programs sit in CAS)",
            "Dean",
            "Prof. Christian Bryan S. Bustamante, Ph.D.",
            "cas_sec@sanbeda.edu.ph",
            "(+632) 8726-2332 local 4022",
            "https://www.sanbeda.edu.ph/manila/academic-programs/college-of-arts-and-sciences",
            "CAS page lists him as Dean and publishes the secretary email and Dean's Office local. BS Computer Science / IT / IS are under CAS. The administrators page also lists Dr. Moses Aaron T. Angeles under College of Arts and Sciences without a title that could be confirmed in this pass.",
        ),
        rec(
            "San Beda University — Student Affairs",
            "Dean, Student Affairs",
            "Student affairs official",
            "Dominador B. Manlincon, LPT",
            MISSING,
            MISSING,
            "https://www.sanbeda.edu.ph/manila/about-us/administrators",
            "Named on the official administrators page. No student-affairs email on that page. University trunk 8-726-2332 was not copied as this office's number.",
        ),
        rec(
            "San Beda University — Community Engagement Center",
            "Director, Community Engagement Center",
            "Organization that can help Be Scam Ready (community)",
            "Norielyn C. Tabag, RSW",
            MISSING,
            MISSING,
            "https://www.sanbeda.edu.ph/manila/about-us/administrators",
        ),
    ],
    [
        rec(
            "San Beda University — AWS / Google student organizations",
            "AWS Learning Club or GDG/GDSC on campus",
            "Organization focusing on tech",
            MISSING,
            MISSING,
            MISSING,
            MISSING,
            NO_AWS_GOOGLE,
        )
    ],
)

files["pnu.json"] = campus(
    "Philippine Normal University",
    "Taft Avenue, Ermita",
    "Manila",
    [
        rec(
            "Philippine Normal University — Faculty of Education and Information Sciences",
            "Faculty of Education and Information Sciences (closest computing / IT unit)",
            "Dean",
            MISSING,
            "feis@pnu.edu.ph",
            "(+63 2) 5317-1768 local 725",
            "https://www.pnu.edu.ph/directory/",
            "Official directory lists the faculty email and local but not a named dean. PNU is a teacher-education university; there is no College of Engineering on that directory.",
        ),
        rec(
            "Philippine Normal University — Student Affairs and Services Office",
            "Student Affairs and Services Office",
            "Student affairs official",
            MISSING,
            "saso@pnu.edu.ph",
            "(+63 2) 5317-1768 local 713",
            "https://www.pnu.edu.ph/directory/",
            "Office email and local from the official directory. No officer name on that table.",
        ),
        rec(
            "Philippine Normal University — Linkages and International Office",
            "Linkages and International Office",
            "Partnership contact",
            MISSING,
            "lio@pnu.edu.ph",
            "(+63 2) 5317-1768 local 755",
            "https://www.pnu.edu.ph/directory/",
        ),
        rec(
            "Philippine Normal University — Community Partnership and Extension Office",
            "Community Partnership and Extension Office",
            "Organization that can help Be Scam Ready (community)",
            MISSING,
            "cpeo@pnu.edu.ph",
            "(+63 2) 5317-1768 local 727",
            "https://www.pnu.edu.ph/directory/",
        ),
    ],
    [
        rec(
            "Philippine Normal University — University Student Council",
            "University Student Council",
            "Student organization",
            MISSING,
            "uscpnu.pnumanila@pnu.edu.ph",
            "(+63 2) 5317-1768 local 783",
            "https://www.pnu.edu.ph/directory/",
        ),
        rec(
            "Philippine Normal University — AWS / Google student organizations",
            "AWS Learning Club or GDG/GDSC on campus",
            "Organization focusing on tech",
            MISSING,
            MISSING,
            MISSING,
            MISSING,
            NO_AWS_GOOGLE,
        ),
    ],
)

files["ceu_mendiola.json"] = campus(
    "Centro Escolar University",
    "Mendiola",
    "Manila",
    [
        rec(
            "Centro Escolar University Manila — computing / IT / engineering dean",
            "Dean, computing / IT / engineering",
            "Dean",
            MISSING,
            MISSING,
            MISSING,
            "https://www.ceu.edu.ph/contacts/administrative-offices",
            "Official administrative-offices page could not be read (Cloudflare block). No computing/engineering dean was recorded.",
        ),
        rec(
            "Centro Escolar University Manila — student affairs",
            "Vice President for Student Affairs",
            "Student affairs official",
            "Dr. Carlito B. Olaer",
            MISSING,
            "(+63)2 8735-68-61 to 71 loc.209",
            "https://www.ceu.edu.ph/contacts/administrative-offices",
            "Name, title, and local appear on the official administrative-offices listing. The page email was Cloudflare-obfuscated and was not reconstructed. Direct fetch of the page was blocked during this pass.",
        ),
    ],
    [
        rec(
            "Centro Escolar University Manila — AWS / Google student organizations",
            "AWS Learning Club or GDG/GDSC on campus",
            "Organization focusing on tech",
            MISSING,
            MISSING,
            MISSING,
            MISSING,
            NO_AWS_GOOGLE,
        )
    ],
)

files["lpu_intramuros.json"] = campus(
    "Lyceum of the Philippines University",
    "Intramuros",
    "Manila",
    [
        rec(
            "Lyceum of the Philippines University Manila — College of Technology",
            "Dean, College of Technology",
            "Dean",
            "Dr. Arlene R. Caballero",
            "technology@lpu.edu.ph",
            "(632) 8527-8251 local 158",
            "https://manila.lpu.edu.ph/about-lpu/university-officials/",
            "Dean from official university officials page. College email and local from https://manila.lpu.edu.ph/contact-info/. Direct fetch hit Cloudflare; content is from those official LPU Manila pages.",
        ),
        rec(
            "Lyceum of the Philippines University Manila — Student Affairs Office",
            "Dean, Student Affairs",
            "Student affairs official",
            "Ms. Gladys O. Ramos",
            "studentaffairs@lpu.edu.ph",
            "(632) 8527-8251 local 137",
            "https://manila.lpu.edu.ph/about-lpu/university-officials/",
            "Name from university officials page. Email and local from official contact-info page. Direct line 8527-2707 is also listed there for SAO.",
        ),
        rec(
            "Lyceum of the Philippines University Manila — Global Relations and Partnerships",
            "Global Relations and Partnerships",
            "Partnership contact",
            MISSING,
            "globalrelations@lpu.edu.ph",
            "(632) 8527-8251 local 144",
            "https://manila.lpu.edu.ph/contact-info/",
        ),
        rec(
            "Lyceum of the Philippines University Manila — Industry Partnership for Academic Affairs",
            "Director, Industry Partnership for Academic Affairs",
            "Partnership contact",
            "Ms. Regina Isabel D. Laurel",
            MISSING,
            MISSING,
            "https://manila.lpu.edu.ph/about-lpu/university-officials/",
            "Named on the official university officials page. No separate partnership email beside globalrelations@lpu.edu.ph.",
        ),
        rec(
            "Lyceum of the Philippines University Manila — Community Outreach and Service Learning",
            "Manager, Community Outreach and Service Learning",
            "Organization that can help Be Scam Ready (community)",
            "Mr. Edison G. Atanacio",
            MISSING,
            MISSING,
            "https://manila.lpu.edu.ph/about-lpu/university-officials/",
        ),
    ],
    [
        rec(
            "Lyceum of the Philippines University Manila — AWS / Google student organizations",
            "AWS Learning Club or GDG/GDSC on campus",
            "Organization focusing on tech",
            MISSING,
            MISSING,
            MISSING,
            MISSING,
            NO_AWS_GOOGLE,
        )
    ],
)

files["tup_ermita.json"] = campus(
    "Technological University of the Philippines",
    "Ermita / Ayala",
    "Manila",
    [
        rec(
            "Technological University of the Philippines — Computer Studies",
            "Head, Computer Studies",
            "Dean",
            "Asst. Prof. Dolores L. Montesines",
            "computer@tup.edu.ph",
            MISSING,
            "https://tup.edu.ph/pages/about/tup-officials",
            "Name and office email from the official TUP officials listing (also on https://www.tup.edu.ph/pages/administration/vpaa). Personal email dolores_montesines@tup.edu.ph is printed on the same official table. Direct fetch of tup.edu.ph returned HTTP 502 during this pass.",
        ),
        rec(
            "Technological University of the Philippines — Office of Student Affairs",
            "Dean, Office of Student Affairs",
            "Student affairs official",
            "Assoc. Prof. Dr. Margaret S. Aquino",
            "osa@tup.edu.ph",
            MISSING,
            "https://tup.edu.ph/pages/about/tup-officials",
            "Name and office email from the official TUP officials listing. Personal email margaret_aquino@tup.edu.ph is on the same table.",
        ),
    ],
    [
        rec(
            "Technological University of the Philippines — Computer Students' Association (COMPASS)",
            "Tech student organization",
            "Organization focusing on tech",
            "Sophia Ashley San Juan",
            MISSING,
            MISSING,
            "https://www.tup.edu.ph/pages/students/student-organizations",
            "President listed on the official student-organizations page. Advisers listed there include Prof. Peragrino B. Amador, Jr. and Prof. Dolores Montesines. No org email or phone.",
        ),
        rec(
            "Technological University of the Philippines — TUP Tech Guild",
            "Tech student organization",
            "Organization focusing on tech",
            "Jesse Ann P. Tolentino",
            MISSING,
            MISSING,
            "https://www.tup.edu.ph/pages/students/student-organizations",
            "President listed on the official student-organizations page. Advisers listed: Prof. Jay Fel C. Quijano and Prof. Dolores L. Montesines. No org email or phone.",
        ),
        rec(
            "Technological University of the Philippines — GDG on Campus",
            "Google Developer Groups on Campus (official Google community page)",
            "Organization focusing on tech",
            "Jefferson Padua (Organizer); Kien Serapio (Co-Lead)",
            MISSING,
            MISSING,
            "https://gdg.community.dev/gdg-on-campus-technological-university-of-the-philippines-manila-philippines/",
            "Official GDG on Campus chapter page. No organizer email or phone is published there. AWS Learning Club was not found on official TUP pages.",
        ),
    ],
)

files["miriam_college.json"] = campus(
    "Miriam College",
    "Katipunan, Loyola Heights",
    "Quezon City",
    [
        rec(
            "Miriam College — computing / IT / engineering dean",
            "Dean, computing / IT / engineering",
            "Dean",
            MISSING,
            MISSING,
            MISSING,
            "https://mc.edu.ph/contact-us/directory/",
            "No computing/IT/engineering dean was verified on official Miriam College pages in this pass.",
        ),
        rec(
            "Miriam College — Global Relations and Partnerships / OIPRM",
            "Partnership / linkages office",
            "Partnership contact",
            MISSING,
            MISSING,
            MISSING,
            "https://mc.edu.ph/about-mc/affiliation-linkages/",
            "The official linkages page describes the Office of Institutional Partnerships and Resource Mobilization. The homepage also names a Global Relations and Partnerships Office. The public directory does not publish a dedicated partnership email; assist@mc.edu.ph is a general inbox and was not copied as a partnership address.",
        ),
        rec(
            "Miriam College — Office of Student Affairs (Higher Education Unit)",
            "Office of Student Affairs",
            "Student affairs official",
            MISSING,
            "heustudentaffairs@mc.edu.ph",
            "8930-6272 local 2045, 2046",
            "https://mc.edu.ph/contact-us/directory/",
            "Email and locals from the official directory. Direct fetch timed out; listing is from that official directory page. The directory notes OSA on Facebook; Facebook was not scraped.",
        ),
    ],
    [
        rec(
            "Miriam College — AWS / Google student organizations",
            "AWS Learning Club or GDG/GDSC on campus",
            "Organization focusing on tech",
            MISSING,
            MISSING,
            MISSING,
            MISSING,
            NO_AWS_GOOGLE,
        )
    ],
)

files["umak.json"] = campus(
    "University of Makati",
    "West Rembo",
    "Taguig",
    [
        rec(
            "University of Makati — computing / IT / engineering dean",
            "Dean, computing / IT / engineering",
            "Dean",
            MISSING,
            MISSING,
            MISSING,
            "https://www.umak.edu.ph/",
            "No dean name, partnership email, or dedicated computing-college contact was verified on accessible official UMak pages in this pass.",
        ),
        rec(
            "University of Makati — student affairs",
            "Student affairs official",
            "Student affairs official",
            MISSING,
            MISSING,
            MISSING,
            "https://www.umak.edu.ph/",
            "No student-affairs officer name or email was verified on accessible official UMak pages in this pass.",
        ),
    ],
    [
        rec(
            "University of Makati — AWS / Google student organizations",
            "AWS Learning Club or GDG/GDSC on campus",
            "Organization focusing on tech",
            MISSING,
            MISSING,
            MISSING,
            MISSING,
            NO_AWS_GOOGLE,
        )
    ],
)

files["rtu_mandaluyong.json"] = campus(
    "Rizal Technological University",
    "Boni Avenue (main campus)",
    "Mandaluyong",
    [
        rec(
            "Rizal Technological University — Institute of Computer Studies",
            "Director, Institute of Computer Studies",
            "Dean",
            "Dr. Lea S. Nisperos",
            MISSING,
            MISSING,
            "https://www.rtu.edu.ph/administration/",
            "Named on the official administration page. No ICS email or dedicated phone on that page.",
        ),
        rec(
            "Rizal Technological University — College of Engineering",
            "Dean, College of Engineering",
            "Dean",
            "Dr. Wilfredo Timajo",
            MISSING,
            MISSING,
            "https://www.rtu.edu.ph/administration/",
        ),
        rec(
            "Rizal Technological University — Student Affairs Office",
            "Director, Student Affairs Office",
            "Student affairs official",
            "Instr. Mariel A. Dela Trinidad",
            MISSING,
            MISSING,
            "https://www.rtu.edu.ph/administration/",
            "Current administration page lists her as SAO Director. Older news still used other OSAAS titles; this file follows the live administration page.",
        ),
        rec(
            "Rizal Technological University — International Affairs and Linkages Office",
            "Director, International Affairs and Linkages Office",
            "Partnership contact",
            "Assoc. Prof. Donato Z. Estocada",
            "ialo@rtu.edu.ph",
            "(02) 8534-8267 loc. 1609",
            "https://www.rtu.edu.ph/administration/",
            "Director from administration page. Partnership/events emails and phone from https://www.rtu.edu.ph/internationalization/ (also intlaffairs.support@rtu.edu.ph).",
        ),
    ],
    [
        rec(
            "Rizal Technological University — AWS / Google student organizations",
            "AWS Learning Club or GDG/GDSC on campus",
            "Organization focusing on tech",
            MISSING,
            MISSING,
            MISSING,
            MISSING,
            NO_AWS_GOOGLE,
        )
    ],
)


if __name__ == "__main__":
    for name, payload in files.items():
        dump(name, payload)
