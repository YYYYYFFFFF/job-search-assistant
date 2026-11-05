# Setup

## Local setup

Requirements: Python 3.9 or newer and an agent with filesystem/shell access. Live vacancy discovery also needs the host's web/search or authorized browser tools. The Python helper itself has no network dependencies. A standard-library timezone database is available on many systems; on Windows, install `tzdata` if `doctor` reports a missing named timezone.

Download this repository as a ZIP, or use GitHub's **Use this template** once the repository is published as a template. Open the resulting folder in Codex. Root `AGENTS.md` routes to the four Skills in `skills/`; prompts work without copying them into a global skill directory.

From that folder:

```sh
python3 scripts/career.py init
python3 scripts/career.py doctor
```

On Windows use `py -3` where these examples use `python3`. `init` creates a private `.career/` folder. `doctor` initially reports missing profile/search fields.

Ask your agent:

> Help me set up this career workflow. Ask for my target roles, locations, work types, current work rights, existing resume PDFs and relevant experience. Put approved facts in the private workspace. Use chat recommendations and local archives initially.

Fill `.career/profile.json` and `.career/config.json` from your own facts/preferences. Tool entries can use `{ "name": "Tool", "scope": "actual capability", "source": "project or employment evidence" }`; employment/education/projects retain actual dates, labels, contribution and evidence links. Open questions stay in `profile.json.open_questions`.

Register an existing reviewed resume, assigning its actual category/version:

```sh
python3 scripts/career.py register-resume 'Data Analytics' '1.0' /path/to/resume.pdf --approved-by-user
python3 scripts/career.py doctor
```

Use `--workspace /path/to/private-folder` **before** the subcommand for another data location. `CAREER_WORKSPACE` also selects it. Place private data outside Git, or keep the default ignored `.career/`. Store credentials only through your host's supported authentication.

## Try the fictional demo

```sh
python3 scripts/demo.py
python3 -m unittest discover -s tests -v
python3 scripts/check_package.py
```

The demo uses a temporary data directory without Git, fictional people/jobs and a generated fictional PDF. It prints a lifecycle report and removes its temporary data. It never contacts an employer or sends email.

## Optional plugin package

Root `plugin.json` and `skills/` follow the [portable Agent Plugins layout](https://developers.openai.com/plugins/build/plugins). They package the same four Skills used by root `AGENTS.md`. Host plugin installation support varies. Opening the repository in Codex is the baseline installation; plugin-directory acceptance and installation in other hosts are separate checks.

Packaged Skills reference `../../docs/`, `../../scripts/` and `../../templates/` within the same package. Keep those folders together. A plugin host must provide writable private storage plus Python/shell access for the bundled helpers, or invoke the helpers locally; a remote-only chat surface does not execute this filesystem workflow by itself.

## First live run

> Find jobs from the past five days for my configured roles and locations. Recommend suitable jobs in chat. Show any access or eligibility gaps.

> Prepare these selected jobs with my registered resume. Ask about unknown answers. I will submit the applications myself.

> I submitted job ID … today using the prepared resume. Record it and archive its materials.

Use [integrations](integrations.md) when you want email, Notion, Canva or your existing browser login. They are optional; each account is authorized by its own user.
