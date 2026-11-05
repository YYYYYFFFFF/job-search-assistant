# Job Search Assistant

Use the user's latest instruction and the private workspace selected by `--workspace` or `CAREER_WORKSPACE`, default `.career/`. Analysis requests authorize discussion. Run [initialization](docs/setup.md#local-setup) when the user requests setup. Repository Skills are written in English; chat follows the user's language.

## Routing

| User request | Workflow owner |
|---|---|
| Find jobs, screen, recommend or recover delivery | [Job Search](skills/job-search/SKILL.md) |
| Prepare named/selected jobs, resume an application, record submission or interview | [Job Application](skills/job-application/SKILL.md) |
| Maintain facts, priorities, project details, search preferences or resume keywords | [Career Maintenance](skills/career-maintenance/SKILL.md) |
| Discuss a standalone question and save its approved answer idea | [Question Bank](skills/question-bank/SKILL.md) |

An application request for a directly named role calls Job Search's [job information preparation](skills/job-search/SKILL.md#prepare-job-information) only for missing JD fields, then continues Job Application. A search request ends at recommendations. The user performs final employer Submit or Send.

## Sources and boundaries

Use the [workspace map](docs/data.md#workspace-map) to locate each owner. Read relevant sections once and retain source references and modification times; refresh changed, missing or time-sensitive information. Pass the same job record between Skills. Changing Skills does not restart completed checks.

Candidate claims come from private `profile.json` and its cited evidence; project facts stay with their project. Preserve actual titles, contributions, proficiency, dates and results. Unknown facts remain unknown. Verify current legal/work-rights questions against the user's documents and authoritative jurisdiction-specific sources before relying on them.

Discover the live connected tool and exact object/session before external reads and writes. Use [integration configuration](docs/integrations.md) for destinations. Credentials stay in the host's authentication system. The user handles passwords, MFA and access consent.

Keep browser work in an authorized background session. Reuse the chosen page/draft identity. If an operation requires focus or a new visible window, tell the user and obtain that preference before proceeding with the disruptive operation. Keep other jobs moving when one requires input.

Preserve existing files and resume releases. Clean only verified job-owned temporary files through [local storage commands](docs/commands.md). External deletion requires explicit scope and exact object IDs. Failures retain resumable records and files. Maintenance runs on request; confirmed corrections update their existing owners.
