---
name: product-brief
description: "Use this when a brand or product needs to be marketed through UGC MADA influencers. Validates the brief, scores cultural fit, checks for authenticity risks, and prepares the input package for the CCO pipeline."
---

# Product Brief Intake & Validation

Process an incoming brand brief into a validated, structured package ready for the CCO pipeline. A brief that fails cultural fit or has authenticity risks must be flagged before any content is generated.

## Brief Schema

Every product brief must conform to this structure:

```json
{
  "brand": "string — brand name",
  "product": "string — specific product name",
  "key_message": "string — the core claim or feeling to convey (max 20 words)",
  "assets": ["list of image/video file paths or URLs"],
  "target": {
    "age": "string — e.g. 18-35",
    "niche": "string — e.g. food/humor, lifestyle, travel",
    "commune": "string — e.g. 'all', 'Fort-de-France', 'Sainte-Anne'"
  },
  "tone": "string — e.g. 'proud and warm, not touristy'",
  "do_not": ["list of hard constraints — things the content must never do or say"],
  "influencers": ["list of influencer IDs from agency_config.json"],
  "posts": "number — total posts requested",
  "deadline": "ISO date string",
  "budget_tier": "string — nano / micro / standard / premium"
}
```

## Checklist

1. **Parse the brief** — extract all fields, flag any missing required fields
2. **Cultural fit score** — rate 1-10: does this product/brand have a natural place in Martinican daily life? Reference Martinique_DB if available
3. **Authenticity risk check** — would this read as a paid ad to a Martinican audience? Flag high-risk key messages
4. **Do-not audit** — are the constraints specific enough? Vague constraints (e.g. 'be authentic') must be clarified into actionable rules
5. **Influencer match** — verify requested influencers' niches align with target. Suggest alternatives if mismatched
6. **Asset review** — confirm assets exist and are usable (no watermarks, correct format for short-form video)
7. **Output validated brief** — write to `campaigns/<brand>-<date>/brief.json`
8. **Gate** — only proceed to cco-pipeline skill if cultural fit score ≥ 6 and no critical authenticity risks

## Cultural Fit Scoring Guide

| Score | Meaning |
|---|---|
| 9-10 | Product is already part of Martinican culture (rhum, local food, local events) |
| 7-8 | Product fits naturally into daily life with the right framing |
| 5-6 | Possible but requires creative work to avoid feeling foreign |
| 3-4 | High risk of feeling like mainland French or American advertising |
| 1-2 | Product has no cultural anchor in Martinique — reject or request significant repositioning |

## Authenticity Risk Signals

Flag immediately if the key message or do-not list contains:
- Generic tropical/exotic framing ("paradise", "island escape", "under the sun")
- No local reference point (could apply to any French territory)
- Overly formal French that no Martinican would use in a caption
- Pressure to mention price or discount prominently

## Output Format

Write validated brief + scores to `campaigns/<brand>-<YYYY-MM-DD>/brief.json`. Include:
- All original fields
- `cultural_fit_score`: number
- `authenticity_risk`: low / medium / high
- `validation_notes`: string
- `status`: "validated" | "needs_revision" | "rejected"
