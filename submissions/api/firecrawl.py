"""
Website crawling module using FireCrawl API or web scraping
"""
import requests
from bs4 import BeautifulSoup
import time
from typing import Dict, Any, Optional
import logging

api_key = "fc-5de4b54e2adf416bbc93b3803f6cab70"
logger = logging.getLogger(__name__)

def crawl_website(url: str, timeout: int = 30) -> Dict[str, Any]:
    """
    Crawl a website and extract SEO-relevant data
    
    Args:
        url: Website URL to crawl
        timeout: Request timeout in seconds
        
    Returns:
        Dictionary containing website data
    """
    try:
        # Clean up URL
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Set headers to mimic browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }
        
        # Start timer for page load measurement
        start_time = time.time()
        
        # Make request
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        # Calculate load time
        load_time = time.time() - start_time
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract SEO data
        data = {
            'url': url,
            'status_code': response.status_code,
            'page_load_time': round(load_time, 2),
            'title': extract_title(soup),
            'meta_description': extract_meta_description(soup),
            'meta_keywords': extract_meta_keywords(soup),
            'headings': extract_headings(soup),
            'word_count': extract_word_count(soup),
            'image_count': len(soup.find_all('img')),
            'internal_links': count_internal_links(soup, url),
            'external_links': count_external_links(soup, url),
            'mobile_friendly': check_mobile_viewport(soup),
            'has_ssl': url.startswith('https://'),
            'content_length': len(response.content),
            'response_headers': dict(response.headers),
        }
        
        # Additional technical SEO checks
        data.update(technical_seo_checks(soup, response))
        
        logger.info(f"Successfully crawled {url}")
        return data
        
    except requests.exceptions.Timeout:
        logger.error(f"Timeout crawling {url}")
        return create_error_response(url, "Timeout")
    except requests.exceptions.ConnectionError:
        logger.error(f"Connection error crawling {url}")
        return create_error_response(url, "Connection Error")
    except Exception as e:
        logger.error(f"Error crawling {url}: {str(e)}")
        return create_error_response(url, str(e))

def extract_title(soup: BeautifulSoup) -> Optional[str]:
    """Extract page title"""
    title_tag = soup.find('title')
    return title_tag.get_text().strip() if title_tag else None

def extract_meta_description(soup: BeautifulSoup) -> Optional[str]:
    """Extract meta description"""
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    if not meta_desc:
        meta_desc = soup.find('meta', attrs={'property': 'og:description'})
    return meta_desc.get('content').strip() if meta_desc else None

def extract_meta_keywords(soup: BeautifulSoup) -> Optional[str]:
    """Extract meta keywords"""
    meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
    return meta_keywords.get('content').strip() if meta_keywords else None

def extract_headings(soup: BeautifulSoup) -> Dict[str, int]:
    """Extract heading structure"""
    headings = {}
    for i in range(1, 7):
        h_tags = soup.find_all(f'h{i}')
        headings[f'h{i}'] = len(h_tags)
    return headings

def extract_word_count(soup: BeautifulSoup) -> int:
    """Extract approximate word count from visible text"""
    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.decompose()
    
    # Get text and count words
    text = soup.get_text()
    words = text.split()
    return len(words)

def count_internal_links(soup: BeautifulSoup, base_url: str) -> int:
    """Count internal links"""
    from urllib.parse import urljoin, urlparse
    
    base_domain = urlparse(base_url).netloc
    internal_count = 0
    
    for link in soup.find_all('a', href=True):
        href = link['href']
        full_url = urljoin(base_url, href)
        link_domain = urlparse(full_url).netloc
        
        if link_domain == base_domain:
            internal_count += 1
    
    return internal_count

def count_external_links(soup: BeautifulSoup, base_url: str) -> int:
    """Count external links"""
    from urllib.parse import urljoin, urlparse
    
    base_domain = urlparse(base_url).netloc
    external_count = 0
    
    for link in soup.find_all('a', href=True):
        href = link['href']
        if href.startswith(('http://', 'https://')):
            link_domain = urlparse(href).netloc
            if link_domain != base_domain:
                external_count += 1
    
    return external_count

