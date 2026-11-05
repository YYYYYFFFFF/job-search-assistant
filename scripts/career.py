#!/usr/bin/env python3
"""Job Search Assistant's local storage and material helpers. Python 3.9+, stdlib only."""
import argparse
import collections
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
import zipfile
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
STATES = {"discovered", "recommended", "prepared", "submitted", "abandoned"}
TRACKING = {"source", "ref", "refid", "trackingid", "fbclid", "gclid", "ebp", "origin", "origintolandingjobpostings"}


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=".write-", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def slug(value):
    result = re.sub(r"[^\w]+", "-", value.casefold()).strip("-_")
    if not result:
        raise ValueError("Use a nonempty category/identifier with letters or digits.")
    return result


def canonical(url):
    p = urlsplit(url)
    if p.scheme not in {"http", "https"} or not p.hostname or p.username or p.password:
        raise ValueError("Job URL must be an HTTP(S) URL without credentials.")
    query = [(k, v) for k, v in parse_qsl(p.query, keep_blank_values=True)
             if not k.lower().startswith("utm_") and k.lower() not in TRACKING]
    return urlunsplit((p.scheme.lower(), p.netloc.lower(), p.path.rstrip("/") or "/", urlencode(sorted(query)), ""))


def normalize(value):
    return " ".join(value.casefold().split())


def identity(job):
    requisition = job.get("requisition_id")
    key = ("req:" + normalize(job["employer"]) + ":" + str(requisition).strip()) if requisition else canonical(job["url"])
    return hashlib.sha256(key.encode()).hexdigest()[:16]


def inside(root, relative):
    root = Path(root).resolve()
    relative = Path(relative)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError("Expected a workspace-relative path.")
    target = root / relative
    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError("Workspace-owned paths cannot contain symlinks.")
    if target.resolve() != root and root not in target.resolve().parents:
        raise ValueError("Path escapes the workspace.")
    return target


def workspace(path):
    raw = Path(path).expanduser()
    if raw.is_symlink():
        raise ValueError("Workspace root cannot be a symlink.")
    root = raw.resolve()
    if not (root / "config.json").is_file():
        raise ValueError("Initialize a private workspace first: init")
    return root


def job_path(root, job_id):
    if not re.fullmatch(r"[a-f0-9]{16}", job_id):
        raise ValueError("Invalid job ID.")
    return inside(root, "jobs/" + job_id + ".json")


def jobs(root):
    folder = inside(root, "jobs")
    return [read(inside(root, str(p.relative_to(Path(root).resolve())))) for p in sorted(folder.glob("*.json"))]


def validate_job(job):
    for key in ("employer", "title", "location", "url", "checked_at", "category"):
        if not isinstance(job.get(key), str) or not job[key].strip():
            raise ValueError("Job requires a nonempty " + key)
    canonical(job["url"])
    dt.datetime.fromisoformat(job["checked_at"].replace("Z", "+00:00"))
    jd = job.get("jd", {})
    if not isinstance(jd, dict) or not all(isinstance(jd.get(k), list) for k in ("responsibilities", "requirements")):
        raise ValueError("JD requires responsibilities and requirements arrays.")
    if not jd["responsibilities"] or not jd["requirements"]:
        raise ValueError("Keep incomplete JDs in chat until source capture is available.")
    if any(not isinstance(v, str) or not v.strip() for k in ("responsibilities", "requirements") for v in jd[k]):
        raise ValueError("JD bullets must be nonempty strings; retain nesting through indentation.")
    for key in ("keywords", "capabilities", "tools", "tools_to_learn"):
        values = job.get(key, [])
        if not isinstance(values, list) or any(not isinstance(v, str) or not v.strip() for v in values):
            raise ValueError(key + " must be a list of nonempty strings.")
    screening = job.get("screening", {})
    if not isinstance(screening, dict):
        raise ValueError("screening must be an object.")
    for key in ("open", "in_window", "location", "eligibility"):
        if screening.get(key) is not None and type(screening[key]) is not bool:
            raise ValueError("Screening checks accept true, false or null.")
    if screening.get("match") not in {"high", "partial", "exclude", "hold", None}:
        raise ValueError("Unknown direction-match label.")


