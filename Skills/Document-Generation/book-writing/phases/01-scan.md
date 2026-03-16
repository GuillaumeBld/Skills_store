# Phase 1: Scan

Automated codebase analysis. No user input needed — the codebase-scanner agent handles this.

## Process

Launch the `codebase-scanner` agent with the project root path. The agent autonomously:

1. **Maps the directory structure** — identifies source directories, config files, docs, tests
2. **Detects tech stack** — languages, frameworks, package managers, databases
3. **Analyzes scale** — file count, line count, module count, dependency count
4. **Reads existing docs** — README, CONTRIBUTING, inline comments density, existing docs/
5. **Identifies key entry points** — main files, routers, CLI entry, build scripts
6. **Maps module relationships** — imports, dependencies between internal modules
7. **Reads git history** — project age, activity patterns, contributor count, recent changes
8. **Identifies patterns** — architecture style (monolith, microservices, CLI tool, library, etc.)

## Output

The agent produces `project-map.json` saved to the output directory:

```json
{
  "project_name": "...",
  "description": "...",
  "tech_stack": {
    "languages": [],
    "frameworks": [],
    "databases": [],
    "infrastructure": []
  },
  "scale": {
    "files": 0,
    "lines_of_code": 0,
    "modules": 0,
    "dependencies": 0
  },
  "architecture_style": "...",
  "key_entry_points": [],
  "modules": [
    {
      "name": "...",
      "path": "...",
      "purpose": "...",
      "key_files": [],
      "depends_on": [],
      "complexity": "low|medium|high"
    }
  ],
  "existing_docs": {
    "readme": true,
    "contributing": false,
    "docs_directory": false,
    "inline_comments_density": "low|medium|high"
  },
  "git_summary": {
    "age_days": 0,
    "total_commits": 0,
    "contributors": 0,
    "last_activity": "..."
  },
  "proposed_outline": [
    {
      "chapter": 1,
      "title": "...",
      "pattern": "origin-story|guided-tour|building-blocks|problem-solution|onboarding",
      "covers_modules": [],
      "estimated_length": "short|medium|long",
      "rationale": "..."
    }
  ]
}
```

The `proposed_outline` is the scanner's recommendation based on project characteristics. It gets presented to the user in Phase 2 for approval/modification.

## Phase 1 Complete

Project map generated. Return to SKILL.md routing — next is Phase 2.
