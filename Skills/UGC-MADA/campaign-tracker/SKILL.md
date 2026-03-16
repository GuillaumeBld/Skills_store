---
name: campaign-tracker
description: "Use this after a UGC campaign has been published to track performance, measure engagement, feed results back into the autoresearch loop, and determine whether to keep or revert the content strategy."
---

# Campaign Performance Tracker

Measure published campaign performance and feed results back into the Karpathy autoresearch loop. Good strategy advances. Poor strategy reverts.

## Tracking Schedule

For each published post, collect metrics at:
- **T+24h** — early signal (view velocity, comment sentiment)
- **T+72h** — engagement stabilization
- **T+7d** — final performance verdict

## Metrics to Collect

```json
{
  "post_url": "string",
  "influencer_id": "string",
  "platform": "TikTok | Instagram",
  "published_at": "ISO datetime",
  "campaign_id": "string",
  "metrics": {
    "views": number,
    "likes": number,
    "comments": number,
    "shares": number,
    "saves": number,
    "engagement_rate": "calculated: (likes+comments+shares+saves) / views",
    "completion_rate": "% of viewers who watched to end (TikTok only)"
  },
  "qualitative": {
    "top_comments": ["list of notable comments"],
    "sentiment": "positive | neutral | negative",
    "cringe_signals": "any comments calling out inauthenticity"
  }
}
```

## The Autoresearch Decision

After T+7d metrics are collected, apply the Karpathy rule:

```
If engagement_rate > baseline_for_this_influencer:
  → KEEP: commit CCO chain settings to results.tsv, advance branch
  → Note what worked: hook type, slang used, product integration style

If engagement_rate <= baseline:
  → REVERT: log to results.tsv with status 'discard'
  → git reset CCO prompt chain to previous version
  → Flag specific failure points for next iteration

If cringe_signals detected (comments calling out the ad):
  → CRITICAL REVERT regardless of engagement rate
  → Authenticity failure overrides all metrics
  → Mandatory CCO chain review before next campaign
```

## Baseline Calculation

Baseline = rolling average of last 5 organic posts for the same influencer. Updated after each campaign. Stored in `campaigns/baselines.json`.

## Output

Write to `campaigns/<brand>-<date>/performance.json` and append summary row to `campaigns/results.tsv`:

```
campaign_id\tbrand\tinfluencer\tengagement_rate\tbaseline\tstatus\tnotes
```
