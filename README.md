# Job Search Assistant

An agent-assisted job-search workflow: find suitable roles, prepare application materials, review them yourself and maintain the facts/resume keywords used next time.

Start with local files and chat recommendations. Add Notion, email or Canva when you want them. Your profession, country, search preferences, resume categories and service links are private configuration.

## Start

1. Download this repository, open it in Codex and follow [setup](docs/setup.md).
2. Run `python3 scripts/career.py init` and fill your private profile/preferences with the agent.
3. Register your existing resume PDFs. Ask the agent to find jobs, then choose which applications to prepare.
4. Review and submit applications yourself. Tell the agent which you submitted so it can record and archive them.

Python 3.9+ is enough for the local helper. Live search/forms require web/browser tools in your agent host. A document viewer checks the final Word layout. [Optional integrations](docs/integrations.md) use each user's own authenticated account.

## Four Skills

| Skill | Responsibility |
|---|---|
| [Job Search](skills/job-search/SKILL.md) | Discover, screen, match, deduplicate and recommend |
| [Job Application](skills/job-application/SKILL.md) | Prepare materials/answers, hand off submission and archive confirmed applications |
| [Career Maintenance](skills/career-maintenance/SKILL.md) | Maintain facts/preferences and approved resume keyword releases |
| [Question Bank](skills/question-bank/SKILL.md) | Discuss standalone questions and retain approved answer ideas |

[AGENTS.md](AGENTS.md) routes requests. Skills contain execution rules; [data reference](docs/data.md) identifies owners and schemas. Each job keeps one record across the workflow.

## Try it

```sh
python3 scripts/demo.py
python3 -m unittest discover -s tests -v
python3 scripts/check_package.py
```

The fictional demo runs discovery intake, recommendation, material preparation, simulated user-confirmed submission, archive and maintenance in temporary storage. It sends nothing. [Verification](docs/verification.md) separates automated checks from live account checks.

## Distribution and contribution

The repository can be used as a GitHub template. A portable `plugin.json` also packages the same Skills for compatible hosts; plugin-directory publication/approval is separate from this GitHub source release. See [setup](docs/setup.md#optional-plugin-package).

Run the commands above before proposing changes. Keep reusable rules in their owning Skills, source schemas in references, and user data in the private workspace. [Command reference](docs/commands.md) covers deterministic local operations.

MIT licensed. The distributed examples are fictional and the Word layout is independently authored.