JOB_FIELDS = {"employer", "title", "location", "url", "checked_at", "category", "requisition_id", "published_at",
              "deadline", "duration", "compensation", "contact", "job_type", "jd", "screening", "keywords", "capabilities", "tools", "tools_to_learn", "evidence"}


def source_fields(incoming):
    validate_job(incoming)
    extra = set(incoming) - JOB_FIELDS
    if extra:
        raise ValueError("Unknown job fields: " + ", ".join(sorted(extra)))


def init(path):
    raw = Path(path).expanduser()
    if raw.is_symlink():
        raise ValueError("Workspace root cannot be a symlink.")
    root = raw.resolve()
    if root.exists() and any(root.iterdir()):
        raise ValueError("Destination is not empty; existing data was preserved.")
    root.mkdir(parents=True, exist_ok=True)
    for name in ("config.json", "profile.json", "resumes.json", "questions.json", "CURRENT.md"):
        shutil.copyfile(ROOT / "templates" / name, root / name)
    for name in ("jobs", "resumes", "applications", "archive"):
        (root / name).mkdir()
    (root / ".gitignore").write_text("*\n", encoding="utf-8")
    return {"workspace": str(root), "next": "Fill config.json and profile.json, then run doctor."}


def doctor(root):
    config, profile = read(inside(root, "config.json")), read(inside(root, "profile.json"))
    issues = []
    if not profile.get("name"):
        issues.append("profile.name is empty")
    for key in ("directions", "locations", "platforms"):
        if not config.get("search", {}).get(key):
            issues.append("config.search." + key + " is empty")
    from zoneinfo import ZoneInfo
    try:
        ZoneInfo(config.get("timezone", "UTC"))
    except Exception:
        issues.append("timezone is unavailable; install tzdata or choose an available zone")
    for item in read(inside(root, "resumes.json"))["releases"]:
        file = inside(root, item["path"])
        if not file.is_file() or sha(file) != item["sha256"]:
            issues.append("Resume missing or changed: " + item["path"])
    return {"ready": not issues, "issues": issues, "integrations": config["integrations"],
            "browser": "Connect explicitly when needed; doctor does not inspect accounts or tabs."}


def add_job(root, incoming):
    source_fields(incoming)
    # Input describes source facts only; lifecycle state is owned by this program.
    key = identity(incoming)
    url = canonical(incoming["url"])
    for existing in jobs(root):
        if existing["id"] == key or url in existing["aliases"]:
            return {"id": existing["id"], "duplicate": True, "state": existing["state"]}
        same = all(normalize(existing["source"][k]) == normalize(incoming[k]) for k in ("employer", "title", "location"))
        different_reqs = (existing["source"].get("requisition_id") and incoming.get("requisition_id")
                          and existing["source"]["requisition_id"] != incoming["requisition_id"])
        if same and not different_reqs:
            raise ValueError("Possible cross-post of " + existing["id"] + "; verify the employer requisition and use the same ID.")
    value = {"id": key, "state": "discovered", "source": incoming, "aliases": [url], "delivery": None,
             "materials": [], "resume": None, "submission": None, "archive": None}
    write(job_path(root, key), value)
    return {"id": key, "duplicate": False, "state": "discovered"}


def update_job(root, job_id, incoming):
    source_fields(incoming)
    path = job_path(root, job_id)
    old = read(path)
    if old["state"] in {"submitted", "abandoned"}:
        raise ValueError("Completed source snapshots are preserved.")
    if identity(incoming) != identity(old["source"]):
        raise ValueError("Identity changed; resolve the vacancy explicitly instead of overwriting it.")
    old["source"] = incoming
    write(path, old)
    return {"id": job_id, "updated": True}


