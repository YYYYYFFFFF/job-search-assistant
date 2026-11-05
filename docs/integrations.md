# Optional integrations

The baseline is local JSON/files plus recommendations in the conversation. Connector destinations belong in private `config.json`; access stays in the host's own account connections. This package includes no API keys, mail server, OAuth client or service-specific backend.

## Browser and existing login

Use your agent host's supported browser connection. To use an existing Chrome login, [Playwright MCP's official extension instructions](https://github.com/microsoft/playwright/tree/main/packages/extension) describe native browser consent and connection selection. An isolated automation browser has its own profile and will not inherit your daily browser's login.

The user selects the intended tab/session and handles login/MFA. Current browser tools determine background/focus behavior. Check the installed tool version's options before configuring it: development-branch documentation can describe flags absent from a released package. This repository does not install or rewrite your machine's browser configuration. The tested demo uses an isolated headless local form rather than a personal logged-in tab.

## Email

Set `integrations.delivery` to `email` and fill `integrations.email.mailbox` and `recipient` with your own mailbox/address. Connect the supported mail app in your agent host. Required capabilities: send recommendations, read exact sent messages for uncertain delivery, create/read/edit drafts and inspect attachments for employer email applications.

Search delivery receipts appear in each job's `delivery.receipt`. Application draft IDs appear in `progress.draft_id`. Without a supported mail connection, leave delivery as `chat`; email application material can be handed to the user as files/text.

## Notion

Optional destination entries:

| Config key | Destination contents |
|---|---|
| `application_tracker` | One row per local job/application ID |
| `resume_versions` | Category, version, checksum, attachment, change note |
| `question_bank` | Question, category, approved answer idea |
| `projects` | Exact user project pages/evidence links |
| `interviews` | Job ID, round ID, status, date/time/timezone, location/link |

Application field map:

| Local field | Suggested Notion property/body |
|---|---|
| `id` | Application ID (text, stable unique key) |
| `source.title`, `employer`, `location`, `category`, `job_type`, `url` | Role, Company, Location, Category, Job type, Source URL |
| `state`, `submission.result`, `submission.date` | Stage, Result, Submission date |
| `source.keywords`, `capabilities`, `tools`, `tools_to_learn` | Equivalent multi-select fields |
| `source.jd` | Page body: Role and Info, JD capture, Application Files |
| `resume`, `archive.files` | Exact release reference, actual file attachments, filenames/checksums |

Each user's live database schema supplies actual property names/types/options. There are no hardcoded Notion IDs. The agent uses the connected app's current tools to map/synchronize records; this distribution's Python helper performs local operations only. Pending cloud writes remain visible in job progress.

## Resume editor

With Canva, put the exact user-owned design ID under `canva.designs_by_category`. Editing/export depends on the connected tool's live capabilities. Existing PDF masters work without Canva. Other editable resume sources can use the same approved-wording/review/release workflow; Canva-specific automation is optional.

## Integration acceptance checklist

These are user-account setup checks, performed after that user connects their own services:

| Integration | Small acceptance check |
|---|---|
| Browser | Authorized intended tab visible to the agent; a benign field edit keeps the user's chosen focus behavior |
| Mail | User-requested self-test recommendation sent/read back with an exact message ID |
| Notion | User-requested fictional record and attachment written/read back in the selected test destination |
| Canva | User-requested test copy edited/exported; actual PDF opened and checked |

Synthetic local tests do not establish any of these account-specific results.
