# Phase 3: Write

Parallel chapter writing using subagents. This is the core production phase.

## Prerequisites

`.project-documenter.json` must exist from Phase 2 with `status: "ready"`.

## Process

### Step 1: Prepare Chapter Assignments

Read the approved outline from `.project-documenter.json`. For each chapter, prepare a writing brief:

```json
{
  "chapter_number": 1,
  "title": "...",
  "pattern": "...",
  "covers_modules": ["..."],
  "audience": "...",
  "tone": "...",
  "depth": "...",
  "story_context": "...",
  "emphasis": ["..."],
  "exclusions": ["..."],
  "previous_chapter_summary": "...",
  "next_chapter_preview": "..."
}
```

The `previous_chapter_summary` and `next_chapter_preview` fields ensure narrative continuity across chapters. For chapter 1, `previous_chapter_summary` is null. For the last chapter, `next_chapter_preview` is null.

### Step 2: Launch Chapter Writers in Parallel

Spawn one `chapter-writer` agent per chapter using the Agent tool. All agents run concurrently.

Each agent receives:
- The writing brief (above)
- The project-map.json (full codebase analysis)
- Access to Read and Grep tools (to examine source code)
- The book-writing skill's pedagogical principles (embedded in agent system prompt)

**Parallelization strategy:**
- Chapters with no dependencies on each other launch simultaneously
- If a chapter explicitly builds on another (e.g., "Getting Started" needs "Architecture"), provide the dependency chapter's summary in the brief
- Maximum parallel agents: match the number of chapters (typically 4-8)

### Step 3: Collect and Assemble

As chapter agents complete:

1. Save each chapter to the output directory: `<output_path>/chapters/ch<N>-<slug>.md`
2. Track completion in `.project-documenter.json`
3. When all chapters are done, generate:
   - **Table of contents**: `<output_path>/TOC.md`
   - **Combined book**: `<output_path>/book.md` (all chapters concatenated with page breaks)
   - **Chapter index**: Update `.project-documenter.json` with file paths

### Step 4: Continuity Check

After all chapters are written, do a quick continuity scan:
- Check that cross-references between chapters are valid
- Verify no forward references to unexplained concepts
- Ensure consistent terminology across chapters
- Fix any continuity issues directly (minor edits, not full rewrites)

Update status in `.project-documenter.json` to `"written"`.

---

## Chapter Writing Guidelines (for agent system prompts)

Each chapter-writer agent follows these rules:

### Structure
- Open with a narrative hook — a question, scenario, or problem
- Provide context before diving into details
- Use concrete examples before abstract explanations
- Close with a bridge to the next topic

### Code Examples
- Include real code from the project, not invented examples
- Use file path references: `src/api/routes.ts:42`
- Show the most illuminating snippet, not the longest
- Always explain what the code does and why it matters

### Formatting
- Use markdown headers for sections (## and ###)
- Use callout blocks for important notes: `> **Note:** ...`
- Use diagrams (mermaid) for architecture and flow explanations
- Keep paragraphs short — 3-5 sentences max
- Use bullet lists for enumerations, prose for explanations

### Length
- Short chapters: 800-1,200 words
- Medium chapters: 1,500-2,500 words
- Long chapters (deep dives): 3,000-5,000 words
- Let content determine length — don't pad, don't truncate

---

## Phase 3 Complete

All chapters written and assembled. Return to SKILL.md routing — next is Phase 4.
