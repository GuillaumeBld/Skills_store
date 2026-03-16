---
name: project-nav
description: "This skill should be used when the user asks to 'generate a navigation skill', 'create a nav skill for this project', 'make the project navigable', or wants a project-scoped Claude Code skill that helps navigate the codebase. Generates a project-scoped skill file saved to <project>/.claude/skills/ that activates automatically in every session opened within that project."
---

# Project Navigation Skill Generator

Generate a project-scoped Claude Code navigation skill from completed documentation.

## What It Produces

A skill file saved at `<project>/.claude/skills/navigate-<project-slug>.md`.

Because it lives inside the project directory, Claude Code automatically makes it
available in every session opened within that project — and only that project.

## When to Use

- After `/document` completes (runs automatically as part of Phase 5)
- Standalone: when you want a nav skill for a project that's already documented
- After major refactors: regenerate to keep the skill current

## What the Skill Contains

```
navigate-<project>.md
├── Project at a Glance      — 2-3 sentence mental model
├── Architecture Map         — directory tree with annotations
├── Key Files Index          — table: file → purpose → when to open
├── Finding Things by Task   — "to do X, go to Y" patterns
├── Search Patterns          — ready-to-use grep/glob commands
├── Conventions to Know      — project-specific rules and patterns
└── Entry Points             — where the main flows start
```

## Scope

The skill is **project-scoped**: it only activates when Claude Code is run inside
the project directory. It does not pollute global Claude settings.

Each project gets exactly one nav skill. Re-running overwrites the previous version.

## Invocation

This skill is invoked by the orchestrator at the end of Phase 5. It can also be
triggered manually:

```
/document-nav /path/to/project
```

## Agent

The `nav-skill-writer` agent reads the project-map.json and chapter documentation
to produce the skill. It verifies every file path before including it.