def recommend(root, job_id, receipt=None):
    path = job_path(root, job_id)
    item = read(path)
    source = item["source"]
    checks = source.get("screening", {})
    if any(checks.get(k) is not True for k in ("open", "in_window", "location", "eligibility")) or checks.get("match") not in {"high", "partial"}:
        raise ValueError("Recommendation held: resolve source, date, location, eligibility and direction checks.")
    if item["state"] not in {"discovered", "recommended"}:
        raise ValueError("Job has already entered an application or was abandoned.")
    config = read(inside(root, "config.json"))
    excluded = config["search"].get("excluded_terms", [])
    haystack = normalize(" ".join([source["title"], source["employer"]] + source["jd"]["responsibilities"] + source["jd"]["requirements"]))
    if any(normalize(term) in haystack for term in excluded if term.strip()):
        raise ValueError("A configured exclusion matches the JD; resolve it before recommending.")
    channel = config["integrations"]["delivery"]
    if channel not in {"chat", "email"}:
        raise ValueError("Delivery must be chat or email.")
    if channel == "email" and not receipt:
        raise ValueError("Send through the connected mail tool first, then pass its exact message ID as --receipt.")
    if item["delivery"]:
        return {"id": job_id, "already_delivered": True, "delivery": item["delivery"]}
    text = "# " + source["title"] + " — " + source["employer"] + "\n\n"
    text += "## Role and Info\n"
    for label, key in [("Role title", "title"), ("Company", "employer"), ("Location", "location"), ("JD link", "url"), ("Application deadline", "deadline"), ("Duration", "duration"), ("Compensation", "compensation"), ("Contact", "contact")]:
        text += "- " + label + ": " + str(source.get(key) or "Unknown") + "\n"
    text += "\n## Keywords\n"
    for key in ("keywords", "capabilities", "tools"):
        text += "- " + key + ": " + (", ".join(source.get(key, [])) or "None identified") + "\n"
    text += "\n## JD capture\n"
    for key in ("responsibilities", "requirements"):
        text += "\n### " + key.title() + "\n" + "\n".join("- " + bullet for bullet in source["jd"][key]) + "\n"
    text += "\n## Application Files\nNo application materials at discovery.\n"
    item["state"] = "recommended"
    item["delivery"] = {"channel": channel, "receipt": receipt or "conversation", "at": dt.datetime.now(dt.timezone.utc).isoformat()}
    write(path, item)
    return {"id": job_id, "delivery": item["delivery"], "recommendation": text}


def register_resume(root, category, version, file, approval):
    if not approval:
        raise ValueError("An approved resume release requires --approved-by-user.")
    file = Path(file)
    if file.suffix.lower() != ".pdf" or not file.read_bytes().startswith(b"%PDF-"):
        raise ValueError("Register an actual PDF. Review its content and layout before releasing it.")
    registry = read(inside(root, "resumes.json"))
    category_id, version_id = slug(category), slug(version)
    if any(r["category"].casefold() == category.casefold() and r["version"] == version for r in registry["releases"]):
        raise ValueError("This category/version already exists; use a new version.")
    relative = "resumes/" + category_id + "/" + version_id + ".pdf"
    target = inside(root, relative)
    if target.exists():
        raise ValueError("Release path already exists.")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(file, target)
    release = {"category": category, "version": version, "path": relative, "sha256": sha(target)}
    registry["releases"].append(release)
    registry["active"][category] = version
    write(inside(root, "resumes.json"), registry)
    return release


def current_resume(root, category):
    registry = read(inside(root, "resumes.json"))
    version = registry["active"].get(category)
    release = next((r for r in registry["releases"] if r["category"] == category and r["version"] == version), None)
    if not release:
        raise ValueError("No active resume for this category; ask which existing resume to use.")
    path = inside(root, release["path"])
    if sha(path) != release["sha256"]:
        raise ValueError("Resume checksum changed; verify the release before use.")
    return release


def make_docx(path, content):
    # Independently authored layout; no downloaded or candidate-specific template.
    paragraphs = content.get("paragraphs", [])
    if not paragraphs or any(not isinstance(p, str) or not p.strip() for p in paragraphs):
        raise ValueError("Letter input requires nonempty paragraphs.")
    if sum(len(p.split()) for p in paragraphs) > 450:
        raise ValueError("Keep the letter under 450 words, then check its rendered page count.")
    body = "".join('<w:p><w:pPr><w:spacing w:after="140"/></w:pPr><w:r><w:t xml:space="preserve">' + escape(p) + '</w:t></w:r></w:p>' for p in paragraphs)
    document = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>' + body + '<w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1134" w:right="1134" w:bottom="1134" w:left="1134"/></w:sectPr></w:body></w:document>'
    types = '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/><Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/></Types>'
    rels = '<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>'
    styles = '<?xml version="1.0"?><w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/><w:sz w:val="22"/></w:rPr></w:rPrDefault></w:docDefaults></w:styles>'
    document_rels = '<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>'
    with zipfile.ZipFile(path, "x", zipfile.ZIP_DEFLATED) as archive:
        for name, value in {"[Content_Types].xml": types, "_rels/.rels": rels, "word/document.xml": document, "word/styles.xml": styles, "word/_rels/document.xml.rels": document_rels}.items():
            archive.writestr(name, value)


