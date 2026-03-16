---
name: influencer-assign
description: "Use this when a product brief needs to be matched to the right UGC MADA influencers. Scores each influencer against the brief's target niche, tone, and audience, and outputs an assignment with reasoning."
---

# Influencer Assignment

Match a validated product brief to the best-fit virtual influencers from the fleet. Assignment must be based on niche alignment, tone compatibility, and audience overlap — not just availability.

## Inputs

- Validated brief: `campaigns/<brand>-<date>/brief.json`
- Influencer fleet: `agency_config.json` (6 influencers with niche, tone, accounts)
- Historical performance: `campaigns/*/status.json` (if available)

## Scoring Matrix

For each influencer, score 1-5 on:

| Dimension | Weight | Description |
|---|---|---|
| Niche match | 40% | Does the influencer's content niche align with the product category? |
| Tone match | 30% | Does the influencer's tone (humor/aspirational/lifestyle) fit the brief's tone requirement? |
| Audience overlap | 20% | Does the influencer's target demographic match the brief's target? |
| Past performance | 10% | Has this influencer performed well on similar product types? |

Weighted score = (niche×0.4) + (tone×0.3) + (audience×0.2) + (performance×0.1)

## Assignment Rules

- Minimum score threshold: **3.5 / 5** to be assigned
- Maximum influencers per campaign: **3** (avoid brand saturation across the fleet)
- If requested influencers score below threshold, flag it and recommend alternatives
- Never assign the same influencer to more than 2 active campaigns simultaneously

## Output

Append to `campaigns/<brand>-<date>/brief.json`:

```json
"assignment": {
  "assigned": ["influencer_2", "influencer_5"],
  "scores": {
    "influencer_2": { "total": 4.3, "niche": 5, "tone": 4, "audience": 4, "performance": 3 },
    "influencer_5": { "total": 3.9, "niche": 4, "tone": 4, "audience": 4, "performance": 3 }
  },
  "reasoning": "string — why these influencers, not others",
  "conflicts": [] 
}
```
