---
name: notebooklm
description: "This skill should be used when the user asks to 'generate audio from docs', 'create a podcast from documentation', 'make slides from docs', 'create a video explainer', 'transform docs into learning materials', or wants to use NotebookLM for media generation from project documentation. Handles notebook creation, source upload, content generation (audio, video, slides, study guides), artifact download, and watermark removal."
---

# NotebookLM Media Generation

Transform project documentation into rich media outputs — audio podcasts, video explainers, slide decks, study guides — using the NotebookLM MCP.

## Rules

1. **MCP Only**: Use `notebooklm-mcp` MCP tool calls for ALL NotebookLM operations. NEVER use `nlm` CLI via Bash (except `nlm login` for auth).
2. **No Script Files**: NEVER create automation script files. Use MCP tool calls directly.
3. **State First**: Write state files before any `notebook_create` call.

## Supported Output Formats

| Format | NotebookLM Type | Sub-options |
|--------|----------------|-------------|
| Audio podcast | `audio` | format: `deep_dive`, `brief`, `critique`, `debate`; length: `short`, `default`, `long` |
| Video explainer | `video` | format: `explainer`, `brief`; style: `classic`, `whiteboard`, `kawaii`, etc. |
| Slide deck | `slide_deck` | format: `detailed_deck`, `presenter_slides`; length: `short`, `default` |
| Study guide | `report` | format: `Study Guide` |
| Briefing doc | `report` | format: `Briefing Doc` |

## Workflow

### Quick Generation (single format)

1. Verify MCP: call `server_info` to confirm NotebookLM MCP is running
2. Create notebook: `notebook_create` with project name as title
3. Upload sources: `source_add` with `wait=true`, `wait_timeout=120` for each file
4. Generate: `studio_create` with `confirm=true` and format-specific options
5. Poll: `studio_status` every 15-30 seconds until complete
6. Download: `download_artifact` to output path

### Batch Generation (multiple formats)

Read `phases/01-configure.md` for the full batch processing workflow with state tracking.

## MCP Reference

### Critical Parameters

| Tool | Parameter | Value | Required |
|------|-----------|-------|----------|
| `source_add` | `wait` | `true` | Yes — blocks until indexed |
| `source_add` | `wait_timeout` | `120` | Yes — sources need 60-90s |
| `studio_create` | `confirm` | `true` | Yes — fails silently without it |

### Source Types
- `file` — Local files (markdown, PDF, text)
- `url` — Web pages, YouTube links
- `text` — Pasted content
- `drive` — Google Drive files

### Focus Prompts for Documentation

Tailor the generation with context-appropriate prompts:

**For audio podcast:**
> "Create an engaging podcast discussion about this software project. Two hosts explore the architecture, explain key design decisions in plain language, and discuss what makes this project interesting. Target audience: developers considering using or contributing to this project."

**For video explainer:**
> "Create a visual explainer walking through this project's architecture and key features. Focus on the big picture and practical value."

**For study guide:**
> "Create a study guide for developers onboarding to this codebase. Include key concepts, architecture overview, and common tasks."

## Watermark Removal

For NotebookLM-generated slide deck PDFs, use the watermark cleaning script:

```bash
cd ${CLAUDE_PLUGIN_ROOT}/skills/notebooklm/scripts && npm install  # first time
node ${CLAUDE_PLUGIN_ROOT}/skills/notebooklm/scripts/clean-watermark.js <input.pdf>
```

Batch mode: `node clean-watermark.js --batch <directory>`

## Error Recovery

| Error | Fix |
|-------|-----|
| Auth failure | `nlm login` via Bash, then retry |
| Source timeout | Retry with `wait_timeout=300` |
| Studio creation fails | Verify sources are READY status first |
| Download fails | Check `studio_status` — artifact may still be generating |

## Additional Resources

### Phase Files
- **`phases/01-configure.md`** — Full batch processing configuration
- **`phases/02-confirm.md`** — State file creation and confirmation
- **`phases/03-process.md`** — Batch processing loop with state tracking

### Scripts
- **`scripts/clean-watermark.js`** — PDF watermark removal utility
