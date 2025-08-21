"""
News Scraping Pipeline

This pipeline demonstrates concurrent web scraping, content processing, and data
extraction patterns. It scrapes multiple news sources simultaneously, processes
content with NLP techniques, and stores structured data for analysis.

Note: This example uses mock APIs (httpbin.org) for demonstration. In real usage,
replace with actual news sites and appropriate scraping ethics.
"""

import logging
import json
import re
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import pandas as pd
from bs4 import BeautifulSoup

from hamilton import function
from hamilton.function_modifiers import parameterize, config

from flowerpower.cfg import Config

logger = logging.getLogger(__name__)

# Load configuration parameters
BASE_DIR = Path(__file__).parent.parent
PARAMS = Config.load(str(BASE_DIR), {}).run.inputs


class WebScraper:
    """Thread-safe web scraper with rate limiting and retry logic."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.session = self._create_session()
        
    def _create_session(self) -> requests.Session:
        """Create a configured requests session with retries."""
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=self.config.get('max_retries', 3),
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set headers
        session.headers.update({
            'User-Agent': self.config.get('user_agent', 'FlowerPower Scraper'),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
        return session
    
    def fetch_url(self, url: str) -> Optional[Dict[str, Any]]:
        """Fetch a single URL with error handling."""
        try:
            logger.info(f"Fetching: {url}")
            
            response = self.session.get(
                url,
                timeout=self.config.get('timeout', 30)
            )
            response.raise_for_status()
            
            return {
                'url': url,
                'status_code': response.status_code,
                'content': response.text,
                'headers': dict(response.headers),
                'timestamp': datetime.now().isoformat(),
                'encoding': response.encoding
            }
            
        except requests.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            return {
                'url': url,
                'error': str(e),
                'status_code': getattr(e.response, 'status_code', None),
                'timestamp': datetime.now().isoformat()
            }
    
    def fetch_urls_concurrent(self, urls: List[str]) -> List[Dict[str, Any]]:
        """Fetch multiple URLs concurrently with rate limiting."""
        results = []
        max_workers = min(self.config.get('max_concurrent_requests', 5), len(urls))
        delay = self.config.get('request_delay', 1.0)
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all requests
            future_to_url = {
                executor.submit(self.fetch_url, url): url 
                for url in urls
            }
            
            # Collect results with rate limiting
            for i, future in enumerate(as_completed(future_to_url)):
                if i > 0 and delay > 0:
                    time.sleep(delay)
                
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    url = future_to_url[future]
                    logger.error(f"Exception for {url}: {e}")
                    results.append({
                        'url': url,
                        'error': str(e),
                        'timestamp': datetime.now().isoformat()
                    })
        
        logger.info(f"Completed fetching {len(results)} URLs")
        return results


def target_urls(urls: List[Dict[str, Any]]) -> List[str]:
    """Extract URLs from target site configurations."""
    url_list = [site['url'] for site in urls]
    logger.info(f"Prepared {len(url_list)} URLs for scraping")
    return url_list


def raw_web_data(
    target_urls: List[str],
    max_concurrent_requests: int,
    request_delay: float,
    timeout: int,
    user_agent: str,
    max_retries: int
) -> List[Dict[str, Any]]:
    """Scrape multiple websites concurrently."""
    scraper_config = {
        'max_concurrent_requests': max_concurrent_requests,
        'request_delay': request_delay,
        'timeout': timeout,
        'user_agent': user_agent,
        'max_retries': max_retries
    }
    
    scraper = WebScraper(scraper_config)
    raw_data = scraper.fetch_urls_concurrent(target_urls)
    
    # Filter successful responses
    successful_responses = [
        data for data in raw_data 
        if 'error' not in data and data.get('status_code') == 200
    ]
    
    logger.info(f"Successfully scraped {len(successful_responses)} of {len(target_urls)} URLs")
    return successful_responses


def parsed_content(
    raw_web_data: List[Dict[str, Any]], 
    urls: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Parse content from raw web data based on site configurations."""
    parsed_articles = []
    
    # Create URL to config mapping
    url_configs = {site['url']: site for site in urls}
    
    for data in raw_web_data:
        if 'content' not in data:
            continue
            
        url = data['url']
        site_config = url_configs.get(url, {})
        content_type = site_config.get('type', 'html')
        selectors = site_config.get('selectors', {})
        
        try:
            if content_type == 'json':
                # Parse JSON response (mock data)
                content_data = json.loads(data['content'])
                article = {
                    'source_url': url,
                    'source_name': site_config.get('name', 'unknown'),
                    'title': f"Mock Article from {site_config.get('name', 'API')}",
                    'content': f"This is mock content from {url}. In real usage, this would contain actual article text.",
                    'publish_date': datetime.now().isoformat(),
                    'author': 'Mock Author',
                    'content_type': content_type,
                    'scraped_at': data['timestamp']
                }
                
            elif content_type == 'xml':
                # Parse XML response (mock data)
                article = {
                    'source_url': url,
                    'source_name': site_config.get('name', 'unknown'),
                    'title': f"Mock XML Article from {site_config.get('name', 'Feed')}",
                    'content': f"This is mock XML content from {url}. In real usage, this would parse RSS/XML feeds.",
                    'publish_date': datetime.now().isoformat(),
                    'author': 'Mock Feed Author',
                    'content_type': content_type,
                    'scraped_at': data['timestamp']
                }
                
            else:
                # Parse HTML content
                soup = BeautifulSoup(data['content'], 'html.parser')
                
                # Extract based on selectors (simplified for demo)
                title = soup.find('title')
                title_text = title.text.strip() if title else f"Article from {url}"
                
                # In real usage, you'd use the selectors from config
                content_text = soup.get_text()[:1000] + "..." if len(soup.get_text()) > 1000 else soup.get_text()
                
                article = {
                    'source_url': url,
                    'source_name': site_config.get('name', 'unknown'),
                    'title': title_text,
                    'content': content_text,
                    'publish_date': datetime.now().isoformat(),
                    'author': 'Unknown',
                    'content_type': content_type,
                    'scraped_at': data['timestamp']
                }
            
            # Add metadata
            article['content_hash'] = hashlib.md5(article['content'].encode()).hexdigest()
            article['content_length'] = len(article['content'])
            
            parsed_articles.append(article)
            
        except Exception as e:
            logger.error(f"Error parsing content from {url}: {e}")
            continue
    
    logger.info(f"Parsed {len(parsed_articles)} articles from {len(raw_web_data)} responses")
    return parsed_articles


