# Phase 1: Configure

Ask each question and wait for the user's answer before proceeding. Do NOT skip steps or assume defaults.

## Contents

- Step 1: Analyze Source
- Step 2: Primary File Type
- Step 3: Grouping Logic
- Step 4: Companion Files
- Step 5: Shared/Global Files
- Step 6: Output Directory & Naming
- Step 7: Output Format(s)
- Step 8: Focus Prompt

## Progress Checklist

Copy this checklist and track your progress:

```
Configuration Progress:
- [ ] Step 1: Analyze source directory
- [ ] Step 2: Primary file type selected
- [ ] Step 3: Grouping logic selected
- [ ] Step 4: Companion files configured
- [ ] Step 5: Shared/global files configured
- [ ] Step 6: Output directory & naming set
- [ ] Step 7: Output format(s) selected
- [ ] Step 8: Focus prompt collected
```

---

## Step 1: Analyze Source

Ask the user for the source path (files or folder to transform), or use the path they already mentioned.

Then analyze it using filesystem tools (Glob, Read, directory listing):

1. Present a **directory tree** showing folders and subfolders.
2. List **file types detected with counts** (e.g., "86 .md files, 86 .png files, 21 gesture images in generated_gestures/").
3. Show **file distribution per subfolder**.
4. Note any non-content directories (shared asset folders, config folders, etc.).

Present the full picture to the user. They need to see what exists before making decisions.

**GATE: Wait for the user to acknowledge the analysis before proceeding to Step 2.**

---

## Step 2: Primary File Type

Ask the user:

> "Which file type(s) should be the **primary content** — the files that define each notebook? For example, if you have .md and .png files, should each .md file become its own notebook?"

Let the user specify one or more file extensions (e.g., `.md`, `.pdf`). These files determine how many notebooks get created.

**GATE: Wait for the user's answer before proceeding to Step 3.**

---

## Step 3: Grouping Logic

Ask the user how to group the primary files into notebooks:

| Option | Description |
|--------|-------------|
| `individual_file` | Each primary file becomes its own notebook |
| `subfolder` | All primary files in each subfolder share one notebook |
| `folder` | All primary files in the entire source folder share one notebook |
| `custom` | User describes custom grouping rules |

**GATE: Wait for the user's answer before proceeding to Step 4.**

---

## Step 4: Companion Files

Check if there are **other file types in the same directories** as the primary files. If there are, ask:

> "I notice there are also [.png, .jpg, etc.] files alongside your [.md] files in the same folders. Should any of these be **included as additional sources** in each notebook alongside the primary file?"

If the user says yes, ask about the **pairing logic**:

| Pairing | Description | Example |
|---------|-------------|---------|
| `positional` | Match by position/index within folder | 1st .md with 1st .png |
| `name_prefix` | Match by shared filename prefix | `topic.md` pairs with `topic.png` |
| `all_in_folder` | ALL companion files go into EVERY notebook in that folder | All .png files in every notebook |
| `custom` | User describes their own matching rule | |

If there are no other file types alongside the primary files, tell the user and set companion files to disabled.

**GATE: Wait for the user's answer before proceeding to Step 5.**

---

## Step 5: Shared / Global Files

Ask the user:

> "Are there any **shared files or folders** from other locations that should be uploaded to **EVERY** notebook? For example, a common reference document, a set of images, or a template that provides context for all files."

If the user says yes, collect the path(s). If they say no, record shared_files as an empty list.

**GATE: Wait for the user's answer before proceeding to Step 6.**

---

## Step 6: Output Directory & Naming

Ask the user:

> "Where should the generated outputs be saved? (Default: `./notebook-decks-output/`)"
>
> "How should output files be named? Available variables: `{filename}`, `{subfolder}`, `{course}`, `{index}`, `{format}`. Default: `{filename}_{format}`"

**GATE: Wait for the user's answer before proceeding to Step 7.**

---

## Step 7: Output Format(s)

Present the supported output formats and ask the user to select one or more:

| Format | Sub-options |
|--------|-------------|
| `audio` | format: `deep_dive`, `brief`, `critique`, `debate`; length: `short`, `default`, `long` |
| `video` | format: `explainer`, `brief`; style: `classic`, `whiteboard`, `kawaii`, `anime`, `watercolor`, `retro_print`, `heritage`, `paper_craft` |
| `slide_deck` | format: `detailed_deck`, `presenter_slides`; length: `short`, `default` |
| `report` | format: `Briefing Doc`, `Study Guide`, `Blog Post`, `Create Your Own` |
| `quiz` | difficulty: `easy`, `medium`, `hard`; question_count: number |
| `flashcards` | difficulty: `easy`, `medium`, `hard` |
| `infographic` | orientation: `landscape`, `portrait`, `square`; detail_level: `concise`, `standard`, `detailed` |
| `mind_map` | (no sub-options) |
| `data_table` | description: text describing what data to extract |

For each selected format, ask which sub-options to use. Multiple formats can be selected — all will be generated from the same notebook per batch.

If `slide_deck` is selected, ask: "Enable automatic watermark removal for slide decks?" (default: yes)

**GATE: Wait for the user's answer before proceeding to Step 8.**

---

## Step 8: Focus Prompt

This is the most important question. Ask the user:

> "What instructions or focus should be given to NotebookLM when generating the content? This guides the AI on what to emphasize. For example:
> - 'Focus on key concepts and practical examples'
> - 'Create beginner-friendly explanations with analogies'
> - 'Emphasize actionable takeaways and frameworks'
>
> You can provide one global prompt for all batches, or say 'none' to skip."

**CRITICAL GATE: You MUST wait for the user to respond. Do NOT proceed until you have their answer. Even "none" is a valid response — but the user must say it explicitly. Do NOT default to null without asking.**

Record the user's response as the `focus_prompt`.

---

## Phase 1 Complete

Configuration collected:
- Source path and file analysis
- Primary file type(s)
- Grouping logic
- Companion file settings
- Shared/global files
- Output directory and naming convention
- Output format(s) with sub-options
- Focus prompt

**Phase 1 done.** Return to SKILL.md routing — next is Phase 2.
