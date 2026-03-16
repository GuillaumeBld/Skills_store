# Phase 3: Process

Process batches using NotebookLM MCP tools.

## Contents

- Step 1: Check Authentication
- Step 2: Batch Processing Loop
- Step 3: Watermark Cleaning
- Step 4: Verify & Checkpoint
- MCP Workflow Reference
- Error Handling
- Common Mistakes

## Rules

- **MCP tools ONLY**: Use `notebooklm-mcp:*` tool calls. NEVER use `nlm` CLI via Bash.
- **NEVER create script files** to automate processing.
- **Only allowed Bash**: `nlm login` (auth) and `node clean-watermark.js` (watermark removal).
- **Process ONE batch at a time**.

## Batch Progress Checklist

For each batch, copy and track:

```
Batch N Progress:
- [ ] 2a: Notebook created
- [ ] 2b: Sources uploaded
- [ ] 2c: Content generation started
- [ ] 2d: Generation complete
- [ ] 2e: Results downloaded
- [ ] 2f: State updated
- [ ] Step 3: Watermark cleaned (if slide_deck)
- [ ] Step 4: Verified & checkpointed
```

---

## Step 1: Check Authentication

1. Call `notebooklm-mcp:server_info` to verify MCP is running.
2. If auth error: try `notebooklm-mcp:refresh_auth`, then `nlm login` via Bash.
3. Verify with `notebooklm-mcp:notebook_list`.

---

## Step 2: Batch Processing Loop

Read the batch list from `.notebook-decks-meta.json`. For each batch with status "pending" or "failed":

### 2a. Create Notebook

Call `notebooklm-mcp:notebook_create` with the batch name as title.

Save `notebook_id` to `.notebook-decks-meta.json`. Update `tasks.md` status to "creating".

### 2b. Upload Sources

Upload ALL files in order: primary → companions → shared.

Call `notebooklm-mcp:source_add` for each file. **Important**: Set `wait=true` and `wait_timeout=120` to block until sources are processed.

Wait for all sources to reach READY status. Update `tasks.md` status to "sources_uploaded".

### 2c. Generate Content

Call `notebooklm-mcp:studio_create` with the artifact type from config. **Important**: Set `confirm=true` (required). Include `focus_prompt` if provided.

### 2d. Poll Status

Call `notebooklm-mcp:studio_status` every 15-30 seconds until complete. Update `tasks.md` status to "generating".

### 2e. Download Results

Call `notebooklm-mcp:download_artifact` with the output path following the naming convention.

### 2f. Update State (IMMEDIATELY after each batch)

After downloading all artifacts for a batch:

1. Update `.notebook-decks-meta.json`:
   - Set batch `status` to "downloaded"
   - Add `outputs` with file paths
   - Update `updated_at` timestamp

2. Update `tasks.md`:
   - Set batch row status to "downloaded" (or "cleaned" after watermark removal)
   - Add log entry: `- [<timestamp>] Batch N "<name>" completed`

3. Update `generation-config.jsonl`:
   - Update the batch line's status field

---

## Step 3: Watermark Cleaning (slide_deck only)

If `slide_deck` was generated AND `clean_watermarks` is `true`:

1. **Install dependencies** (first time only):
```bash
cd .claude/skills/notebook-decks/scripts && npm install
```
Required packages: `canvas@^3.0.2`, `pdf-lib@^1.17.1`, `pdfjs-dist@^3.11.174`

2. **Run watermark removal**:
```bash
node .claude/skills/notebook-decks/scripts/clean-watermark.js <downloaded_slides.pdf>
```
Output: `<name>_cleaned.pdf` in the same directory.

3. **Batch mode** (multiple PDFs):
```bash
node .claude/skills/notebook-decks/scripts/clean-watermark.js --batch <output_directory>
```

4. Update state: mark batch as "cleaned".

---

## Step 4: Verify & Checkpoint

After each batch is fully processed (generated + downloaded + optionally cleaned):

