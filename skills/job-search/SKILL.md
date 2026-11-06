---
name: job-search
description: Search vacancies, screen eligibility and direction match, deduplicate, prepare JD information and deliver recommendations.
---

# Job Search

## Set search scope

Read private `config.json` search preferences, `CURRENT.md` temporary priorities and relevant `profile.json` location/work-rights facts through the [workspace map](../../docs/data.md#workspace-map). Fix the requested publication window at search start in the configured timezone; use `search.days` when no window is supplied. Original publication dates determine eligibility; reposts retain their original date.

Use configured platforms, keywords, locations and job types. Check current platform access. Follow directories and reposts to the current employer/ATS vacancy or the original recruiter ad when the employer is undisclosed. Try one suitable alternative for a blocked source and report the remaining gap; continue other accessible sources and candidate work.

For each configured career direction, check at least two independent sources within the permitted location/remote scope where accessible, and record any shortfall. Use native board filters, sorting and relevant pagination; verify that redirects preserve the applied filters and sort order. Keep indexed site-search results distinct from native board coverage. Retain the source, query, filters, access method, inspected pages/range and remaining gaps in the current context.

When results are sparse, fill planned coverage gaps with related terms and specialist, student or direct-employer sources, and seek missing evidence for promising holds within the access limits above. Stop expanding discovery only after accessible planned checks and candidate follow-ups are resolved or have a recorded blocker, and further accessible, relevant pages add no plausible new vacancies. Inaccessible pages, empty search-engine queries and the number of recommendations delivered do not establish that stopping condition.

## Screen and assess

Read each full JD. Apply configured conditions/exclusions and current scope. Verify open status, publication date, location and employment arrangement, and resolve facts needed to apply an explicit search condition. Record source evidence, check time and unresolved facts in the [job record](../../docs/data.md#job-record). Hold decisive missing vacancy evidence and exclude failed search conditions.

Treat other advertised qualifications, experience, graduation year, hours, pay and start date as cautions unless a configured search condition explicitly makes them a recommendation gate. Do not add candidate-readiness, tool-proficiency or resume-availability gates. Unknown candidate fit alone is not a hold reason. Preserve all requirements in the JD capture and explain fit concerns in chat, without claiming that the candidate meets them. Set `screening.eligibility` from the configured recommendation conditions; retain candidate-fit cautions in `evidence`.

Assess actual duties against configured career directions:

- **high:** principal duties directly practice a current direction.
- **partial:** explicit professional duties build relevant experience with a stated material gap.
- **exclude:** duties lack a concrete connection to a current direction.
- **hold:** decisive duties or evidence remain unclear.

Give a concrete JD-based reason. Shared titles, industries or tools alone do not establish direction match. Resume availability does not change discovery eligibility or match labels.

## Deduplicate

Read existing job identities once through [list/show commands](../../docs/commands.md#jobs). Match the confirmed employer requisition first, then canonical application URLs, then employer/title/location/JD. Merge cross-posts into the existing record; preserve confirmed different requisitions. Resolve possible matches before creating another record. A provider board ID is evidence of that posting's identity only.

## Prepare job information

Reuse the reviewed JD and completed fields in the [job record](../../docs/data.md#job-record). Retain the original source URL and check time.

1. Capture Role title, Company, Location, JD link, Application deadline, Duration, Compensation and Contact. Leave missing values unknown. Capture Responsibilities and Requirements in source order, retaining every bullet's meaning, nesting, alternatives, named tools and required/preferred status. Check the capture against the source once; label partial access and conflicts.
2. Choose a category from the user's configured career directions by principal outputs and recurring duties. Preserve the advertised title. Flag an unresolved category for discussion.
3. Extract `keywords` as meaningful occupational terms/phrases occurring at least twice after case, inflection and confirmed-alias normalization. Ignore duplicated source blocks and boilerplate; leave the set empty when appropriate. Extract explicitly advertised actions/outputs into `capabilities` and named software/languages/equipment into `tools`; one explicit mention suffices. Preserve scope and editions. Derive `tools_to_learn` from JD tools absent from recorded tools, labelling these as unrecorded learning targets, without inferring proficiency or inability.
4. Save the source fields with [add-job/update-job](../../docs/commands.md#jobs). Reuse the existing ID across application steps. Keep facts and evidence distinct from the assessment.

## Deliver recommendations

Deliver only high/partial jobs whose decisive checks passed. Once a job has passed deduplication and preparation, deliver its recommendation without waiting for unrelated sources or held jobs. Use Role and Info, Keywords, JD capture and Application Files in that order; Application Files states that materials are not prepared at discovery. Keep match reasons and cautions in chat.

For configured chat delivery, run [recommend](../../docs/commands.md#recommendations) and present its result. For email delivery, send one recommendation per job to the configured user recipient through the live mail tool, verify recipient/body/send evidence, then record its exact message ID with `recommend --receipt`. Recover uncertain sends by exact ID/targeted delivery evidence before retrying.

## Finish or resume

Before ending, account for sources checked or blocked and give every plausible job found a supported decision: retained, excluded, duplicate or held. Continue any remaining independent work that available tools and evidence allow.

Report the applicable outcomes separately:

- **Completed search:** discovery reached its stopping condition, all found candidates were screened, and all recommendations due were delivered and verified. Zero recommendations is valid after completed screening; never add jobs to meet a quota.
- **Partial coverage:** access gaps or unresolved essential checks prevent a completed-search conclusion. State actual coverage, held jobs, blockers and next steps; do not present this as a completed zero-result search.
- **Pending delivery:** retained jobs remain undelivered or their delivery status is uncertain. State each job's actual delivery status and available message IDs; continue other ready recommendations.

Report delivered jobs and reasons alongside these outcomes. Keep incomplete jobs and delivery evidence available in their existing records and reuse completed checks when resuming.
