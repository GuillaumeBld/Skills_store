# Phase 5: Produce

Media generation from the completed documentation. Only runs if user requested formats beyond "book" in Phase 2.

## Prerequisites

Documentation reviewed. `.project-documenter.json` status is `"reviewed"`.
Check `output_formats` — skip this phase entirely if only `["book"]` was selected.

## Process

### Step 1: Check NotebookLM Availability

If any format requires NotebookLM (audio, video, study guide):

1. Verify NotebookLM MCP is available by checking for `notebooklm-mcp` tools
2. If not available, inform the user:
   > "Audio/video/study guide generation requires NotebookLM MCP. Install it with: `nlm setup add claude-code`. Skipping media generation — your book documentation is ready."
3. If available, proceed with media generation

### Step 2: Launch Media Producer Agent

Spawn the `media-producer` agent with:
- The combined `book.md` file
- The output formats requested
- The output directory path
- The project name (for notebook naming)

### Step 3: Media Generation Workflow

The media-producer agent follows the notebooklm skill's phased approach:

#### For Audio Podcast
1. Create a NotebookLM notebook named `"<project-name> Documentation"`
2. Upload `book.md` as source (or individual chapters if book exceeds source limits)
3. Generate audio with format `deep_dive` and the project's focus prompt:
   `"Create an engaging podcast-style discussion about this software project. Explain the architecture, key design decisions, and how to get started as if explaining to a colleague."`
4. Download to `<output_path>/media/<project-name>-podcast.wav`

#### For Slide Deck (Marp)
1. Generate a Marp-formatted markdown presentation from the book content
2. Focus on: project overview, architecture diagrams, key flows, getting started
3. Save to `<output_path>/media/<project-name>-slides.md`
4. Include Marp frontmatter for theme and pagination

#### For Video Explainer
1. Create NotebookLM notebook (reuse if already created for audio)
2. Generate video with format `explainer`
3. Download to `<output_path>/media/<project-name>-explainer.mp4`

#### For Study Guide
1. Create NotebookLM notebook (reuse if already created)
2. Generate report with format `Study Guide`
3. Download to `<output_path>/media/<project-name>-study-guide.pdf`

### Step 4: Watermark Cleaning

If slide deck PDFs were generated via NotebookLM (not Marp):
1. Run the watermark cleaning script from the notebooklm skill
2. Save cleaned versions alongside originals

### Step 5: Generate Project Navigation Skill

Always run this step, regardless of media format selection.

Spawn the `nav-skill-writer` agent:

```
Agent: nav-skill-writer
Prompt: "Generate a navigation skill for <project-name>.
  Project path: <project_path>
  Project map: <project-map.json path>
  Chapters: <output_path>/chapters/
  Output: <project_path>/.claude/skills/navigate-<slug>.md"
```

The skill is saved inside the project directory so it activates automatically
in any future Claude Code session opened within that project.

### Step 6: Final Output Summary

Update `.project-documenter.json` status to `"complete"`.

Display to user:

```
=== Documentation Complete ===

Book:
  <output_path>/book.md (combined)
  <output_path>/chapters/ (individual chapters)
  <output_path>/TOC.md

Audio:       <output_path>/media/<name>-podcast.wav
Slides:      <output_path>/media/<name>-slides.md
Video:       <output_path>/media/<name>-explainer.mp4
Study Guide: <output_path>/media/<name>-study-guide.pdf

Nav Skill:   <project_path>/.claude/skills/navigate-<slug>.md

Review:      <output_path>/review-report.md
Config:      <output_path>/.project-documenter.json
```

---

## Phase 5 Complete

All requested outputs generated. Documentation pipeline finished.
