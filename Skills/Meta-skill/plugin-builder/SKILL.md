---
name: plugin-builder
description: Build a bespoke Claude Code plugin for any project by picking components from the PluginKit buffet and refactoring them to fit the project context. This skill should be used when the user asks to "create a plugin", "build a Claude Code plugin", "equip this project with a plugin", "generate a plugin from components", "assemble a plugin for this project", or "what plugin would fit this project". Works with any platform. Analyzes the project, queries the PluginKit (https://github.com/GuillaumeBld/PluginKit), selects the best-fit commands/agents/skills/hooks/MCP components, adapts every placeholder to the actual project context, and assembles a ready-to-use plugin. Output is always a finished, project-specific plugin — never a generic template dump.
---

# Plugin Builder

Builds a bespoke Claude Code plugin for any project by picking components from the **PluginKit** buffet and adapting them to fit the project's actual context.

## What It Does

```
PluginKit (raw ingredients)  +  plugin-builder (chef)  =  bespoke plugin (finished dish)
```

1. **Analyze** the project — stack, domain entities, services, env vars, paths
2. **Browse** the PluginKit `index.json` — score components by relevance
3. **Pick** the best-fit commands, agents, skills, hooks, MCP servers
4. **Adapt** each component — resolve all `{{placeholders}}` with real project values
5. **Assemble** — write the plugin directory structure, verify no gaps remain

## PluginKit

Repository: **https://github.com/GuillaumeBld/PluginKit**

- `index.json` — lightweight discovery index (always load this first, never catalog.json)
- `Commands/` — slash command templates
- `Agents/` — autonomous agent templates
- `Skills/` — auto-activating skill templates
- `Hooks/` — event handler templates
- `MCP/` — MCP server templates

## Autonomous Execution

The **plugin-builder agent** (`PluginKit/plugin-builder/AGENT.md`) handles everything end-to-end. Invoke it with:

> "Build a Claude Code plugin for this project"

The agent will:
- Read project files (README, CLAUDE.md, package.json, Makefile, .env.example)
- Fetch `index.json` from PluginKit
- Score and select components
- Replace all `{{placeholders}}` with project-specific values
- Write the finished plugin to `<project-name>-plugin/`
- Report any gaps that need manual review

## Script Pipeline (manual)

```bash
# Clone the store
git clone https://github.com/GuillaumeBld/PluginKit /tmp/PluginKit

# Step 1: Analyze project
python3 /tmp/PluginKit/plugin-builder/scripts/analyze-project.py /path/to/project > context.json

# Step 2: Pick components
python3 /tmp/PluginKit/plugin-builder/scripts/pick-components.py context.json > selection.json

# Step 3: Adapt to project context
python3 /tmp/PluginKit/plugin-builder/scripts/adapt-to-context.py selection.json context.json /tmp/PluginKit > adapted.json

# Step 4: Assemble plugin
python3 /tmp/PluginKit/plugin-builder/scripts/assemble-plugin.py adapted.json /path/to/output
```

## Plugin Structure (output)

```
<project-name>-plugin/
├── .claude-plugin/plugin.json   ← manifest (name, version, description)
├── commands/                    ← slash commands adapted to project
├── agents/                      ← subagents adapted to project domain
├── skills/<name>/SKILL.md       ← auto-activating skills
├── hooks/hooks.json             ← event hooks
└── .mcp.json                    ← MCP server (if applicable)
```

## Activation

```bash
# Test locally
claude --plugin-dir /path/to/plugin

# Install permanently
cp -r /path/to/plugin ~/.claude/plugins/<plugin-name>
```

## Key Principle

The store provides **templates with `{{placeholders}}`**. This skill ensures every placeholder is resolved with the project's actual values before the plugin is written. The result is always project-specific — never a generic copy-paste.

## Adding Components to the Store

After building a plugin, if a component is worth generalizing:
1. Extract reusable parts, replace project-specifics with `{{PLACEHOLDER}}`
2. Add `requires_adaptation` list in frontmatter
3. Copy to the appropriate `PluginKit/<Type>/<name>/` directory
4. Run `python3 PluginKit/plugin-builder/scripts/generate-index.py` to rebuild index

## Related

- **skills-store-access** — access the Skills_store (this repository)
- **PluginKit** — https://github.com/GuillaumeBld/PluginKit
- **skill-creator** — create new skills for the Skills_store
