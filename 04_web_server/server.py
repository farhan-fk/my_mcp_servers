"""
Web Tools REST API Server
Web scraping, URL operations, and HTTP utilities
"""
import os
import re
import requests
from typing import Dict, List
from urllib.parse import urlparse, urljoin
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import time

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

port = int(os.getenv("PORT", 8000))
app = FastAPI(title="Web Tools API", version="1.0")


# Request Models
class FetchWebpageRequest(BaseModel):
    url: str
    timeout: int = 10

class URLRequest(BaseModel):
    url: str
    timeout: int = 5

class ExtractLinksRequest(BaseModel):
    url: str
    filter_external: bool = False

class ScrapeWebpageRequest(BaseModel):
    url: str
    css_selector: str = None

class CheckMultipleURLsRequest(BaseModel):
    urls: List[str]
    timeout: int = 5


@app.get("/")
async def root():
    return {
        "service": "Web Tools API",
        "version": "1.0",
        "tools": [
            "fetch_webpage", "check_url_status", "extract_links",
            "scrape_webpage", "extract_metadata", "parse_url",
            "download_file_info", "check_multiple_urls"
        ]
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/tools/fetch_webpage")
async def fetch_webpage(request: FetchWebpageRequest) -> Dict:
    """Fetch the content of a webpage."""
    try:
        response = requests.get(request.url, timeout=request.timeout, headers={
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


@app.post("/tools/check_url_status")
async def check_url_status(request: URLRequest) -> Dict:
    """Check if a URL is accessible and get its HTTP status."""
    try:
        start_time = time.time()
        
        response = requests.head(request.url, timeout=request.timeout, allow_redirects=True, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        response_time = time.time() - start_time
        
        return {
            'url': request.url,
            'accessible': True,
            'status_code': response.status_code,
            'status_message': response.reason,
            'response_time_seconds': round(response_time, 3),
            'final_url': response.url,
            'redirected': response.url != request.url
        }
        
    except requests.exceptions.Timeout:
        return {'url': request.url, 'accessible': False, 'error': 'Timeout'}
    except requests.exceptions.RequestException as e:
        return {'url': request.url, 'accessible': False, 'error': str(e)}


@app.post("/tools/extract_links")
async def extract_links(request: ExtractLinksRequest) -> Dict:
    """Extract all links from a webpage."""
    if not BeautifulSoup:
        raise HTTPException(status_code=500, detail='BeautifulSoup4 library not installed')
    
    try:
        response = requests.get(request.url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        soup = BeautifulSoup(response.text, 'html.parser')
        
        base_domain = urlparse(request.url).netloc
        internal_links = []
        external_links = []
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            absolute_url = urljoin(request.url, href)
            
            # Parse the link
            parsed = urlparse(absolute_url)
            
            if parsed.netloc == base_domain or not parsed.netloc:
                internal_links.append(absolute_url)
            else:
                external_links.append(absolute_url)
        
        result = {
            'url': request.url,
            'total_links': len(internal_links) + len(external_links),
            'internal_links': list(set(internal_links)),
            'external_links': list(set(external_links))
        }
        
        if request.filter_external:
            result['links'] = result['internal_links']
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Failed to extract links: {str(e)}')


@app.post("/tools/scrape_webpage")
async def scrape_webpage(request: ScrapeWebpageRequest) -> Dict:
    """Scrape specific content from a webpage using CSS selectors."""
    if not BeautifulSoup:
        raise HTTPException(status_code=500, detail='BeautifulSoup4 library not installed')
    
    try:
        response = requests.get(request.url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        soup = BeautifulSoup(response.text, 'html.parser')
        
        if request.css_selector:
            # Scrape specific elements
            elements = soup.select(request.css_selector)
            results = []
            
            for elem in elements[:50]:  # Limit to 50 elements
                results.append({
                    'text': elem.get_text(strip=True),
                    'html': str(elem)[:500]  # Limit HTML length
                })
            
            return {
                'url': request.url,
                'selector': request.css_selector,
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
                'url': request.url,
                'title': title,
                'text': text[:5000],  # Limit to first 5000 chars
                'text_length': len(text)
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Failed to scrape webpage: {str(e)}')


@app.post("/tools/extract_metadata")
async def extract_metadata(request: URLRequest) -> Dict:
    """Extract metadata from a webpage (title, description, Open Graph tags, etc.)."""
    if not BeautifulSoup:
        raise HTTPException(status_code=500, detail='BeautifulSoup4 library not installed')
    
    try:
        response = requests.get(request.url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        soup = BeautifulSoup(response.text, 'html.parser')
        
        metadata = {
            'url': request.url,
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
        raise HTTPException(status_code=500, detail=f'Failed to extract metadata: {str(e)}')


@app.post("/tools/parse_url")
async def parse_url(request: URLRequest) -> Dict:
    """Parse a URL into its components (scheme, domain, path, query, etc.)."""
    try:
        parsed = urlparse(request.url)
        
        # Parse query parameters
        query_params = {}
        if parsed.query:
            for param in parsed.query.split('&'):
                if '=' in param:
                    key, value = param.split('=', 1)
                    query_params[key] = value
        
        return {
            'url': request.url,
            'scheme': parsed.scheme,
            'domain': parsed.netloc,
            'path': parsed.path,
            'query': parsed.query,
            'query_params': query_params,
            'fragment': parsed.fragment,
            'is_secure': parsed.scheme == 'https'
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Failed to parse URL: {str(e)}')


@app.post("/tools/download_file_info")
async def download_file_info(request: URLRequest) -> Dict:
    """Get information about a downloadable file without downloading it."""
    try:
        response = requests.head(request.url, timeout=10, allow_redirects=True, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        content_length = response.headers.get('Content-Length')
        content_type = response.headers.get('Content-Type')
        
        return {
            'url': request.url,
            'accessible': response.status_code == 200,
            'status_code': response.status_code,
            'content_type': content_type,
            'file_size_bytes': int(content_length) if content_length else None,
            'file_size_mb': round(int(content_length) / (1024 * 1024), 2) if content_length else None,
            'final_url': response.url
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Failed to get file info: {str(e)}')


@app.post("/tools/check_multiple_urls")
async def check_multiple_urls(request: CheckMultipleURLsRequest) -> List[Dict]:
    """Check the status of multiple URLs at once."""
    results = []
    
    for url in request.urls[:50]:  # Limit to 50 URLs
        try:
            response = requests.head(url, timeout=request.timeout, allow_redirects=True, headers={
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
    print(f"Starting Web Tools REST API Server on port {port}...")
    print("Available endpoints:")
    print("  POST /tools/fetch_webpage")
    print("  POST /tools/check_url_status")
    print("  POST /tools/extract_links")
    print("  POST /tools/scrape_webpage")
    print("  POST /tools/extract_metadata")
    print("  POST /tools/parse_url")
    print("  POST /tools/download_file_info")
    print("  POST /tools/check_multiple_urls")
    
    uvicorn.run(app, host="0.0.0.0", port=port)
