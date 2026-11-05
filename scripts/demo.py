#!/usr/bin/env python3
"""Run a fictional, network-free workflow and remove temporary data."""
import json
from pathlib import Path
import tempfile
import career


def fictional_pdf(path):
    text = b"BT /F1 14 Tf 60 760 Td (Alex Example - Fictional demo resume) Tj 0 -24 Td (Course project: SQL query validation and spreadsheet checks.) Tj ET"
    objects = [b"<< /Type /Catalog /Pages 2 0 R >>",
               b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
               b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
               b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
               b"<< /Length " + str(len(text)).encode() + b" >>\nstream\n" + text + b"\nendstream"]
    data = b"%PDF-1.4\n"
    offsets = [0]
    for i, obj in enumerate(objects, 1):
        offsets.append(len(data))
        data += str(i).encode() + b" 0 obj\n" + obj + b"\nendobj\n"
    xref = len(data)
    data += b"xref\n0 6\n0000000000 65535 f \n"
    data += b"".join(("%010d 00000 n \n" % offset).encode() for offset in offsets[1:])
    data += b"trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n" + str(xref).encode() + b"\n%%EOF\n"
    Path(path).write_bytes(data)


def populate(root):
    career.init(root)
    config = career.read(root / "config.json")
    config["timezone"] = "Pacific/Auckland"
    config["search"].update({"directions": ["Data Analytics"], "locations": ["Wellington, New Zealand"],
                             "job_types": ["Part-time"], "keywords": ["data analyst", "SQL"],
                             "platforms": ["https://careers.example.test"]})
    career.write(root / "config.json", config)
    profile = career.read(root / "profile.json")
    profile.update({"name": "Alex Example", "contact": {"email": "alex@example.test", "location": "Wellington"},
                    "tools": [{"name": "SQL", "scope": "Course-project queries", "source": "Fictional course project"}],
                    "projects": [{"name": "Course query project", "contribution": "SQL queries, spreadsheet validation and a course presentation", "source": "Fictional fixture"}]})
    career.write(root / "profile.json", profile)


def run():
    with tempfile.TemporaryDirectory(prefix="career-demo-") as temp:
        parent = Path(temp)
        root = parent / ".career"
        populate(root)
        pdf = parent / "fictional-resume.pdf"
        fictional_pdf(pdf)
        release = career.register_resume(root, "Data Analytics", "1.0", pdf, True)
        job = career.add_job(root, career.read(career.ROOT / "examples/job.json"))
        duplicate = career.add_job(root, career.read(career.ROOT / "examples/job.json"))
        assert duplicate["id"] == job["id"] and duplicate["duplicate"]
        career.recommend(root, job["id"])
        career.prepare(root, job["id"], "Data Analytics", career.ROOT / "examples/letter.json")
        career.submit(root, job["id"], "2030-04-15", True, "SIMULATION: fictional user confirmation, no employer contacted")
        archive = career.archive_job(root, job["id"])
        demand = career.keyword_demand(root, "Data Analytics")
        assert next(row for row in demand["counts"] if row["term"] == "sql")["vacancies"] == 1
        career.save_idea(root, "Describe a project", "Projects", "Approved fictional SQL validation example", True)
        assert career.sha(root / release["path"]) == release["sha256"]
        assert not (root / "applications" / job["id"]).exists()
        result = {"fictional": True, "network_requests": 0, "duplicate_merged": True,
                  "final_state": career.read(career.job_path(root, job["id"]))["state"],
                  "archived_files_verified": len(archive["archive"]["files"]), "resume_preserved": True,
                  "sql_demand_distinct_vacancies": 1, "temporary_data_removed_on_exit": True}
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    run()
