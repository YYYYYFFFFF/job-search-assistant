# Command reference

All examples run from the package root. Global `--workspace PATH` precedes the subcommand. JSON input/output uses UTF-8. Exit codes: `0` success, `1` incomplete doctor check, `2` invalid input or failed operation. Helpers validate local records; the agent performs source research, factual assessment, document review and connected-service actions.

## Jobs

```sh
python3 scripts/career.py add-job /path/to/job.json
python3 scripts/career.py list
python3 scripts/career.py show JOB_ID
python3 scripts/career.py update-job JOB_ID /path/to/refreshed-job.json
python3 scripts/career.py progress JOB_ID /path/to/progress.json
```

Input schema: [job record](data.md#job-record). `add-job` returns an existing ID for a matching requisition/canonical URL; possible employer/title/location cross-posts require resolution. `update-job` replaces source facts only for an active job with the same identity. Progress input is a partial object with the documented progress fields.

## Recommendations

```sh
python3 scripts/career.py recommend JOB_ID
python3 scripts/career.py recommend JOB_ID --receipt EXACT_SENT_MESSAGE_ID
```

The default prints a chat recommendation and records local delivery. Email mode records a receipt after a connected-tool send; this command has no mail-sending transport. A repeated delivery returns its existing receipt.

## Resumes

```sh
python3 scripts/career.py register-resume 'Data Analytics' '1.0' /path/to/resume.pdf --approved-by-user
```

Registration copies an existing reviewed PDF into an immutable version path, records its checksum and selects the release as active. It does not write resume content or modify the input PDF. PDF header/checksum checks are file checks; content and visual checks belong to the Skill.

## Application materials

```sh
python3 scripts/career.py prepare JOB_ID --resume 'Data Analytics' --letter /path/to/completed-letter.json
python3 scripts/career.py attach JOB_ID /path/to/other-required-file.pdf
```

Letter input: [template](../templates/letter.json), with each string replaced by actual final wording. The helper creates an A4 Word document and copies the exact resume. It limits letter length to 450 words; rendered one-page fit requires a document viewer. Additional files and hashes are added with `attach`. Existing material is preserved on collision/failure.

## Submission and archive

```sh
python3 scripts/career.py submit JOB_ID --date 2030-04-15 --note 'User confirmed submission in chat' --confirmed-by-user
python3 scripts/career.py archive JOB_ID
python3 scripts/career.py abandon JOB_ID --confirmed-by-user
```

For a job already submitted outside this workflow:

```sh
python3 scripts/career.py submit JOB_ID --date 2030-04-15 --note 'User confirmed self-submission; version unknown' --unknown-resume --confirmed-by-user
```

Use `--resume CATEGORY` instead of `--unknown-resume` only when that category's current release is confirmed as the actual submitted file. A prepared job already retains its selected version. `--confirmed-by-user` represents confirmation already received; it does not operate any employer form.

Archive copies listed files, checks their SHA-256, saves archive metadata and then removes only the corresponding active folder. Failed verification preserves originals. A repeat returns the saved archive. Abandonment cleans only verified unsubmitted temporary materials and retains the local identity/decision. External drafts/messages/pages are separate connected-tool objects.

## Maintenance

```sh
python3 scripts/career.py keyword-demand 'Data Analytics'
python3 scripts/career.py save-idea --question 'Tell me about a project' --category Projects --idea 'Approved example and contribution' --approved-by-user
```

Demand output includes distinct vacancies, missing tag coverage and term counts. An idea is updated in place for the same normalized question. Semantically equivalent questions can use the established prompt text to reuse that row.