def processed_content(
    parsed_content: List[Dict[str, Any]],
    min_content_length: int,
    max_content_length: int,
    extract_keywords: bool,
    sentiment_analysis: bool,
    language_detection: bool
) -> List[Dict[str, Any]]:
    """Process and enhance content with NLP techniques."""
    processed_articles = []
    
    for article in parsed_content:
        content = article['content']
        content_length = len(content)
        
        # Filter by content length
        if content_length < min_content_length or content_length > max_content_length:
            logger.debug(f"Skipping article due to length: {content_length}")
            continue
        
        # Create processed copy
        processed_article = article.copy()
        
        # Extract keywords (simplified implementation)
        if extract_keywords:
            keywords = extract_simple_keywords(content)
            processed_article['keywords'] = keywords
        
        # Sentiment analysis (simplified implementation)
        if sentiment_analysis:
            sentiment = analyze_simple_sentiment(content)
            processed_article['sentiment'] = sentiment
        
        # Language detection (simplified implementation)
        if language_detection:
            language = detect_simple_language(content)
            processed_article['language'] = language
        
        # Content statistics
        processed_article['word_count'] = len(content.split())
        processed_article['sentence_count'] = len(content.split('.'))
        processed_article['processed_at'] = datetime.now().isoformat()
        
        processed_articles.append(processed_article)
    
    logger.info(f"Processed {len(processed_articles)} articles with NLP enhancements")
    return processed_articles


def filtered_articles(
    processed_content: List[Dict[str, Any]],
    date_range: Dict[str, str],
    keywords: Dict[str, Any],
    content_types: List[str]
) -> List[Dict[str, Any]]:
    """Filter articles based on date range, keywords, and content types."""
    filtered = []
    
    # Parse date range
    start_date = datetime.fromisoformat(date_range['start_date'])
    end_date = datetime.fromisoformat(date_range['end_date'])
    include_keywords = keywords.get('include', [])
    exclude_keywords = keywords.get('exclude', [])
    
    for article in processed_content:
        # Date filtering
        try:
            publish_date = datetime.fromisoformat(article['publish_date'].replace('Z', '+00:00'))
            if not (start_date <= publish_date <= end_date):
                continue
        except (ValueError, KeyError):
            # If date parsing fails, include the article
            pass
        
        # Content type filtering
        if content_types and article.get('content_type') not in content_types:
            continue
        
        # Keyword filtering
        content_lower = article['content'].lower()
        title_lower = article['title'].lower()
        
        # Check exclude keywords first
        if exclude_keywords and any(
            keyword.lower() in content_lower or keyword.lower() in title_lower
            for keyword in exclude_keywords
        ):
            continue
        
        # Check include keywords (if specified)
        if include_keywords and not any(
            keyword.lower() in content_lower or keyword.lower() in title_lower
            for keyword in include_keywords
        ):
            continue
        
        filtered.append(article)
    
    logger.info(f"Filtered to {len(filtered)} articles from {len(processed_content)} processed articles")
    return filtered


