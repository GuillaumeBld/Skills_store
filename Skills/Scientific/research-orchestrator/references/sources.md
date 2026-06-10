# Research Sources Registry

## Open Access Sources

### Google Scholar
- **URL**: https://scholar.google.com/scholar?q={query}
- **Access**: Free, no auth required
- **Strengths**: Broad coverage, citation counts, "cited by" links
- **Limitations**: No API, rate limiting, inconsistent metadata
- **Query tips**: Use quotes for exact phrases, `author:` prefix, `site:` for specific domains

### Semantic Scholar
- **URL**: https://www.semanticscholar.org/search?q={query}
- **API**: https://api.semanticscholar.org/graph/v1/paper/search?query={query}
- **Access**: Free, API available (rate limited)
- **Strengths**: AI-extracted citations, TLDR summaries, influence scores
- **Limitations**: Less comprehensive than Scholar for non-CS fields
- **Query tips**: Supports field filters: `fieldsOfStudy:Economics`

### SSRN (Social Science Research Network)
- **URL**: https://papers.ssrn.com/sol3/results.cfm?txtKey_Words={query}
- **Access**: Free abstracts, most full texts free
- **Strengths**: Working papers, finance/econ/law focus, early access to research
- **Limitations**: Quality varies (not peer-reviewed)
- **Query tips**: Filter by JEL codes for economics papers

### arXiv
- **URL**: https://arxiv.org/search/?query={query}
- **API**: https://export.arxiv.org/api/query?search_query={query}
- **Access**: Fully open
- **Strengths**: Preprints in physics, math, CS, econ (q-fin), stats
- **Limitations**: Not peer-reviewed
- **Query tips**: Use category filters (q-fin.PM for portfolio management)

### NBER (National Bureau of Economic Research)
- **URL**: https://www.nber.org/papers?page=1&perPage=50&q={query}
- **Access**: Free abstracts, full text for recent papers
- **Strengths**: High-quality economics working papers, influential authors
- **Limitations**: US-centric, abstracts-only for older papers without subscription
- **Query tips**: Filter by program (Corporate Finance, Asset Pricing, etc.)

### PubMed / PMC
- **URL**: https://pubmed.ncbi.nlm.nih.gov/?term={query}
- **API**: E-utilities available
- **Access**: Free abstracts, PMC has open access full texts
- **Strengths**: Definitive for biomedical research
- **Limitations**: Medical/bio focus only
- **Query tips**: Use MeSH terms for precision, filter by "Free full text"

### ResearchGate
- **URL**: https://www.researchgate.net/search/publication?q={query}
- **Access**: Free with account
- **Strengths**: Author-uploaded PDFs, direct author contact
- **Limitations**: Inconsistent coverage, requires login for some features

## Central Bank / Policy Sources

### Federal Reserve (FRED, working papers)
- **URL**: https://www.federalreserve.gov/econres/feds/index.htm
- **Access**: Fully open
- **Strengths**: Monetary policy, banking, financial stability
- **Query tips**: Check regional Fed sites (NY, St. Louis, etc.) for additional papers

### ECB Working Papers
- **URL**: https://www.ecb.europa.eu/pub/research/working-papers/html/index.en.html
- **Access**: Fully open
- **Strengths**: European monetary policy, banking supervision

### BIS (Bank for International Settlements)
- **URL**: https://www.bis.org/publ/work.htm
- **Access**: Fully open
- **Strengths**: International banking, financial regulation, systemic risk

### IMF Working Papers
- **URL**: https://www.imf.org/en/Publications/WP
- **Access**: Fully open
- **Strengths**: International finance, macro, development

## Institutional Access Sources

### JSTOR
- **URL**: https://www.jstor.org/action/doBasicSearch?Query={query}
- **Access**: Requires institutional subscription
- **Strengths**: Historical journal archives, humanities coverage
- **Workaround**: Many papers available via author websites or preprint servers

### ScienceDirect
- **URL**: https://www.sciencedirect.com/search?qs={query}
- **Access**: Requires institutional subscription
- **Strengths**: Elsevier journals, broad STEM coverage

## Domain Mapping

| Research Domain | Primary Sources | Secondary Sources |
|-----------------|-----------------|-------------------|
| Finance/Banking | SSRN, NBER, Fed, BIS | Scholar, Semantic |
| Economics | NBER, SSRN, Fed | Scholar, arXiv (q-fin) |
| Machine Learning | arXiv, Semantic Scholar | ACM DL, Scholar |
| Medical/Health | PubMed, Cochrane | Scholar |
| Statistics | arXiv (stat) | JSTOR, Scholar |
| General | Scholar, Semantic Scholar | ResearchGate |

## Access Priority

When fetching papers, try in this order:
1. Direct PDF link (if provided in search results)
2. arXiv/SSRN/PMC version (open access)
3. Author's personal website
4. ResearchGate upload
5. Flag as "requires institutional access" for user
