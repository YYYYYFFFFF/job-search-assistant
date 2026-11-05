import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
import zipfile
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import career
import demo


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.parent = Path(self.temp.name)
        self.root = self.parent / ".career"
        demo.populate(self.root)
        self.pdf = self.parent / "resume.pdf"
        demo.fictional_pdf(self.pdf)
        self.release = career.register_resume(self.root, "Data Analytics", "1.0", self.pdf, True)
        self.source = career.read(career.ROOT / "examples/job.json")
        self.letter = career.ROOT / "examples/letter.json"

    def tearDown(self):
        self.temp.cleanup()

    def add(self, source=None):
        return career.add_job(self.root, source or self.source)["id"]

    def prepared(self):
        job_id = self.add()
        career.prepare(self.root, job_id, "Data Analytics", self.letter)
        return job_id

    def submitted(self):
        job_id = self.prepared()
        career.submit(self.root, job_id, "2030-04-15", True, "SIMULATED user confirmation")
        return job_id

    def test_fresh_setup_does_not_invent_personal_defaults(self):
        other = self.parent / "blank"
        career.init(other)
        profile = career.read(other / "profile.json")
        self.assertEqual(profile["name"], "")
        self.assertEqual(profile["work_rights"]["details"], "")
        self.assertFalse(career.doctor(other)["ready"])
        self.assertTrue(career.doctor(self.root)["ready"])
        with self.assertRaises(ValueError):
            career.init(self.root)
        self.assertEqual(career.read(self.root / "profile.json")["name"], "Alex Example")

    def test_cli_supports_private_path_with_spaces(self):
        path = self.parent / "another private workspace"
        result = subprocess.run([sys.executable, str(career.ROOT / "scripts/career.py"), "--workspace", str(path), "init"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["workspace"], str(path.resolve()))

    def test_tracking_urls_retain_meaningful_query_ids(self):
        one = career.canonical("https://jobs.example.test/view?jobId=1&utm_source=x#part")
        two = career.canonical("https://jobs.example.test/view?utm_source=y&jobId=1")
        self.assertEqual(one, two)
        self.assertNotEqual(one, career.canonical("https://jobs.example.test/view?jobId=2"))
        with self.assertRaises(ValueError):
            career.canonical("https://user:password@jobs.example.test/1")

    def test_employer_requisition_merges_cross_posts(self):
        first = self.add()
        other = copy.deepcopy(self.source)
        other["url"] = "https://other.example.test/ad/999"
        result = career.add_job(self.root, other)
        self.assertEqual(result["id"], first)
        self.assertTrue(result["duplicate"])
        self.assertEqual(len(career.jobs(self.root)), 1)

    def test_possible_cross_post_requires_resolution_but_distinct_reqs_survive(self):
        self.add()
        other = copy.deepcopy(self.source)
        other.pop("requisition_id")
        other["url"] = "https://other.example.test/ad/999"
        with self.assertRaisesRegex(ValueError, "Possible cross-post"):
            career.add_job(self.root, other)
        other["requisition_id"] = "DEMO-102"
        self.add(other)
        self.assertEqual(len(career.jobs(self.root)), 2)

    def test_unknown_eligibility_and_failed_conditions_hold_recommendation(self):
        for key, value in [("eligibility", None), ("open", False), ("location", None), ("in_window", False)]:
            other = copy.deepcopy(self.source)
            other["requisition_id"] = key
            other["url"] += "&check=" + key
            other["screening"][key] = value
            with self.assertRaisesRegex(ValueError, "held"):
                career.recommend(self.root, self.add(other))

    def test_source_cannot_inject_submitted_state_or_string_boolean(self):
        other = copy.deepcopy(self.source)
        other["state"] = "submitted"
        with self.assertRaisesRegex(ValueError, "Unknown job fields"):
            self.add(other)
        other.pop("state")
        other["screening"]["eligibility"] = "true"
        with self.assertRaises(ValueError):
            self.add(other)

    def test_exclusion_and_repeated_delivery(self):
        job_id = self.add()
        config = career.read(self.root / "config.json")
        config["search"]["excluded_terms"] = ["query results"]
        career.write(self.root / "config.json", config)
        with self.assertRaisesRegex(ValueError, "exclusion"):
            career.recommend(self.root, job_id)
        config["search"]["excluded_terms"] = []
        career.write(self.root / "config.json", config)
        result = career.recommend(self.root, job_id)
        self.assertIn(self.source["jd"]["requirements"][1], result["recommendation"])
        self.assertTrue(career.recommend(self.root, job_id)["already_delivered"])

    def test_email_receipt_is_required_and_not_sent_by_helper(self):
        config = career.read(self.root / "config.json")
        config["integrations"]["delivery"] = "email"
        career.write(self.root / "config.json", config)
        job_id = self.add()
        with self.assertRaisesRegex(ValueError, "connected mail tool"):
            career.recommend(self.root, job_id)
        self.assertEqual(career.recommend(self.root, job_id, "fictional-sent-message")["delivery"]["receipt"], "fictional-sent-message")

    def test_word_material_and_original_resume_bytes(self):
        job_id = self.prepared()
        folder = self.root / "applications" / job_id
        self.assertEqual(career.sha(folder / "resume.pdf"), self.release["sha256"])
        with zipfile.ZipFile(folder / "cover-letter.docx") as archive:
            for name in archive.namelist():
                if name.endswith((".xml", ".rels")):
                    ET.fromstring(archive.read(name))
            text = "".join(ET.fromstring(archive.read("word/document.xml")).itertext())
        for paragraph in career.read(self.letter)["paragraphs"]:
            self.assertIn(paragraph, text)
        self.assertEqual(career.sha(self.pdf), self.release["sha256"])

    def test_submit_requires_confirmation_and_detects_changed_attachment(self):
        job_id = self.prepared()
        with self.assertRaisesRegex(ValueError, "confirmation"):
            career.submit(self.root, job_id, "2030-04-15", False, "No confirmation")
        (self.root / "applications" / job_id / "resume.pdf").write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "changed"):
            career.submit(self.root, job_id, "2030-04-15", True, "SIMULATED confirmation")
        self.assertEqual(career.read(career.job_path(self.root, job_id))["state"], "prepared")

    def test_full_lifecycle_archives_readable_bytes_and_is_idempotent(self):
        job_id = self.submitted()
        result = career.archive_job(self.root, job_id)
        self.assertFalse((self.root / "applications" / job_id).exists())
        for file in result["archive"]["files"]:
            self.assertEqual(career.sha(self.root / file["path"]), file["sha256"])
        self.assertTrue(career.archive_job(self.root, job_id)["already_archived"])
        self.assertTrue(career.submit(self.root, job_id, "2030-04-15", True, "SIMULATED confirmation")["already_recorded"])
        self.assertTrue((self.root / self.release["path"]).exists())

    def test_archive_copy_failure_retains_originals_and_resumes(self):
        job_id = self.submitted()
        with mock.patch.object(career.shutil, "copyfile", side_effect=OSError("simulated disk full")):
            with self.assertRaises(OSError):
                career.archive_job(self.root, job_id)
        self.assertTrue((self.root / "applications" / job_id / "resume.pdf").exists())
        career.archive_job(self.root, job_id)
        self.assertFalse((self.root / "applications" / job_id).exists())

    def test_preparation_failure_resumes_without_overwriting_existing_letter(self):
        job_id = self.add()
        with mock.patch.object(career.shutil, "copyfile", side_effect=OSError("simulated disk full")):
            with self.assertRaises(OSError):
                career.prepare(self.root, job_id, "Data Analytics", self.letter)
        letter = self.root / "applications" / job_id / "cover-letter.docx"
        digest = career.sha(letter)
        career.prepare(self.root, job_id, "Data Analytics", self.letter)
        self.assertEqual(career.sha(letter), digest)
        self.assertTrue(career.prepare(self.root, job_id, "Data Analytics", self.letter)["already_prepared"])

    def test_unicode_resume_category(self):
        result = career.register_resume(self.root, "数据分析", "1.0", self.pdf, True)
        self.assertEqual(result["category"], "数据分析")

    def test_corrupt_archive_retains_originals(self):
        job_id = self.submitted()
        target = self.root / "archive" / job_id
        target.mkdir()
        (target / "cover-letter.docx").write_bytes(b"corrupt")
        with self.assertRaisesRegex(ValueError, "Archive verification failed"):
            career.archive_job(self.root, job_id)
        self.assertTrue((self.root / "applications" / job_id / "resume.pdf").exists())

    @unittest.skipIf(os.name == "nt", "Windows symlink creation may require developer mode")
    def test_cleanup_rejects_symlink_and_preserves_unrelated_data(self):
        job_id = self.submitted()
        outside = self.parent / "unrelated"
        outside.mkdir()
        (outside / "keep.txt").write_text("keep")
        (self.root / "applications" / job_id / "surprise").symlink_to(outside, target_is_directory=True)
        with self.assertRaises(ValueError):
            career.archive_job(self.root, job_id)
        self.assertEqual((outside / "keep.txt").read_text(), "keep")
        with self.assertRaises(ValueError):
            career.inside(self.root, "../unrelated")

    def test_resume_release_keeps_history_and_prepared_snapshot(self):
        job_id = self.prepared()
        next_file = self.parent / "revision.pdf"
        demo.fictional_pdf(next_file)
        with next_file.open("ab") as stream:
            stream.write(b"\n% fictional revision\n")
        revision = career.register_resume(self.root, "Data Analytics", "1.1", next_file, True)
        self.assertNotEqual(revision["sha256"], self.release["sha256"])
        item = career.read(career.job_path(self.root, job_id))
        self.assertEqual(item["resume"]["version"], "1.0")
        self.assertEqual(career.sha(self.root / self.release["path"]), self.release["sha256"])
        with self.assertRaises(ValueError):
            career.register_resume(self.root, "Data Analytics", "1.1", next_file, True)
        with self.assertRaises(ValueError):
            career.register_resume(self.root, "Data Analytics", "1.2", next_file, False)

    def test_demand_counts_sql_once_across_fields_and_cross_posts(self):
        self.add()
        self.add()
        counts = career.keyword_demand(self.root, "Data Analytics")
        self.assertEqual(counts["vacancies"], 1)
        self.assertEqual(next(r["vacancies"] for r in counts["counts"] if r["term"] == "sql"), 1)
        self.assertFalse(any(r["term"] == "tools_to_learn" for r in counts["counts"]))

    def test_question_approval_and_update_same_prompt(self):
        with self.assertRaises(ValueError):
            career.save_idea(self.root, "Question", "Projects", "Idea", False)
        career.save_idea(self.root, "Question", "Projects", "Approved idea", True)
        career.save_idea(self.root, " QUESTION ", "Projects", "Approved revision", True)
        self.assertEqual(len(career.read(self.root / "questions.json")), 1)
        self.assertEqual(career.read(self.root / "questions.json")[0]["idea"], "Approved revision")

    def test_another_profession_and_market_have_no_fixed_design_or_australia_rule(self):
        source = copy.deepcopy(self.source)
        source.update({"employer": "Example Infrastructure", "title": "Cloud Engineer", "location": "Toronto, Canada",
                       "category": "Cloud Infrastructure", "requisition_id": "CAN-88", "url": "https://infra.example.test/88"})
        job_id = self.add(source)
        result = career.recommend(self.root, job_id)
        self.assertIn("Toronto, Canada", result["recommendation"])
        self.assertEqual(career.read(career.job_path(self.root, job_id))["source"]["category"], "Cloud Infrastructure")

    def test_self_submission_preserves_unknown_version(self):
        job_id = self.add()
        career.submit(self.root, job_id, "2030-04-15", True, "SIMULATED self-submission, version unknown", unknown_resume=True)
        self.assertIsNone(career.read(career.job_path(self.root, job_id))["resume"])
        career.archive_job(self.root, job_id)

    def test_abandonment_and_progress_keep_other_jobs_and_masters(self):
        job_id = self.prepared()
        career.save_progress(self.root, job_id, {"step": "waiting for answer", "pending_questions": ["Availability?"]})
        self.assertIn("pending_questions", career.read(career.job_path(self.root, job_id))["progress"])
        with self.assertRaises(ValueError):
            career.abandon(self.root, job_id, False)
        career.abandon(self.root, job_id, True)
        self.assertEqual(career.read(career.job_path(self.root, job_id))["state"], "abandoned")
        self.assertTrue((self.root / self.release["path"]).exists())


if __name__ == "__main__":
    unittest.main()