def prepare(root, job_id, category, letter_file):
    path = job_path(root, job_id)
    item = read(path)
    if item["state"] == "prepared":
        for material in item["materials"]:
            if sha(inside(root, material["path"])) != material["sha256"]:
                raise ValueError("Prepared file changed; inspect the existing material.")
        return {"id": job_id, "already_prepared": True, "materials": item["materials"]}
    if item["state"] not in {"discovered", "recommended"}:
        raise ValueError("Application has already been submitted or abandoned.")
    if any(item["source"].get("screening", {}).get(k) is not True for k in ("open", "eligibility")):
        raise ValueError("Resolve vacancy availability and eligibility before preparing.")
    release = item["resume"] or current_resume(root, category)
    if release["category"] != category or sha(inside(root, release["path"])) != release["sha256"]:
        raise ValueError("Interrupted preparation's resume release requires review.")
    folder = inside(root, "applications/" + job_id)
    content = read(letter_file)
    if folder.exists() and any(p.name not in {"cover-letter.docx", "resume.pdf"} or p.is_symlink() or not p.is_file() for p in folder.iterdir()):
        raise ValueError("Unexpected preparation files; inspect the existing folder.")
    item["resume"] = release
    write(path, item)
    folder.mkdir(exist_ok=True)
    try:
        letter = folder / "cover-letter.docx"
        if letter.exists():
            with zipfile.ZipFile(letter) as document:
                xml = ET.fromstring(document.read("word/document.xml"))
                paragraphs = ["".join(p.itertext()) for p in xml.findall(".//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p")]
                if paragraphs != content.get("paragraphs"):
                    raise ValueError("Existing letter differs; preserve and review it.")
        else:
            make_docx(letter, content)
        resume = folder / "resume.pdf"
        if not resume.exists():
            shutil.copyfile(inside(root, release["path"]), resume)
        if sha(resume) != release["sha256"]:
            raise ValueError("Existing resume differs; preserve and review it.")
    except Exception:
        # Preserve any partially written material for review/recovery.
        raise
    item["materials"] = [{"path": str(p.relative_to(Path(root).resolve())), "sha256": sha(p)} for p in sorted(folder.iterdir())]
    item["resume"] = release
    item["state"] = "prepared"
    write(path, item)
    return {"id": job_id, "state": "prepared", "materials": item["materials"], "next": "Review rendered letter, actual attachments and all form answers; user submits."}


def submit(root, job_id, date, confirmed, note, resume_category=None, unknown_resume=False):
    if not confirmed:
        raise ValueError("Wait for explicit user confirmation; use --confirmed-by-user only after it arrives.")
    dt.date.fromisoformat(date)
    if not note.strip():
        raise ValueError("Record the user's confirmation/source, not an inferred submission.")
    path = job_path(root, job_id)
    item = read(path)
    if item["state"] == "submitted":
        return {"id": job_id, "already_recorded": True}
    if item["state"] == "abandoned":
        raise ValueError("An abandoned application requires a new explicit user decision.")
    if item["state"] != "prepared":
        if not resume_category and not unknown_resume:
            raise ValueError("For a self-submitted job, specify --resume CATEGORY or --unknown-resume.")
        item["resume"] = current_resume(root, resume_category) if resume_category else None
    for material in item["materials"]:
        if sha(inside(root, material["path"])) != material["sha256"]:
            raise ValueError("Prepared material changed; identify the actual submitted file first.")
    item["state"] = "submitted"
    item["submission"] = {"date": date, "confirmation": note, "result": "pending"}
    write(path, item)
    return {"id": job_id, "state": "submitted"}


