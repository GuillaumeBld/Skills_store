# Output Formats Reference

## Format Selection Guide

| Format | Best For | Token Cost |
|--------|----------|------------|
| **Prose** | Reports, sharing with non-technical audiences | Medium |
| **Structured** | Decision-making, comparison, audit trail | Medium |
| **Both** | Comprehensive analysis with flexibility | High |

## Prose Format

Natural language synthesis optimized for readability.

### Structure
1. **Lead**: Direct answer in first sentence
2. **Evidence**: Summary of supporting literature (2-3 paragraphs)
3. **Nuance**: Conflicts, caveats, context (1-2 paragraphs)
4. **Recommendation**: Clear action guidance
5. **Gaps**: What remains unknown

### Example Opening
> "The optimal approach to portfolio rebalancing depends heavily on transaction costs and tax implications. The literature generally supports calendar-based rebalancing at 12-month intervals for taxable accounts, while threshold-based approaches (5% bands) outperform in tax-advantaged accounts."

### Tone
- Direct, confident where evidence supports
- Appropriately hedged where evidence is mixed
- No unnecessary caveats or academic hedging
- Actionable language

## Structured Format

Tabular and sectioned output for systematic analysis.

### Required Sections

```markdown
## Summary
[2-3 sentences. Answer first.]

## Evidence Overview
| Topic | Papers | Consensus | Quality |
|-------|--------|-----------|---------|

## Options Analysis
### Option 1: [Name]
- **Description**: 
- **Supporting evidence**: 
- **Effect size**: 
- **Tradeoffs**: 

### Option 2: [Name]
...

## Recommendation
[Clear statement]
- **Confidence**: High/Medium/Low
- **Rationale**: 
- **Conditions**: When this applies
- **Alternatives**: When to deviate

## Risk Assessment
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|

## Assumptions
- [Assumption 1]
- [Assumption 2]

## Knowledge Gaps
- [Gap 1]
- [Gap 2]

## References
[Formatted citations]
```

## Both Format

Start with structured analysis, conclude with prose narrative.

### Structure
1. All structured sections (as above)
2. `## Narrative Summary` section at end
3. Prose synthesis (300-500 words)

## Citation Style

Use author-year inline: (Smith & Jones, 2023)

Full references at end:
```
Smith, A., & Jones, B. (2023). Paper Title. Journal Name, 45(2), 123-145.
```

For working papers:
```
Smith, A. (2024). Paper Title. NBER Working Paper No. 12345.
```
