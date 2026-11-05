---
name: career-maintenance
description: Maintain requested priorities, candidate facts, project evidence and search preferences; propose and release approved resume keyword revisions.
---

# Career Maintenance

## Maintain the requested owner

Use the [workspace map](../../docs/data.md#workspace-map) to update the relevant existing owner:

- Priorities and temporary preferences: private `CURRENT.md`, retaining scope/end conditions.
- Personal facts, tools, employment and education: private `profile.json`, retaining confirmation source and actual check dates; remove resolved open questions.
- Projects: the exact private project evidence linked from `profile.json`, recording contribution, state, assets and reuse permission.
- Lasting search directions, keywords, exclusions and platforms: private `config.json`, preserving unrelated preferences and distinguishing exclusions from cautions.
- Connector destinations: private `config.json` integration entries, using exact verified object/session IDs from [integration setup](../../docs/integrations.md).
- Workflow rules and navigation: affected Skill or entry point, with working incoming links.

Verify changed/time-sensitive official claims using authoritative sources for the user's jurisdiction and personal documents. Record source-check dates separately from edit dates. Recompute affected unrecorded tool targets after tool facts change using [Job Search preparation](../job-search/SKILL.md#prepare-job-information), preserving other job fields and activity dates.

## Resume keywords

### 1. Count demand

Use [keyword-demand](../../docs/commands.md#maintenance) for the requested category's saved keywords, capabilities and tools. Count each normalized term once per distinct vacancy across those fields; report missing tag coverage. Learning targets add no demand occurrence.

### 2. Propose wording

Compare demand with the existing category master in private `resumes.json`. Show frequencies, a justified cutoff and exact proposed wording. Use equivalent wording or recorded experience to support each term. Check a relevant fact only when the change adds a claim. Preserve facts and layout. Wait for approval of the exact wording.

### 3. Release the approved revision

Use the configured Canva design or the user's existing editable source through [resume integration](../../docs/integrations.md#resume-editor). Apply only approved wording. Review the actual design and exported PDF at reading size for content, layout, selectable text, extraction order and contact links. Obtain the PDF through the supported export or the user's download.

Register a new immutable version with [register-resume](../../docs/commands.md#resumes). Verify its actual bytes/checksum before selecting it as current. Preserve previous releases and files referenced by applications. When an external resume archive is configured, verify that copy and attachment before declaring external synchronization complete. Retain the existing release if validation or registration fails.