1. **Verify outputs exist** — check that downloaded files are present and non-empty (check file sizes).
2. **For cleaned PDFs** — verify the `_cleaned.pdf` file was created successfully.
3. **Update `tasks.md`** with final status for this batch.
4. **Update `.notebook-decks-meta.json`** with batch completion.
5. **Tell the user**: "Batch N/M '<name>' complete. Outputs saved to <paths>. Continue to next batch?"

If user says stop, save state and exit. The session can be resumed later.

---

## MCP Workflow Reference

Use `mcp__notebooklm-mcp__*` tools. Claude discovers tool schemas via introspection.

### Workflow Sequence

```
notebook_create → source_add (×N) → studio_create → studio_status (poll) → download_artifact
```

### Non-Obvious Parameters

| Tool | Parameter | Value | Why |
|------|-----------|-------|-----|
| `source_add` | `wait` | `true` | Block until source indexed |
| `source_add` | `wait_timeout` | `120` | Sources need 60-90s typically |
| `studio_create` | `confirm` | `true` | Required—fails silently without it |
| `notebook_delete` | `confirm` | `true` | Destructive operation safeguard |

### Response Handling

**studio_status response:**
```json
{
  "status": "success",
  "artifacts": [{
    "status": "in_progress" | "completed",
    "slide_deck_url": "..."
  }]
}
```
- Poll every 15-30s until artifact `status` = `"completed"`
- On `"completed"`: URL fields are populated → call `download_artifact`

**source_add response (with wait=true):**
```json
{ "source_id": "...", "status": "ready" | "processing" | "failed" }
```
- Only proceed when status = `"ready"`

### Example: Slide Deck Generation

```python
# 1. Create notebook
notebook_create(title="Chapter 1")
# { "notebook_id": "abc123" }

# 2. Add sources (MUST wait for each)
source_add(notebook_id="abc123", source_type="file",
           file_path="ch1.md", wait=True, wait_timeout=120)
# { "status": "ready" }

# 3. Generate slides (MUST confirm)
studio_create(notebook_id="abc123", artifact_type="slide_deck",
              format="detailed_deck", confirm=True)
# { "status": "success", "generation_status": "in_progress" }

# 4. Poll until complete
studio_status(notebook_id="abc123")
# { "artifacts": [{"status": "in_progress"}] }  # wait 15-30s
# { "artifacts": [{"status": "completed", "slide_deck_url": "..."}] }

# 5. Download
download_artifact(notebook_id="abc123", artifact_type="slide_deck",
                  output_path="./output/ch1_slides.pdf")
```

---

## Error Handling

| Error | Recovery |
|-------|----------|
| Auth failure | Run `nlm login` or `refresh_auth` MCP tool |
| Source upload timeout | Retry with longer `wait_timeout` (300s) |
| Source processing error | Check file format, try re-uploading |
| Studio creation fails | Check artifact type spelling, verify sources are READY |
| Download fails | Check `studio_status` first — artifact may still be generating |
| Watermark script error | Check Node.js version, run `npm install` in scripts/ |

Always update state files after errors so progress is not lost.

---

## Common Mistakes — Do NOT Do These

| Mistake | Correct Behavior |
|---------|------------------|
| Creating `process-decks.sh` or `.js` | Use MCP tool calls directly |
| Running `nlm notebook create` via Bash | Use `notebooklm-mcp:notebook_create` |
| Running `nlm source add` via Bash | Use `notebooklm-mcp:source_add` |
| Running `nlm slides create` via Bash | Use `notebooklm-mcp:studio_create` |
| Skipping the focus prompt question | Must be asked in Phase 1 |
| Not writing state files first | State files before `notebook_create` |
| Skipping Phase 2 confirmation | Must confirm before processing |
| Deleting outputs without asking | Ask user first |

---

## Cross-Conversation Resume

When resuming (routed here because state exists with incomplete batches):

1. All decisions are already in `.notebook-decks-meta.json` — do NOT re-ask questions.
2. Read `tasks.md` to find the first incomplete batch.
3. Start the batch processing loop from that batch.
4. Existing `notebook_id` values in meta.json mean the notebook already exists — check if sources are uploaded before re-creating.