def processed_articles(
    filtered_articles: List[Dict[str, Any]],
    scrape_timestamp: str,
    output_format: str,
    output_dir: str,
    include_metadata: bool,
    deduplication: bool
) -> Dict[str, Any]:
    """Save processed articles and return summary statistics."""
    
    # Ensure output directory exists
    output_path = BASE_DIR / output_dir
    output_path.mkdir(exist_ok=True)
    
    articles = filtered_articles.copy()
    
    # Deduplication
    if deduplication:
        seen_hashes = set()
        deduplicated = []
        for article in articles:
            content_hash = article.get('content_hash')
            if content_hash and content_hash not in seen_hashes:
                seen_hashes.add(content_hash)
                deduplicated.append(article)
        articles = deduplicated
        logger.info(f"Deduplicated to {len(articles)} unique articles")
    
    # Add batch metadata
    if include_metadata:
        batch_metadata = {
            'scrape_timestamp': scrape_timestamp,
            'total_articles': len(articles),
            'processing_timestamp': datetime.now().isoformat(),
            'sources': list(set(article['source_name'] for article in articles)),
            'content_types': list(set(article.get('content_type', 'unknown') for article in articles))
        }
        
        for article in articles:
            article['batch_metadata'] = batch_metadata
    
    # Save data
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if output_format == 'json':
        output_file = output_path / f"articles_{timestamp}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(articles, f, indent=2, ensure_ascii=False)
            
    elif output_format == 'csv':
        output_file = output_path / f"articles_{timestamp}.csv"
        # Flatten nested data for CSV
        flattened_articles = []
        for article in articles:
            flat_article = article.copy()
            # Convert lists/dicts to strings for CSV compatibility
            for key, value in flat_article.items():
                if isinstance(value, (list, dict)):
                    flat_article[key] = json.dumps(value)
            flattened_articles.append(flat_article)
        
        df = pd.DataFrame(flattened_articles)
        df.to_csv(output_file, index=False, encoding='utf-8')
        
    else:
        output_file = output_path / f"articles_{timestamp}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(articles, f, indent=2, ensure_ascii=False)
    
    # Create symlink to latest
    latest_file = output_path / f"latest_articles.{output_format}"
    if latest_file.exists():
        latest_file.unlink()
    latest_file.symlink_to(output_file.name)
    
    # Generate summary statistics
    sources = {}
    content_types = {}
    for article in articles:
        source = article['source_name']
        content_type = article.get('content_type', 'unknown')
        sources[source] = sources.get(source, 0) + 1
        content_types[content_type] = content_types.get(content_type, 0) + 1
    
    result = {
        'scraping_completed': True,
        'output_file': str(output_file),
        'latest_file': str(latest_file),
        'format': output_format,
        'total_articles': len(articles),
        'unique_sources': len(sources),
        'source_breakdown': sources,
        'content_type_breakdown': content_types,
        'average_content_length': sum(len(a['content']) for a in articles) / len(articles) if articles else 0,
        'processing_timestamp': datetime.now().isoformat(),
        'sample_articles': articles[:3] if articles else []  # Include sample for verification
    }
    
    logger.info(f"Saved {len(articles)} articles to {output_file}")
    return result


# Utility functions for content processing

def extract_simple_keywords(content: str, max_keywords: int = 10) -> List[str]:
    """Extract keywords using simple frequency analysis."""
    # Remove common stop words and extract frequent terms
    stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'a', 'an', 'this', 'that', 'these', 'those'}
    
    # Simple word extraction
    words = re.findall(r'\b[a-zA-Z]{3,}\b', content.lower())
    word_freq = {}
    
    for word in words:
        if word not in stop_words:
            word_freq[word] = word_freq.get(word, 0) + 1
    
    # Return top keywords
    top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    return [word for word, freq in top_words[:max_keywords]]


def analyze_simple_sentiment(content: str) -> Dict[str, Any]:
    """Perform simple sentiment analysis based on keyword presence."""
    positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'positive', 'success', 'win', 'best', 'love', 'like', 'happy', 'pleased']
    negative_words = ['bad', 'terrible', 'awful', 'horrible', 'negative', 'failure', 'lose', 'worst', 'hate', 'dislike', 'sad', 'angry', 'disappointed']
    
    content_lower = content.lower()
    positive_count = sum(1 for word in positive_words if word in content_lower)
    negative_count = sum(1 for word in negative_words if word in content_lower)
    
    if positive_count > negative_count:
        sentiment = 'positive'
        confidence = min(0.9, 0.5 + (positive_count - negative_count) * 0.1)
    elif negative_count > positive_count:
        sentiment = 'negative'
        confidence = min(0.9, 0.5 + (negative_count - positive_count) * 0.1)
    else:
        sentiment = 'neutral'
        confidence = 0.5
    
    return {
        'sentiment': sentiment,
        'confidence': confidence,
        'positive_words_found': positive_count,
        'negative_words_found': negative_count
    }


def detect_simple_language(content: str) -> str:
    """Simple language detection based on common words."""
    # Very basic language detection - in practice, use a proper library like langdetect
    english_words = ['the', 'and', 'or', 'is', 'are', 'was', 'were', 'have', 'has', 'had', 'this', 'that', 'with', 'for', 'from']
    
    content_lower = content.lower()
    english_count = sum(1 for word in english_words if f' {word} ' in content_lower)
    
    # Simple heuristic - in practice, use proper language detection
    if english_count >= 3:
        return 'en'
    else:
        return 'unknown'