def archive_job(root, job_id):
    path = job_path(root, job_id)
    item = read(path)
    if item["state"] != "submitted":
        raise ValueError("Archive submitted jobs only; interrupted preparation stays available.")
    folder = inside(root, "applications/" + job_id)
    target = inside(root, "archive/" + job_id)
    expected = {Path(m["path"]).name: m["sha256"] for m in item["materials"]}
    if item["archive"] and not folder.exists():
        for file in item["archive"]["files"]:
            if sha(inside(root, file["path"])) != file["sha256"]:
                raise ValueError("Archived material changed; inspect the saved archive.")
        return {"id": job_id, "already_archived": True, "archive": item["archive"]}
    if folder.exists():
        files = list(folder.iterdir())
        if any(not p.is_file() or p.is_symlink() for p in files) or {p.name for p in files} != set(expected):
            raise ValueError("Unexpected material folder contents; local originals were preserved.")
        for p in files:
            if sha(p) != expected[p.name]:
                raise ValueError("Original material changed; local originals were preserved.")
    elif expected:
        raise ValueError("Material originals are missing.")
    target.mkdir(parents=True, exist_ok=True)
    for name, digest in expected.items():
        dest = inside(root, "archive/" + job_id + "/" + name)
        if not dest.exists():
            shutil.copyfile(folder / name, dest)
        if sha(dest) != digest:
            raise ValueError("Archive verification failed; local originals were preserved.")
    archived = [{"path": "archive/" + job_id + "/" + name, "sha256": digest} for name, digest in sorted(expected.items())]
    item["archive"] = {"files": archived, "verified_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    write(path, item)
    if folder.exists():
        shutil.rmtree(folder)
    item["materials"] = archived
    write(path, item)
    return {"id": job_id, "archive": item["archive"], "temporary_materials_removed": True}


def keyword_demand(root, category):
    counts = collections.Counter()
    considered = 0
    untagged = 0
    for item in jobs(root):
        source = item["source"]
        if source["category"] != category or item["state"] == "abandoned":
            continue
        considered += 1
        terms = {normalize(term) for field in ("keywords", "capabilities", "tools") for term in source.get(field, [])}
        if not terms:
            untagged += 1
        counts.update(terms)
    return {"category": category, "vacancies": considered, "untagged": untagged,
            "counts": [{"term": term, "vacancies": count} for term, count in sorted(counts.items(), key=lambda pair: (-pair[1], pair[0]))]}


def save_idea(root, question, category, idea, approved):
    if not approved:
        raise ValueError("Save only a user-approved answer direction.")
    if not all(s.strip() for s in (question, category, idea)):
        raise ValueError("Question, category and idea must be nonempty.")
    path = inside(root, "questions.json")
    rows = read(path)
    row = {"question": question, "category": category, "idea": idea}
    existing = next((i for i, old in enumerate(rows) if normalize(old["question"]) == normalize(question)), None)
    if existing is None:
        rows.append(row)
    else:
        rows[existing] = row
    write(path, rows)
    return row


def save_progress(root, job_id, value):
    allowed = {"step", "pending_questions", "form_url", "session_id", "draft_id", "notion_page_id", "interviews", "answers", "next_action"}
    if not isinstance(value, dict) or set(value) - allowed:
        raise ValueError("Use the progress fields listed in docs/data.md.")
    path = job_path(root, job_id)
    item = read(path)
    item.setdefault("progress", {}).update(value)
    write(path, item)
    return {"id": job_id, "progress": item["progress"]}


def attach(root, job_id, file):
    path = job_path(root, job_id)
    item = read(path)
    if item["state"] != "prepared":
        raise ValueError("Add additional materials to a prepared application.")
    source = Path(file)
    target = inside(root, "applications/" + job_id + "/" + source.name)
    if target.exists():
        raise ValueError("Material already exists; preserve or explicitly review the existing file.")
    shutil.copyfile(source, target)
    item["materials"].append({"path": str(target.relative_to(Path(root).resolve())), "sha256": sha(target)})
    write(path, item)
    return {"id": job_id, "material": item["materials"][-1]}


def abandon(root, job_id, confirmed):
    if not confirmed:
        raise ValueError("Abandonment requires an explicit user decision.")
    path = job_path(root, job_id)
    item = read(path)
    if item["state"] == "submitted":
        raise ValueError("Preserve submitted history; record a withdrawal event instead.")
    folder = inside(root, "applications/" + job_id)
    if folder.exists():
        expected = {Path(m["path"]).name: m["sha256"] for m in item["materials"]}
        files = list(folder.iterdir())
        if any(p.is_symlink() or not p.is_file() for p in files) or {p.name for p in files} != set(expected):
            raise ValueError("Unexpected material folder contents; originals were preserved.")
        if any(sha(p) != expected[p.name] for p in files):
            raise ValueError("Material changed; originals were preserved.")
        shutil.rmtree(folder)
    item["state"] = "abandoned"
    item["materials"] = []
    write(path, item)
    return {"id": job_id, "state": "abandoned", "external_cleanup": "Separate exact-object operation when explicitly requested."}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", default=os.environ.get("CAREER_WORKSPACE", ".career"))
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("init")
    sub.add_parser("doctor")
    sub.add_parser("list")
    for command in ("add-job",):
        sub.add_parser(command).add_argument("input")
    update = sub.add_parser("update-job")
    update.add_argument("id")
    update.add_argument("input")
    show = sub.add_parser("show")
    show.add_argument("id")
    recommend_parser = sub.add_parser("recommend")
    recommend_parser.add_argument("id")
    recommend_parser.add_argument("--receipt")
    resume = sub.add_parser("register-resume")
    resume.add_argument("category")
    resume.add_argument("version")
    resume.add_argument("file")
    resume.add_argument("--approved-by-user", action="store_true")
    prep = sub.add_parser("prepare")
    prep.add_argument("id")
    prep.add_argument("--resume", required=True)
    prep.add_argument("--letter", required=True)
    submission = sub.add_parser("submit")
    submission.add_argument("id")
    submission.add_argument("--date", required=True)
    submission.add_argument("--note", required=True)
    submission.add_argument("--confirmed-by-user", action="store_true")
    group = submission.add_mutually_exclusive_group()
    group.add_argument("--resume")
    group.add_argument("--unknown-resume", action="store_true")
    sub.add_parser("archive").add_argument("id")
    stop = sub.add_parser("abandon")
    stop.add_argument("id")
    stop.add_argument("--confirmed-by-user", action="store_true")
    progress = sub.add_parser("progress")
    progress.add_argument("id")
    progress.add_argument("input")
    attachment = sub.add_parser("attach")
    attachment.add_argument("id")
    attachment.add_argument("file")
    sub.add_parser("keyword-demand").add_argument("category")
    idea = sub.add_parser("save-idea")
    idea.add_argument("--question", required=True)
    idea.add_argument("--category", required=True)
    idea.add_argument("--idea", required=True)
    idea.add_argument("--approved-by-user", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.command == "init":
            result = init(args.workspace)
        else:
            root = workspace(args.workspace)
            command = args.command
            if command == "doctor":
                result = doctor(root)
            elif command == "list":
                result = [{"id": j["id"], "state": j["state"], "employer": j["source"]["employer"], "title": j["source"]["title"]} for j in jobs(root)]
            elif command == "show":
                result = read(job_path(root, args.id))
            elif command == "add-job":
                result = add_job(root, read(args.input))
            elif command == "update-job":
                result = update_job(root, args.id, read(args.input))
            elif command == "recommend":
                result = recommend(root, args.id, args.receipt)
            elif command == "register-resume":
                result = register_resume(root, args.category, args.version, args.file, args.approved_by_user)
            elif command == "prepare":
                result = prepare(root, args.id, args.resume, args.letter)
            elif command == "submit":
                result = submit(root, args.id, args.date, args.confirmed_by_user, args.note, args.resume, args.unknown_resume)
            elif command == "archive":
                result = archive_job(root, args.id)
            elif command == "abandon":
                result = abandon(root, args.id, args.confirmed_by_user)
            elif command == "progress":
                result = save_progress(root, args.id, read(args.input))
            elif command == "attach":
                result = attach(root, args.id, args.file)
            elif command == "keyword-demand":
                result = keyword_demand(root, args.category)
            else:
                result = save_idea(root, args.question, args.category, args.idea, args.approved_by_user)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1 if args.command == "doctor" and not result["ready"] else 0
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(json.dumps({"error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
