"""
Web Tools MCP Server
Web scraping, URL operations, and HTTP utilities
"""
import os
import re
import requests
from typing import Dict, List
from urllib.parse import urlparse, urljoin
from mcp.server.fastmcp import FastMCP

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

port = int(os.getenv("PORT", 8004))
mcp = FastMCP("web_tools", host="0.0.0.0", port=port)


@mcp.tool()
def fetch_webpage(url: str, timeout: int = 10) -> Dict:
    """
    Fetch the content of a webpage.
    
    Use this to retrieve HTML content, check page accessibility, or download web pages.
    
    Args:
        url: The URL to fetch
        timeout: Request timeout in seconds (default: 10)
    
    Returns:
        Dictionary with status_code, content, headers, and metadata
    """
    try:
        response = requests.get(url, timeout=timeout, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        return {
            'success': True,
            'status_code': response.status_code,
            'url': response.url,
            'content': response.text[:10000],  # Limit to first 10k chars
            'content_length': len(response.text),
            'encoding': response.encoding,
            'headers': dict(response.headers)
        }
        
    except requests.exceptions.Timeout:
        return {'success': False, 'error': 'Request timed out'}
    except requests.exceptions.RequestException as e:
        return {'success': False, 'error': str(e)}


@mcp.tool()
def check_url_status(url: str, timeout: int = 5) -> Dict:
    """
    Check if a URL is accessible and get its HTTP status.
    
    Use this to verify links, check website availability, or validate URLs before processing.
    
    Args:
        url: The URL to check
        timeout: Request timeout in seconds (default: 5)
    
    Returns:
        Dictionary with status_code, accessible status, and response time
    """
    try:
        import time
        start_time = time.time()
        
        response = requests.head(url, timeout=timeout, allow_redirects=True, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        response_time = time.time() - start_time
        
        return {
            'url': url,
            'accessible': True,
            'status_code': response.status_code,
            'status_message': response.reason,
            'response_time_seconds': round(response_time, 3),
            'final_url': response.url,
            'redirected': response.url != url
        }
        
    except requests.exceptions.Timeout:
        return {'url': url, 'accessible': False, 'error': 'Timeout'}
    except requests.exceptions.RequestException as e:
        return {'url': url, 'accessible': False, 'error': str(e)}


@mcp.tool()
def extract_links(url: str, filter_external: bool = False) -> Dict:
    """
    Extract all links from a webpage.
    
    Use this to discover page structure, find related pages, or build web crawlers.
    
    Args:
        url: The webpage URL to extract links from
        filter_external: If True, only return links from the same domain (default: False)
    
    Returns:
        Dictionary with lists of internal and external links
    """
    if not BeautifulSoup:
        return {'error': 'BeautifulSoup4 library not installed'}
    
    try:
        response = requests.get(url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        soup = BeautifulSoup(response.text, 'html.parser')
        
        base_domain = urlparse(url).netloc
        internal_links = []
        external_links = []
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            absolute_url = urljoin(url, href)
            
            # Parse the link
            parsed = urlparse(absolute_url)
            
            if parsed.netloc == base_domain or not parsed.netloc:
                internal_links.append(absolute_url)
            else:
                external_links.append(absolute_url)
        
        result = {
            'url': url,
            'total_links': len(internal_links) + len(external_links),
            'internal_links': list(set(internal_links)),
            'external_links': list(set(external_links))
        }
        
        if filter_external:
            result['links'] = result['internal_links']
        
        return result
        
    except Exception as e:
        return {'error': f'Failed to extract links: {str(e)}'}


@mcp.tool()
def scrape_webpage(url: str, css_selector: str = None) -> Dict:
    """
    Scrape specific content from a webpage using CSS selectors.
    
    Use this to extract structured data, parse specific elements, or collect information
    from web pages. If no selector provided, returns page title and main text.
    
    Args:
        url: The webpage URL to scrape
        css_selector: CSS selector to target specific elements (optional)
    
    Returns:
        Dictionary with scraped content
    """
    if not BeautifulSoup:
        return {'error': 'BeautifulSoup4 library not installed'}
    
    try:
        response = requests.get(url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        soup = BeautifulSoup(response.text, 'html.parser')
        
        if css_selector:
            # Scrape specific elements
            elements = soup.select(css_selector)
            results = []
            
            for elem in elements[:50]:  # Limit to 50 elements
                results.append({
                    'text': elem.get_text(strip=True),
                    'html': str(elem)[:500]  # Limit HTML length
                })
            
            return {
                'url': url,
                'selector': css_selector,
                'count': len(results),
                'elements': results
            }
        else:
            # Default: get title and main content
            title = soup.title.string if soup.title else 'No title'
            
            # Remove script and style elements
            for script in soup(['script', 'style']):
                script.decompose()
            
            text = soup.get_text(separator='\n', strip=True)
            
            return {
                'url': url,
                'title': title,
                'text': text[:5000],  # Limit to first 5000 chars
                'text_length': len(text)
            }
        
    except Exception as e:
        return {'error': f'Failed to scrape webpage: {str(e)}'}


@mcp.tool()
def extract_metadata(url: str) -> Dict:
    """
    Extract metadata from a webpage (title, description, Open Graph tags, etc.).
    
    Use this to get page information for previews, SEO analysis, or content categorization.
    
    Args:
        url: The webpage URL to analyze
    
    Returns:
        Dictionary with page title, description, and meta tags
    """
    if not BeautifulSoup:
        return {'error': 'BeautifulSoup4 library not installed'}
    
    try:
        response = requests.get(url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        soup = BeautifulSoup(response.text, 'html.parser')
        
        metadata = {
            'url': url,
            'title': soup.title.string if soup.title else None,
            'description': None,
            'keywords': None,
            'author': None,
            'og_title': None,
            'og_description': None,
            'og_image': None
        }
        
        # Meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            metadata['description'] = meta_desc.get('content')
        
        # Meta keywords
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        if meta_keywords:
            metadata['keywords'] = meta_keywords.get('content')
        
        # Author
        meta_author = soup.find('meta', attrs={'name': 'author'})
        if meta_author:
            metadata['author'] = meta_author.get('content')
        
        # Open Graph tags
        og_title = soup.find('meta', property='og:title')
        if og_title:
            metadata['og_title'] = og_title.get('content')
        
        og_desc = soup.find('meta', property='og:description')
        if og_desc:
            metadata['og_description'] = og_desc.get('content')
        
        og_image = soup.find('meta', property='og:image')
        if og_image:
            metadata['og_image'] = og_image.get('content')
        
        return metadata
        
    except Exception as e:
        return {'error': f'Failed to extract metadata: {str(e)}'}


@mcp.tool()
def parse_url(url: str) -> Dict:
    """
    Parse a URL into its components (scheme, domain, path, query, etc.).
    
    Use this to analyze URLs, extract parameters, or validate URL structure.
    
    Args:
        url: The URL to parse
    
    Returns:
        Dictionary with URL components
    """
    try:
        parsed = urlparse(url)
        
        # Parse query parameters
        query_params = {}
        if parsed.query:
            for param in parsed.query.split('&'):
                if '=' in param:
                    key, value = param.split('=', 1)
                    query_params[key] = value
        
        return {
            'url': url,
            'scheme': parsed.scheme,
            'domain': parsed.netloc,
            'path': parsed.path,
            'query': parsed.query,
            'query_params': query_params,
            'fragment': parsed.fragment,
            'is_secure': parsed.scheme == 'https'
        }
        
    except Exception as e:
        return {'error': f'Failed to parse URL: {str(e)}'}


@mcp.tool()
def download_file_info(url: str) -> Dict:
    """
    Get information about a downloadable file without downloading it.
    
    Use this to check file size, type, and availability before downloading.
    
    Args:
        url: The file URL
    
    Returns:
        Dictionary with file size, content type, and availability
    """
    try:
        response = requests.head(url, timeout=10, allow_redirects=True, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        content_length = response.headers.get('Content-Length')
        content_type = response.headers.get('Content-Type')
        
        return {
            'url': url,
            'accessible': response.status_code == 200,
            'status_code': response.status_code,
            'content_type': content_type,
            'file_size_bytes': int(content_length) if content_length else None,
            'file_size_mb': round(int(content_length) / (1024 * 1024), 2) if content_length else None,
            'final_url': response.url
        }
        
    except Exception as e:
        return {'error': f'Failed to get file info: {str(e)}'}


@mcp.tool()
def check_multiple_urls(urls: List[str], timeout: int = 5) -> List[Dict]:
    """
    Check the status of multiple URLs at once.
    
    Use this to validate multiple links, check site availability, or audit URL lists.
    
    Args:
        urls: List of URLs to check
        timeout: Timeout per URL in seconds (default: 5)
    
    Returns:
        List of dictionaries with status for each URL
    """
    results = []
    
    for url in urls[:50]:  # Limit to 50 URLs
        try:
            response = requests.head(url, timeout=timeout, allow_redirects=True, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            results.append({
                'url': url,
                'accessible': True,
                'status_code': response.status_code
            })
        except:
            results.append({
                'url': url,
                'accessible': False,
                'status_code': None
            })
    
    return results


if __name__ == "__main__":
    print(f"Starting Web Tools MCP Server on port {port}...")
    print("Available tools: fetch_webpage, check_url_status, extract_links,")
    print("                 scrape_webpage, extract_metadata, parse_url,")
    print("                 download_file_info, check_multiple_urls")
    mcp.run()
