---
name: weekly-changelog
description: "This skill should be used when the user asks to 'generate changelog slides', 'create weekly update', 'document recent changes', 'what changed this week', 'generate feature presentation', or wants automated weekly documentation updates with Marp slide decks. Handles git diff analysis, feature detection, chapter updates, and presentation generation."
---

# Weekly Changelog & Slide Generation

Detect project changes since the last documentation run, update relevant chapters, and generate a Marp slide deck highlighting new features.

## How It Works

### Change Detection

Analyze git history since the last documentation run:

1. Read `last_update` timestamp from `.project-documenter.json`
2. Run `git log --since="<last_update>" --oneline --stat` to identify changed files
3. Run `git diff <last_commit_hash>..HEAD --stat` for a summary
4. Categorize changes:
   - **New features** — new files, new modules, new endpoints
   - **Enhancements** — modified existing functionality
   - **Bug fixes** — fixes, patches
   - **Refactoring** — structural changes without behavior change
   - **Infrastructure** — CI/CD, dependencies, config changes

### Relevance Filter

Not every commit deserves a slide. Filter for:
- Changes affecting user-facing functionality
- New modules or significant new files
- Architecture changes
- Breaking changes
- Security-related changes

Skip: typo fixes, dependency bumps, formatting, test-only changes.

### Chapter Updates

For changes that affect documented modules:

1. Identify which chapters cover the changed modules (from `project-map.json`)
2. Spawn `chapter-writer` agents for affected chapters only
3. Provide the agent with:
   - Current chapter content
   - Git diff for the relevant files
   - Instruction: `revision: true, update_type: "incremental"`
4. The agent updates the chapter to reflect changes without full rewrite

### Marp Slide Generation

Generate a Marp-formatted markdown presentation:

```markdown
---
marp: true
theme: default
paginate: true
header: "<project-name> — Weekly Update"
footer: "Week of <date>"
---

# <Project Name> Weekly Update
## Week of <start_date> — <end_date>

---

## What's New

- <feature 1 — one line summary>
- <feature 2 — one line summary>

---

## <Feature 1 Title>

<2-3 sentences explaining the feature>
<code snippet or diagram if relevant>

---

## <Feature 2 Title>

...

---

## Under the Hood

- <refactoring/infra change 1>
- <refactoring/infra change 2>

---

## What's Next

- <upcoming work based on open branches/issues>

---

## Numbers

| Metric | This Week | Total |
|--------|-----------|-------|
| Commits | <N> | <N> |
| Files changed | <N> | <N> |
| Lines added | <N> | <N> |
| Lines removed | <N> | <N> |
```

### Output

Save to: `<output_path>/updates/week-<YYYY-MM-DD>.md`

Update `.project-documenter.json`:
- Set `last_update` to current timestamp
- Add entry to `update_history` array

## Cron Setup

When user opts in to weekly updates, create a cron entry:

```bash
# Weekly documentation update — every Monday at 9:00 AM
0 9 * * 1 cd <project_path> && claude -p "Run /document-update for this project" >> /var/log/project-documenter.log 2>&1
```

Adjust timezone and schedule based on user preference from Phase 2 interview.

## Manual Trigger

Users can run `/document-update` at any time for an on-demand update. The command reads `.project-documenter.json` to determine what changed since `last_update`.
