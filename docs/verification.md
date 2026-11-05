# Verification

## Reproducible local checks

```sh
python3 -m unittest discover -s tests -v
python3 scripts/demo.py
python3 scripts/check_package.py
```

The suite covers fresh configuration, preservation of existing data, private paths with spaces, canonical URLs and meaningful job IDs, cross-post deduplication, unknown eligibility, exclusions, delivery retries/receipts, Word XML/content, actual attachment hashes, explicit submission confirmation, archive corruption/copy failure, bounded cleanup, immutable resume history, demand counts, answer approval and a second profession/market.

The demo completes the local lifecycle using a fictional New Zealand analyst and temporary files. Its submission is simulated. It does not claim that a real person applied or that an employer accepted a form.

An optional `node scripts/browser-smoke.cjs` check uses an already installed Playwright module and Chrome to fill a loopback-only fictional form, upload the actual generated PDF/Word files, compare hashes and simulate a submit. `CAREER_PLAYWRIGHT_MODULE` selects an existing module path; `CAREER_PYTHON` selects Python; `CAREER_BROWSER_CHANNEL` selects an installed compatible browser channel. The test launches headless with the Chromium sandbox enabled and removes its temporary data.

## Live acceptance

An account owner authorizes each integration and runs the small checks in [integration acceptance](integrations.md#integration-acceptance-checklist). A fresh-account run verifies onboarding and live-source access beyond local fixtures. A real employer's form, authentication, eligibility and attachments remain role-specific checks.

Plugin packaging validation establishes package structure and paths. Installation in another agent host, marketplace submission and review are separate acceptance steps.

## Release evidence

Local test results, rendered-document checks, optional headless form checks and publication status are recorded in the release report after they are actually run. Automated checks reduce repeatable file/state errors; factual match quality and document presentation still require the Skill's source and visual review.
