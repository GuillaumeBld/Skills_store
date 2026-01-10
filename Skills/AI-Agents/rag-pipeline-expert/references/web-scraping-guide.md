# Web Scraping Implementation Guide

Complete patterns for web scraping in RAG pipelines. Refer to SKILL.md Phase 1 for tool selection framework.

## Pattern 1: Static Sites (httpx + BeautifulSoup)

Fast, lightweight scraping for HTML-only sites.

```python
import httpx
from bs4 import BeautifulSoup
from markdownify import markdownify as md

def scrape_static_page(url: str) -> dict:
    response = httpx.get(url, timeout=30, headers={'User-Agent': 'RAG-Bot/1.0'})
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Remove unwanted
    for tag in soup(['script', 'style', 'nav', 'footer']):
        tag.decompose()
    
    # Extract
    main = soup.find('main') or soup.find('article') or soup.body
    markdown = md(str(main), heading_style="ATX")
    
    return {
        'url': url,
        'title': soup.find('title').string if soup.find('title') else url,
        'markdown': markdown
    }
```

## Pattern 2: Dynamic Sites (Playwright)

For JavaScript-rendered content.

```python
from playwright.async_api import async_playwright

async def scrape_dynamic_page(url: str) -> dict:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, wait_until='networkidle')
        
        # Wait for content
        await page.wait_for_timeout(3000)
        
        # Extract
        content = await page.evaluate('''() => {
            document.querySelectorAll('script, style, nav, footer').forEach(el => el.remove());
            const main = document.querySelector('main') || document.body;
            return {
                html: main.innerHTML,
                title: document.title
            };
        }''')
        
        await browser.close()
        
        from markdownify import markdownify as md
        return {
            'url': url,
            'title': content['title'],
            'markdown': md(content['html'])
        }
```

## Pattern 3: Recursive Crawling

```python
from urllib.parse import urljoin, urlparse

class RecursiveScraper:
    def __init__(self, base_url: str, max_depth: int = 2):
        self.base_url = base_url
        self.max_depth = max_depth
        self.visited = set()
    
    def crawl(self, url: str, depth: int = 0) -> list:
        if depth > self.max_depth or url in self.visited:
            return []
        
        self.visited.add(url)
        results = [scrape_static_page(url)]
        
        if depth < self.max_depth:
            soup = BeautifulSoup(httpx.get(url).text, 'html.parser')
            for link in soup.find_all('a', href=True):
                next_url = urljoin(url, link['href'])
                if urlparse(next_url).netloc == urlparse(self.base_url).netloc:
                    results.extend(self.crawl(next_url, depth + 1))
        
        return results
```

## n8n HTTP Request Node

```json
{
  "parameters": {
    "url": "={{ $json.url }}",
    "options": {
      "timeout": 30000
    },
    "headerParameters": {
      "parameters": [{"name": "User-Agent", "value": "RAG-Bot/1.0"}]
    }
  },
  "type": "n8n-nodes-base.httpRequest"
}
```

## Robots.txt Compliance

```python
from urllib.robotparser import RobotFileParser

def can_scrape(url: str) -> bool:
    rp = RobotFileParser()
    rp.set_url(urljoin(url, '/robots.txt'))
    rp.read()
    return rp.can_fetch('*', url)
```

## Error Handling

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=10))
def fetch_with_retry(url: str) -> str:
    response = httpx.get(url, timeout=30)
    response.raise_for_status()
    return response.text
```
