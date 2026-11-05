---
name: job-application
description: Prepare selected job materials and form answers, hand off manual submission, record confirmed submissions and archive verified materials.
---

# Job Application

## Reuse the selected job

Use the retained job ID and [local job record](../../docs/data.md#job-record). If needed, fetch the exact configured recommendation message or directly supplied source page. Complete missing JD fields through [Job Search preparation](../job-search/SKILL.md#prepare-job-information). Refresh open status and decisive eligibility before preparing; preserve completed capture and tags.

## Prepare materials

Select an existing category master from private `resumes.json`; retain its category, version and checksum. Ask which existing resume to use if no suitable release exists. Create a new category or tailored resume only on an explicit request.

Use relevant facts and documented examples from private `profile.json` and exact project evidence listed in the [workspace map](../../docs/data.md#workspace-map). Draft a letter using the independent [letter template](../../templates/letter.json). Replace all guidance with role-specific supported content. Verify contact links and official employer details. Include work rights, availability and notice when requested and confirmed.

Generate a Word copy with [prepare](../../docs/commands.md#application-materials), or use an existing user-supplied template. Check wording and render the actual document in an available document viewer; deliver a readable one-page letter. Keep files in the selected job's `applications/<id>/` directory and record any additional required material by exact path/checksum. Preserve current resume masters.

## Fill the application

Follow the JD's stated route and requirements. For external forms, use the selected authorized browser session, fill supported fields and upload the actual intended files. For platform-native applications, provide files/answers and use supported controls. For email applications explicitly requested by the JD, prepare the recipient, subject, body and attachments as an unsent draft. Read back the actual attachments and draft/form state. Edit an existing draft in place.

Use matching approved ideas from private `questions.json` for uncertain questions. Adapt to the actual prompt and length limit using source facts. Ask the user about unknown facts or personal choices in one concise group; continue independent work. Keep approved wording with this application. Standalone answer ideas are saved only through [Question Bank](../question-bank/SKILL.md).

## Hand off submission

Report prepared files, the actual resume version, outstanding questions and the next action. Keep the existing job ID, form/draft IDs and progress in the [job record](../../docs/data.md#job-record). The user reviews and performs final Submit/Send. Wait for explicit confirmation identifying the submitted job.

## Record and archive

After user confirmation, run [submit](../../docs/commands.md#submission-and-archive) with the confirmed date and confirmation source. For self-submitted jobs, record only the known actual resume; leave an unknown version unknown. Preserve historical employer/candidate activity dates during metadata edits.

Run local [archive](../../docs/commands.md#submission-and-archive) to copy materials, verify hashes and clean only temporary copies. When Notion is configured, synchronize the same ID through the [integration field map](../../docs/integrations.md#notion), upload the actual materials and open/read back saved attachments. Retain local durable archives when the external write is pending; report its status and exact object IDs.

Keep interrupted job state and files for resumption. On explicit abandonment, record the decision with [abandon](../../docs/commands.md#submission-and-archive); remove only its verified local temporary material. For separately requested external cleanup, verify exact job-owned draft/message/page IDs, delete only those objects and read back the result. Preserve submission history.

## Interviews

Record one interview round under the existing job record, retaining invitation source, contact, status and known details. An invitation without a booked time stays pending with an empty time. Confirmed slots use the actual date, timezone, location/link and confirmed end time. Rescheduling updates the existing round. The user arranges appointments. Synchronize configured external interview records by the same job/round identity.
