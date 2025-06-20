# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Nishith Desai Associates (NDA) Search Engine

This engine searches through Nishith Desai Associates' extensive legal research
database, articles, hotlines, and other legal content. NDA is Asia's most 
innovative law firm with a strong focus on research-driven legal practice.

Website: https://www.nishithdesai.com
API: No official API - uses web scraping
Categories: Legal research, articles, hotlines, reports
"""

import re
from urllib.parse import urlencode, urlparse, parse_qs
from lxml import html
from searx.result_types import EngineResults
from searx.utils import extract_text, eval_xpath_getindex

# Engine configuration
engine_type = 'online'
categories = ['law']
paging = True
max_page = 10
send_accept_language_header = True
time_range_support = False
safesearch = False

# Engine metadata
about = {
    "website": 'https://www.nishithdesai.com',
    "wikidata_id": 'Q67007071',  # Nishith Desai Associates Wikidata ID
    "official_api_documentation": None,
    "use_official_api": False,
    "require_api_key": False,
    "results": 'HTML',
    "description": "Search legal research, articles, and insights from Asia's most innovative law firm - Nishith Desai Associates",
    "language": 'en'
}

# Search configurations
base_url = 'https://www.nishithdesai.com'
search_url = base_url + '/Search.html'

# Headers to mimic a real browser
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}


def request(query, params):
    """Build the search request URL and parameters."""
    
    # Remove any leading/trailing whitespace and normalize the query
    query = query.strip()
    
    # Build search parameters
    search_params = {
        'q': query,
        'searchtext': query,
        'page': params.get('pageno', 1),
        'results': 20,  # Results per page
    }
    
    # Construct the full search URL
    params['url'] = search_url + '?' + urlencode(search_params)
    params['method'] = 'GET'
    params['headers'] = headers
    
    return params


def response(resp) -> EngineResults:
    """Parse search results from Nishith Desai Associates website."""
    
    res = EngineResults()
    
    try:
        # Parse the HTML response
        dom = html.fromstring(resp.text)
        
        # Multiple potential selectors for search results
        # NDA might use different layouts for different content types
        result_selectors = [
            '//div[contains(@class, "search-result")]',
            '//div[contains(@class, "result")]',
            '//div[contains(@class, "article")]',
            '//div[contains(@class, "hotline")]',
            '//div[contains(@class, "news")]',
            '//div[contains(@class, "content-item")]',
            '//article',
            '//div[contains(@class, "list-item")]'
        ]
        
        results = []
        for selector in result_selectors:
            results = eval_xpath(dom, selector)
            if results:
                break
        
        # If no specific result containers found, try to find links with content
        if not results:
            results = eval_xpath(dom, '//a[contains(@href, "/")]')
        
        for result in results:
            try:
                # Extract title
                title_selectors = [
                    './/h1/text()',
                    './/h2/text()',
                    './/h3/text()',
                    './/h4/text()',
                    './/a/text()',
                    './/strong/text()',
                    './/span[@class="title"]/text()',
                    './/div[@class="title"]/text()'
                ]
                
                title = None
                for title_sel in title_selectors:
                    title_elements = eval_xpath(result, title_sel)
                    if title_elements:
                        title = title_elements[0].strip()
                        break
                
                if not title or len(title) < 5:
                    continue
                
                # Extract URL
                url_selectors = [
                    './/a/@href',
                    './/@href'
                ]
                
                url = None
                for url_sel in url_selectors:
                    url_elements = eval_xpath(result, url_sel)
                    if url_elements:
                        url = url_elements[0]
                        break
                
                if not url:
                    continue
                
                # Normalize URL
                if url.startswith('/'):
                    url = base_url + url
                elif not url.startswith('http'):
                    url = base_url + '/' + url
                
                # Extract content/description
                content_selectors = [
                    './/p/text()',
                    './/div[@class="content"]/text()',
                    './/div[@class="description"]/text()',
                    './/div[@class="excerpt"]/text()',
                    './/span[@class="snippet"]/text()',
                    './/text()'
                ]
                
                content = ""
                for content_sel in content_selectors:
                    content_elements = eval_xpath(result, content_sel)
                    if content_elements:
                        content = ' '.join([text.strip() for text in content_elements[:3] if text.strip()])
                        break
                
                # Clean up content
                content = re.sub(r'\s+', ' ', content).strip()
                if len(content) > 300:
                    content = content[:297] + "..."
                
                # Determine content type and category
                url_lower = url.lower()
                if 'hotline' in url_lower:
                    content_type = 'Legal Hotline'
                elif 'research' in url_lower or 'article' in url_lower:
                    content_type = 'Research Article'
                elif 'news' in url_lower:
                    content_type = 'News'
                elif '.pdf' in url_lower:
                    content_type = 'PDF Document'
                    res.add(
                        res.types.File(
                            url=url,
                            title=title,
                            content=content,
                            template='files.html'
                        )
                    )
                    continue
                else:
                    content_type = 'Legal Content'
                
                # Add prefix to title to indicate content type
                formatted_title = f"[{content_type}] {title}"
                
                # Add search result
                res.add(
                    res.types.Link(
                        url=url,
                        title=formatted_title,
                        content=content
                    )
                )
                
            except Exception as e:
                # Continue processing other results if one fails
                continue
        
        # If we didn't find any results with the above methods,
        # try a more aggressive text-based approach
        if len(res.results) == 0:
            # Look for any links that contain the search terms
            all_links = eval_xpath(dom, '//a[@href]')
            
            for link in all_links:
                try:
                    href = eval_xpath_getindex(link, './@href', 0, None)
                    link_text = extract_text(link)
                    
                    if (href and link_text and 
                        len(link_text.strip()) > 10 and
                        not href.startswith('#') and
                        not href.startswith('javascript:') and
                        not href.startswith('mailto:')):
                        
                        # Normalize URL
                        if href.startswith('/'):
                            href = base_url + href
                        elif not href.startswith('http'):
                            href = base_url + '/' + href
                        
                        res.add(
                            res.types.Link(
                                url=href,
                                title=link_text.strip(),
                                content="Content from Nishith Desai Associates"
                            )
                        )
                        
                        # Limit fallback results
                        if len(res.results) >= 10:
                            break
                            
                except Exception:
                    continue
    
    except Exception as e:
        # If parsing fails completely, return empty results
        pass
    
    return res


def eval_xpath(element, xpath_expr):
    """Helper function to safely evaluate XPath expressions."""
    try:
        return element.xpath(xpath_expr)
    except Exception:
        return []


# Optional: Engine initialization function
def init(engine_settings):
    """Initialize the engine if needed."""
    pass


# Optional: Fetch engine traits for better localization support
def fetch_traits(engine_traits):
    """Fetch traits to improve engine capabilities."""
    # NDA is primarily English content, India-focused
    engine_traits.all_locale = 'en-IN'
    engine_traits.languages['en'] = 'English'
    engine_traits.regions['IN'] = 'India'
    engine_traits.regions['US'] = 'United States'  # International practice
    
    return engine_traits