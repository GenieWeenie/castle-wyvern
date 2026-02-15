"""
Browser Agent for Castle Wyvern
Autonomous web browsing and search capabilities
"""

import requests
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse
import time
import re


@dataclass
class WebPage:
    """Represents a scraped web page."""
    url: str
    title: str
    content: str
    links: List[str]
    timestamp: float


class BrowserAgent:
    """
    Autonomous web browsing agent.
    
    Capabilities:
    - Navigate to URLs
    - Search the web (DuckDuckGo)
    - Extract page content
    - Follow links
    - Summarize findings
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.history: List[WebPage] = []
        self.max_content_length = 10000
        
    def search(self, query: str, num_results: int = 5) -> List[Dict[str, str]]:
        """
        Search the web using DuckDuckGo.
        
        Args:
            query: Search query
            num_results: Number of results to return
            
        Returns:
            List of search results with title, url, snippet
        """
        try:
            # DuckDuckGo HTML interface (no API key needed)
            url = "https://html.duckduckgo.com/html/"
            params = {'q': query}
            
            response = self.session.post(url, data=params, timeout=10)
            response.raise_for_status()
            
            # Parse results (simple regex-based parsing)
            results = []
            
            # Find result blocks
            result_blocks = re.findall(
                r'<a rel="nofollow" class="result__a" href="([^"]+)">([^<]+)</a>.*?<a class="result__snippet"[^>]*>([^<]+)</a>',
                response.text,
                re.DOTALL
            )
            
            for i, (link, title, snippet) in enumerate(result_blocks[:num_results]):
                # Clean up HTML entities
                title = self._clean_html(title)
                snippet = self._clean_html(snippet)
                
                results.append({
                    'title': title,
                    'url': link,
                    'snippet': snippet
                })
            
            return results
            
        except Exception as e:
            return [{'title': 'Search Error', 'url': '', 'snippet': f'Failed to search: {str(e)}'}]
    
    def fetch(self, url: str) -> WebPage:
        """
        Fetch and parse a web page.
        
        Args:
            url: URL to fetch
            
        Returns:
            WebPage object with content
        """
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            html = response.text
            
            # Extract title
            title_match = re.search(r'<title[^>]*>([^<]+)</title>', html, re.IGNORECASE)
            title = title_match.group(1).strip() if title_match else 'No Title'
            
            # Extract content (remove scripts, styles)
            content = self._extract_text(html)
            
            # Extract links
            links = self._extract_links(html, url)
            
            page = WebPage(
                url=url,
                title=title,
                content=content[:self.max_content_length],
                links=links[:20],  # Limit links
                timestamp=time.time()
            )
            
            self.history.append(page)
            return page
            
        except Exception as e:
            return WebPage(
                url=url,
                title='Error',
                content=f'Failed to fetch page: {str(e)}',
                links=[],
                timestamp=time.time()
            )
    
    def research(self, query: str, depth: int = 2) -> str:
        """
        Deep research on a topic.
        
        Args:
            query: Research topic
            depth: How many pages to visit (1-3 recommended)
            
        Returns:
            Summarized research findings
        """
        # Search first
        results = self.search(query, num_results=depth)
        
        if not results or 'Error' in results[0].get('title', ''):
            return f"Could not research '{query}': Search failed"
        
        # Fetch top results
        findings = []
        for result in results[:depth]:
            if result.get('url'):
                page = self.fetch(result['url'])
                findings.append({
                    'title': page.title,
                    'url': page.url,
                    'summary': page.content[:500] + '...' if len(page.content) > 500 else page.content
                })
        
        # Compile research report
        report = f"# Research: {query}\n\n"
        for i, finding in enumerate(findings, 1):
            report += f"## {i}. {finding['title']}\n"
            report += f"**URL:** {finding['url']}\n\n"
            report += f"{finding['summary']}\n\n"
        
        report += f"\n---\n*Researched {len(findings)} sources*"
        return report
    
    def _extract_text(self, html: str) -> str:
        """Extract readable text from HTML."""
        # Remove script and style tags
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove common non-content tags
        for tag in ['nav', 'header', 'footer', 'aside', 'noscript']:
            html = re.sub(rf'<{tag}[^>]*>.*?</{tag}>', '', html, flags=re.DOTALL | re.IGNORECASE)
        
        # Extract text from paragraphs and divs
        text_parts = re.findall(r'<p[^>]*>([^<]+)</p>', html, re.IGNORECASE)
        text_parts += re.findall(r'<div[^>]*>([^<]+)</div>', html, re.IGNORECASE)
        
        # Also get text from li items (lists)
        text_parts += re.findall(r'<li[^>]*>([^<]+)</li>', html, re.IGNORECASE)
        
        # Clean up
        text = ' '.join(text_parts)
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text[:self.max_content_length]
    
    def _extract_links(self, html: str, base_url: str) -> List[str]:
        """Extract links from HTML."""
        links = []
        for match in re.finditer(r'href="([^"]+)"', html):
            href = match.group(1)
            # Skip anchors, javascript, mailto
            if href.startswith(('#', 'javascript:', 'mailto:', 'tel:')):
                continue
            # Convert relative to absolute
            absolute = urljoin(base_url, href)
            links.append(absolute)
        return list(set(links))  # Remove duplicates
    
    def _clean_html(self, text: str) -> str:
        """Clean HTML entities from text."""
        replacements = {
            '&quot;': '"',
            '&amp;': '&',
            '&lt;': '<',
            '&gt;': '>',
            '&#39;': "'",
            '&nbsp;': ' ',
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        return text.strip()
    
    def get_history(self) -> List[WebPage]:
        """Get browsing history."""
        return self.history
    
    def clear_history(self):
        """Clear browsing history."""
        self.history = []


# Standalone usage
if __name__ == "__main__":
    browser = BrowserAgent()
    
    # Example: Search
    print("Searching for 'Python programming'...")
    results = browser.search("Python programming", num_results=3)
    for r in results:
        print(f"\n{r['title']}")
        print(f"  {r['url']}")
        print(f"  {r['snippet'][:100]}...")
