# Phase 4: Review

Pedagogical quality review with autonomous auto-rewrite. No user intervention needed unless critical issues are found.

## Prerequisites

All chapters written. `.project-documenter.json` status is `"written"`.

## Process

### Step 1: Launch Pedagogy Reviewer

Spawn the `pedagogy-reviewer` agent. Provide it with:
- All chapter files from `<output_path>/chapters/`
- The `.project-documenter.json` configuration (audience, tone, emphasis)
- The quality criteria from the book-writing skill

### Step 2: Review Criteria

The reviewer evaluates each chapter against these criteria, scoring 1-5:

| Criterion | What it measures |
|-----------|------------------|
| **Engagement** | Would someone choose to keep reading? Narrative hooks present? |
| **Progressive complexity** | Does each section build on the last? No unexplained forward references? |
| **Context before detail** | Is "why" always before "how"? |
| **Concrete examples** | Are abstract concepts grounded in real code/scenarios? |
| **Tone match** | Does it match the target audience? |
| **Completeness** | Are all assigned modules/topics covered? |
| **Navigability** | Clear headings, logical flow, good transitions? |

### Step 3: Produce Review Report

The reviewer generates `<output_path>/review-report.md`:

```markdown
# Documentation Review Report

## Summary
- Chapters reviewed: N
- Average quality score: X.X/5
- Chapters needing revision: N

## Per-Chapter Results

### Chapter 1: <title>
| Criterion | Score | Notes |
|-----------|-------|-------|
| Engagement | 4 | Strong opening hook |
| Progressive complexity | 3 | Section 3 assumes knowledge from Ch4 |
| ... | ... | ... |

**Overall: X.X/5**
**Needs revision: Yes/No**
**Issues:**
- <specific issue with location>
- <specific issue with location>
```

### Step 4: Auto-Rewrite Weak Sections

For any chapter scoring below 3.5/5 overall, or any criterion scoring below 3:

1. Extract the specific issues from the review report
2. Re-spawn a `chapter-writer` agent with:
   - The original writing brief
   - The current chapter content
   - The specific revision instructions from the reviewer
   - Flag: `revision: true` (agent knows to improve, not rewrite from scratch)
3. Replace the chapter file with the revised version

### Step 5: Final Check

After all revisions:
1. Re-run a lightweight review (engagement + continuity only) on revised chapters
2. If any chapter still scores below 3/5, flag it in the report but proceed (avoid infinite loops)
3. Update `book.md` with revised chapters
4. Update `.project-documenter.json` status to `"reviewed"`

---

## Revision Limits

- Maximum 2 revision passes per chapter
- If a chapter fails after 2 passes, include it with a note in the review report
- The goal is quality, not perfection — diminishing returns after 2 passes

---

## Phase 4 Complete

Documentation reviewed and revised. Return to SKILL.md routing — next is Phase 5.
