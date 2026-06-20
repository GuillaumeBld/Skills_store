---
name: full-research
description: >
  Full-spectrum, triangulated research with a step-by-step terminal interface
  (modeled on /deep-research's guided, phased UX). Fans out to THREE arms in
  parallel and cross-validates them: deep-research (verified general web with
  adversarial fact-checking), research-orchestrator (academic / peer-reviewed
  evidence), and last30days (last-30-days social + community pulse). Use when
  the user wants the most rigorous possible answer on a topic - what the
  fact-checked web says, what the literature says, AND what practitioners are
  saying right now - merged into one report that flags where all three agree
  (highest confidence) and where they diverge. Triggers: "full research on X",
  "triangulated/deep combined research on X", "evidence + web + community on X",
  "the works on X", "research X every way".
argument-hint: "full-research <topic>  [--days=N] [--arms=web,academic,social] [--yes]"
user-invocable: true
allowed-tools: Task, Skill, Bash, Read, Write, WebSearch, WebFetch
---

# Full-Research — triangulated 3-arm research, deep-research-style step-by-step UX

This skill orchestrates three existing research modalities and merges them. It
does NOT re-implement any of them. The terminal experience deliberately mirrors
`/deep-research`: announce a plan, move through numbered phases, show a live
progress tree, and only then deliver the synthesized report. Keep the user
oriented at every step - that guided, stepwise feel IS a requirement, not polish.

The three arms answer different questions; the fusion is the deliverable:

- **🌐 deep-research** (web): fact-checked, adversarially verified web sources.
  Authoritative-but-current; catches claims the academy hasn't published yet.
- **🎓 research-orchestrator** (academic): peer-reviewed / literature evidence
  with confidence levels. Slowest, most rigorous, may lag the present.
- **📰 last30days** (social): what practitioners are saying/shipping in the last
  30 days. Freshest, opinionated, high-signal-but-noisy.

A claim confirmed by all three is the highest-confidence output possible here.
A claim where they disagree is the most interesting finding - surface it loudly.

## Output discipline (applies throughout)

- No em-dashes anywhere. Use " - " (single hyphen with spaces).
- Citations inline as `[name](url)`; never fabricate a URL.
- The progress tree and phase banners are part of the contract - render them.

---

## PHASE 0 - Plan (show it, gate on it)

Parse the request:
- `TOPIC` = everything that is not a flag.
- `--days=N` → passed to last30days (default 30).
- `--arms=web,academic,social` → run only the listed arms (default: all three).
- `--yes` / `--fast` → skip the confirmation gate, dispatch immediately.

If no `TOPIC`, ask for one in a single short question and stop.

Render the plan card verbatim in this shape, substituting real values:

```
🔬 full-research · {TOPIC}

Plan - 3 arms, run in parallel, then triangulated:
  [1] 🌐 deep-research         · verified web + adversarial fact-check
  [2] 🎓 research-orchestrator  · academic / peer-reviewed evidence
  [3] 📰 last30days             · last {DAYS}-day community pulse

Est: 3 parallel research passes. This is the thorough path.
```

Then, unless `--yes`/`--fast` was passed, STOP and ask one line:
`Proceed with all 3 arms, or refine scope (drop an arm / narrow the topic)?`
Wait for the go-ahead. This gate is the deep-research-style step - do not skip it
unless the flag is set. If the user narrows, update the plan card and re-show.

---

## PHASE 1 - Dispatch the arms (parallel) with a live progress tree

Announce the phase, then launch all selected arms in a SINGLE message (one `Task`
call per arm, so they run concurrently). Immediately render the progress tree and
update it as each arm returns:

```
Phase 1/3 · Researching ({k} arms in parallel)
  🌐 deep-research         ▶ running
  🎓 research-orchestrator  ▶ running
  📰 last30days             ▶ running
```

(As results land, reprint the tree with `✓ done ({1-line headline})` or
`✗ failed ({reason}, used fallback)` per arm.)

Each sub-agent (general-purpose) is told to invoke its skill via the `Skill` tool
and return ONLY its final synthesis, not raw logs:

**Arm 1 — 🌐 deep-research (web, verified):**
> Use the `deep-research` skill to produce a fact-checked, cited report on:
> "{TOPIC}". Return the verified key claims (each with its source link and a
> note on how well it survived verification), plus any claims that failed
> verification. Synthesis only.
> Fallback if the skill is unavailable: run 4-6 `WebSearch` queries, `WebFetch`
> the best sources, and for each major claim run one adversarial check ("what
> would refute this?") before including it. Say you used the fallback.

**Arm 2 — 🎓 research-orchestrator (academic):**
> Use the `research-orchestrator` skill for an evidence-based literature
> synthesis on: "{TOPIC}". Return the top evidence-backed recommendations, each
> with a confidence level and 1-2 key citations, plus any contested findings.
> Synthesis only.
> Fallback: spawn your own academic searches (Google Scholar, arXiv, etc.),
> read the top sources, synthesize with confidence levels. Say you used it.

**Arm 3 — 📰 last30days (social):**
> Use the `last30days` skill to research "{TOPIC}"{ --days=N if set}. Return its
> full "What I learned" synthesis, the KEY PATTERNS list, and the engine
> emoji-tree stats footer verbatim. No Sources block. Report only.
> Fallback: run its engine `scripts/last30days.py` directly. Say you used it.

For a single-arm `--arms=` run, skip the Task fan-out, invoke that one skill
directly, and present its report under its own heading (skip PHASE 2 merge).

---

## PHASE 2 - Triangulate (the merge is the deliverable)

Announce `Phase 2/3 · Triangulating`. Read all returned arms. Do NOT staple them
together. Cross-validate claim-by-claim and write:

```
# Full Research: {TOPIC}

## TL;DR
- 3-5 bullets that answer the question. Tag each [all-3] / [web] / [academic] / [social] / [2-of-3].

## ✅ Confirmed by all three (highest confidence)
- {claim} - [web]({url}) + [academic citation] + [social source]. 

## ⚠️ Where the arms DIVERGE
- Web/fact-check says {A} ({url}); the literature says {B} ({citation}); the
  30-day community leans {C} ({social source}). Likely because {recency / incentive / sampling}.

## Evidence by arm
**🌐 Verified web:** {condensed deep-research claims + what failed verification}
**🎓 Academic:** {condensed research-orchestrator findings + confidence levels}
**📰 Community (last {DAYS}d):** {condensed last30days themes + engagement; include its emoji-tree footer verbatim}

## Confidence & gaps
- Rock-solid (all 3 agree): {...}
- Single-arm / unverified: {...}
- Recency caveat: academic may lag a shift the web/community already reflect.
- Verify next: {1-2 concrete checks}
```

Rules:
- Every "Confirmed by all three" bullet must actually cite all three arms.
- If only 2 arms ran (one dropped/failed), relabel that section "Confirmed by both"
  and say which arm is missing.

---

## PHASE 3 - Deliver + step summary

Print the report, then a compact run summary and 2-3 grounded follow-ups:

```
Phase 3/3 · Done
  🌐 deep-research        ✓   🎓 research-orchestrator ✓   📰 last30days ✓

Ask me to:
- Drill into the sharpest disagreement: {the divergence}
- Re-run the social arm fresher: /full-research {TOPIC} --arms=social --days=7
- Deep-read the top paper / source: {citation}
```

Stop and wait. No trailing Sources block (web + academic citations are inline;
social citations are in the emoji-tree footer).