def check_mobile_viewport(soup: BeautifulSoup) -> bool:
    """Check if page has mobile viewport meta tag"""
    viewport = soup.find('meta', attrs={'name': 'viewport'})
    return viewport is not None

def technical_seo_checks(soup: BeautifulSoup, response: requests.Response) -> Dict[str, Any]:
    """Perform additional technical SEO checks"""
    checks = {}
    
    # Check for canonical URL
    canonical = soup.find('link', attrs={'rel': 'canonical'})
    checks['has_canonical'] = canonical is not None
    checks['canonical_url'] = canonical.get('href') if canonical else None
    
    # Check for Open Graph tags
    og_title = soup.find('meta', attrs={'property': 'og:title'})
    og_description = soup.find('meta', attrs={'property': 'og:description'})
    og_image = soup.find('meta', attrs={'property': 'og:image'})
    
    checks['has_og_tags'] = any([og_title, og_description, og_image])
    
    # Check for Twitter Card tags
    twitter_card = soup.find('meta', attrs={'name': 'twitter:card'})
    checks['has_twitter_card'] = twitter_card is not None
    
    # Check for schema markup
    json_ld = soup.find_all('script', attrs={'type': 'application/ld+json'})
    microdata = soup.find_all(attrs={'itemtype': True})
    checks['has_schema'] = len(json_ld) > 0 or len(microdata) > 0
    
    # Check response headers for SEO
    headers = response.headers
    checks['has_gzip'] = 'gzip' in headers.get('Content-Encoding', '')
    checks['cache_control'] = headers.get('Cache-Control')
    checks['server'] = headers.get('Server')
    
    # Check for robots meta tag
    robots_meta = soup.find('meta', attrs={'name': 'robots'})
    checks['robots_meta'] = robots_meta.get('content') if robots_meta else None
    
    return checks

def create_error_response(url: str, error: str) -> Dict[str, Any]:
    """Create error response with default values"""
    return {
        'url': url,
        'error': error,
        'status_code': 0,
        'page_load_time': 0,
        'title': None,
        'meta_description': None,
        'meta_keywords': None,
        'headings': {'h1': 0, 'h2': 0, 'h3': 0, 'h4': 0, 'h5': 0, 'h6': 0},
        'word_count': 0,
        'image_count': 0,
        'internal_links': 0,
        'external_links': 0,
        'mobile_friendly': False,
        'has_ssl': False,
        'content_length': 0,
        'response_headers': {},
        'has_canonical': False,
        'canonical_url': None,
        'has_og_tags': False,
        'has_twitter_card': False,
        'has_schema': False,
        'has_gzip': False,
        'cache_control': None,
        'server': None,
        'robots_meta': None,
    }

# Alternative: Integration with FireCrawl API service
def crawl_with_firecrawl_api(url: str, api_key: str = None) -> Dict[str, Any]:
    """
    Use FireCrawl API service for more advanced crawling
    This is a placeholder for actual FireCrawl API integration
    """
    if not api_key:
        # Fallback to basic crawling
        return crawl_website(url)
    
    try:
        # FireCrawl API integration would go here
        # This is a placeholder implementation
        api_url = "https://api.firecrawl.dev/v0/scrape"
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        data = {
            'url': url,
            'extractorOptions': {
                'mode': 'llm-extraction',
                'extractionSchema': {
                    'type': 'object',
                    'properties': {
                        'title': {'type': 'string'},
                        'description': {'type': 'string'},
                        'keywords': {'type': 'array', 'items': {'type': 'string'}},
                        'content': {'type': 'string'}
                    }
                }
            }
        }
        
        response = requests.post(api_url, headers=headers, json=data)
        if response.status_code == 200:
            api_result = response.json()
            # Transform API result to match our format
            return transform_firecrawl_response(api_result, url)
        else:
            # Fallback to basic crawling
            return crawl_website(url)
            
    except Exception as e:
        logger.error(f"FireCrawl API error: {e}")
        return crawl_website(url)

def transform_firecrawl_response(api_result: Dict, url: str) -> Dict[str, Any]:
    """Transform FireCrawl API response to our format"""
    # This would transform the FireCrawl response format
    # to match our expected data structure
    return crawl_website(url)  # Placeholder fallback