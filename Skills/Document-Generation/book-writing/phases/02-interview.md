# Phase 2: Interview

Gated questionnaire. Every question must be asked and answered before proceeding. Do not assume defaults.

## Prerequisites

`project-map.json` must exist from Phase 1.

## Progress Checklist

```
Interview Progress:
- [ ] Step 1: Present project summary
- [ ] Step 2: Audience
- [ ] Step 3: Tone & depth
- [ ] Step 4: The story
- [ ] Step 5: Output location
- [ ] Step 6: Output formats
- [ ] Step 7: Emphasis & exclusions
- [ ] Step 8: Weekly updates
- [ ] Step 9: Review proposed outline
- [ ] Step 10: Confirmation
```

---

## Step 1: Present Project Summary

Display the project map findings to the user:

```
=== Project Scan Results ===
Project:      <name>
Stack:        <languages, frameworks>
Architecture: <style>
Scale:        <files> files, <loc> lines, <modules> modules
Age:          <age>, <commits> commits, <contributors> contributors
Existing docs: <summary>
```

> "Here's what I found. Does this look accurate? Anything important I missed?"

**GATE: Wait for user acknowledgment.**

---

## Step 2: Audience

> "Who will read this documentation? This determines the tone, depth, and structure."
>
> Options:
> - **Developers** — engineers onboarding to or working with this codebase
> - **Stakeholders** — non-technical people (investors, managers, partners)
> - **Both** — adaptive documentation with technical depth available but not required
> - **Custom** — describe your audience

**GATE: Wait for answer.**

---

## Step 3: Tone & Depth

Based on audience answer, ask:

For **developers**:
> "What experience level should I target? Junior (explain everything), mid-level (explain architecture, skip basics), or senior (focus on decisions and non-obvious behavior)?"

For **stakeholders**:
> "What's their familiarity with the domain? Should I explain the business context or focus on capabilities and status?"

For **both**:
> "Should I create one unified document with layered depth, or separate versions?"

**GATE: Wait for answer.**

---

## Step 4: The Story

> "Every good documentation starts with 'why'. Tell me the story of this project:"
>
> - What problem does it solve?
> - What existed before it? What was painful?
> - What's the vision — where is it heading?
> - Any key decisions or turning points worth documenting?
>
> Even a few sentences help me write an engaging opening. If you'd rather I infer from the code and README, say 'infer'.

**GATE: Wait for answer. 'Infer' is valid — but the user must say it explicitly.**

---

## Step 5: Output Location

> "Where should the documentation be saved?"
>
> - Default: `./docs/book/` inside the project
> - Or specify a custom path
>
> The documentation will create: individual chapter files, a combined book file, and a table of contents.

**GATE: Wait for answer.**

---

## Step 6: Output Formats

> "What output formats do you want?"
>
> | Format | Description |
> |--------|-------------|
> | **Book** (markdown) | Always generated — the core documentation |
> | **Audio podcast** | NotebookLM deep-dive conversation about the project |
> | **Slide deck** | Marp presentation summarizing the project |
> | **Video explainer** | NotebookLM video walkthrough |
> | **Study guide** | NotebookLM study guide for learning the codebase |
>
> Select one or more. Audio/video/slides require NotebookLM MCP to be configured.

**GATE: Wait for answer.**

---

## Step 7: Emphasis & Exclusions

> "Any areas to emphasize or skip?"
>
> - Modules or features to go deep on?
> - Areas to exclude (deprecated code, internal tools, etc.)?
> - Sensitive information to avoid (credentials, internal URLs)?
>
> Say 'none' if the default coverage is fine.

**GATE: Wait for answer.**

---

## Step 8: Weekly Updates

> "Would you like automatic weekly documentation updates?"
>
> When enabled, every week the plugin will:
> - Detect changes via git diff since last run
> - Update relevant chapters
> - Generate a changelog slide deck (Marp) highlighting new features
>
> Options: **yes** (auto-setup cron), **no**, or **manual** (use `/document-update` when you want)

**GATE: Wait for answer.**

---

## Step 9: Review Proposed Outline

Present the scanner's proposed outline, enriched with interview answers:

```
=== Proposed Book Outline ===

Audience: <audience>
Tone: <tone>
Pattern: <dominant structural pattern>

Chapter 1: <title>
  Covers: <modules/topics>
  Pattern: <pattern used>
  Est. length: <short/medium/long>

Chapter 2: <title>
  ...

Appendix: <if applicable>

Total estimated chapters: <N>
```

> "Here's the proposed outline. You can:
> - **Approve** as-is
> - **Add** chapters
> - **Remove** chapters
> - **Reorder** chapters
> - **Rename** chapters
> - **Merge** or **split** chapters"

**GATE: Wait for explicit approval. Iterate until the user confirms.**

---

## Step 10: Confirmation

Save the documentation configuration to `.project-documenter.json` in the output directory:

```json
{
  "version": "1.0",
  "created_at": "<ISO timestamp>",
  "project_path": "<path>",
  "output_path": "<path>",
  "audience": "<audience>",
  "tone": "<tone>",
  "depth": "<depth>",
  "story": "<user's story or 'infer'>",
  "output_formats": ["book", "audio", "..."],
  "emphasis": [],
  "exclusions": [],
  "weekly_updates": true,
  "outline": ["<approved chapters>"],
  "status": "ready"
}
```

Display final summary:

```
=== Documentation Configuration ===
Project:     <name>
Audience:    <audience>
Tone:        <tone>
Chapters:    <N>
Formats:     <formats>
Output:      <path>
Weekly:      <yes/no>

Proceed with writing? (yes / edit)
```

**GATE: Wait for explicit 'yes'. On 'edit', return to the relevant step.**

---

## Phase 2 Complete

Configuration saved. Return to SKILL.md routing — next is Phase 3.
