# Data reference

## Workspace map

Paths below are relative to the selected private workspace, default `.career/`.

| Information | Owning file/directory |
|---|---|
| Personal contact, work rights, skill depth, employment, education and project evidence links | `profile.json` |
| Permanent search preferences, countries/regions, directions/categories, source URLs and connector destinations | `config.json` |
| Current scope and temporary priorities/end conditions | `CURRENT.md` |
| Vacancy facts, assessment, delivery, application progress, submission and interview rounds | `jobs/<id>.json` |
| Immutable resume releases, hashes and category's active version | `resumes.json`; bytes in `resumes/<category>/<version>.pdf` |
| Approved standalone answer ideas | `questions.json` |
| Active job-owned application material | `applications/<id>/` |
| Verified durable local material | `archive/<id>/` |

Notion/email references are exact object IDs stored on that same job's `progress`; they identify external views/copies. The local record is the durable handoff for this distribution. `CURRENT.md` contains current priorities, rather than a second application history.

## Configuration

The [config template](../templates/config.json) contains:

- `language`, `timezone`: user's chat language and an IANA timezone, initially `en` and `UTC`.
- `search.days`: default publication lookback; `directions`, `locations`, `job_types`, `keywords` and `platforms`: user-defined search scope and source URLs.
- `search.excluded_terms`: literal case-insensitive excluded substrings for the local recommendation guard; `conditions`: nuanced conditions assessed by the Skill.
- `integrations.delivery`: `chat` or `email`; `email`: exact mailbox and self-recipient.
- `integrations.notion`: exact configured application tracker/resume/question/project/interview destinations, initially empty.
- `integrations.canva.designs_by_category`: user-owned editable designs keyed by resume category, initially empty.

## Job record

[`examples/job.json`](../examples/job.json) is a complete fictional import. `add-job` accepts source facts, rather than lifecycle state:

| Source field | Type / contents |
|---|---|
| `employer`, `title`, `location`, `url`, `category`, `checked_at` | Nonempty text; check time in ISO 8601 |
| `requisition_id` | Confirmed employer/ATS requisition, optional; provider-only board IDs remain in evidence |
| `published_at`, `deadline`, `duration`, `compensation`, `contact`, `job_type` | Advertised values or absent/unknown |
| `jd.responsibilities`, `jd.requirements` | Ordered nonempty arrays of source bullets; indentation can retain nesting |
| `screening.open`, `in_window`, `location`, `eligibility` | `true`, `false` or `null` |
| `screening.match` | `high`, `partial`, `exclude`, `hold`; reasons/evidence alongside |
| `keywords`, `capabilities`, `tools`, `tools_to_learn` | Unique meaningful term arrays |
| `evidence` | Source references, check context, source limitations and matching rationale |

Generated record fields: `id`, `state`, `source`, canonical URL `aliases`, `delivery`, exact `resume` release, `materials` path/hash pairs, `submission`, `archive` and optional `progress`.

States are `discovered → recommended → prepared → submitted`; directly named jobs can enter `prepared` without recommendation. `abandoned` retains the identity/decision. Archive metadata accompanies `submitted`. Missing historical resume releases remain `null`.

`progress` fields: `step`, `pending_questions`, `form_url`, `session_id`, `draft_id`, `notion_page_id`, `interviews`, `answers`, `next_action`. Interview entries carry a stable round ID, status, source, date/time/timezone and location/link where known.

## Resume registry

[`resumes.json`](../templates/resumes.json) has `active: {category: version}` and `releases` containing category/version/path/SHA-256. A prepared job retains its own exact release snapshot, so a later release does not change historical applications.
