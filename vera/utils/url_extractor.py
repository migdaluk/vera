"""
URL Content Extractor

Utility for extracting text content from web pages.
Supports automatic URL detection and content extraction.
"""

import re
import requests
from bs4 import BeautifulSoup
from typing import Optional, Tuple
import logging

logger = logging.getLogger("vera.utils.url_extractor")


def is_url(text: str) -> bool:
    """
    Check if the input text is a URL.
    
    Args:
        text: Input string to check
        
    Returns:
        True if text appears to be a URL, False otherwise
    """
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return bool(url_pattern.match(text.strip()))


def extract_text_from_url(url: str, timeout: int = 10) -> Tuple[bool, str]:
    """
    Extract text content from a URL.
    
    Args:
        url: URL to extract content from
        timeout: Request timeout in seconds
        
    Returns:
        Tuple of (success: bool, content: str)
        - If successful: (True, extracted_text)
        - If failed: (False, error_message)
    """
    try:
        logger.info(f"Fetching content from URL: {url}")
        
        # Set headers to mimic a browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Fetch the page
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header", "aside", "form", "iframe"]):
            script.decompose()
        
        # Try to find main article content using common selectors
        article_selectors = [
            # Specific article containers
            {'name': 'div', 'class_': 'article__body'},
            {'name': 'div', 'class_': 'article-body'},
            {'name': 'div', 'class_': 'article__text'},
            {'name': 'div', 'class_': 'article-content'},
            {'name': 'article', 'class_': None},
            {'name': 'div', 'class_': 'post-content'},
            {'name': 'div', 'class_': 'entry-content'},
            {'name': 'div', 'class_': 'content'},
            {'name': 'main', 'class_': None},
            # Fallback to body
            {'name': 'body', 'class_': None},
        ]
        
        text = None
        for selector in article_selectors:
            if selector['class_']:
                # Try exact class match
                elem = soup.find(selector['name'], class_=selector['class_'])
                if not elem:
                    # Try partial class match
                    elem = soup.find(selector['name'], class_=lambda x: x and selector['class_'] in x if x else False)
            else:
                elem = soup.find(selector['name'])
            
            if elem:
                logger.debug(f"Found content using selector: {selector}")
                text = elem.get_text(separator='\n', strip=True)
                break
        
        if not text:
            # Try paragraph-based extraction (for sites like Gazeta.pl)
            logger.info("Trying paragraph-based extraction")
            paragraphs = soup.find_all('p')
            paragraph_texts = []
            for p in paragraphs:
                p_text = p.get_text(strip=True)
                if len(p_text) > 50:  # Only meaningful paragraphs
                    paragraph_texts.append(p_text)
            
            if paragraph_texts:
                text = '\n\n'.join(paragraph_texts)
                logger.info(f"Extracted {len(paragraph_texts)} paragraphs")
            else:
                # Ultimate fallback - get all text
                text = soup.get_text(separator='\n', strip=True)
                logger.warning("Using fallback: extracting all text from page")
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        # Limit text length (max 10000 chars to avoid overwhelming the LLM)
        original_length = len(text)
        if len(text) > 10000:
            text = text[:10000] + "\n\n[Content truncated due to length...]"
            logger.warning(f"Content truncated from {original_length} to 10000 characters")
        
        logger.info(f"Successfully extracted {original_length} characters from URL")
        return True, text
        
    except requests.exceptions.Timeout:
        error_msg = f"⏱️ Request timed out after {timeout} seconds. The website may be slow or unresponsive."
        logger.error(f"Timeout error for URL: {url}")
        return False, error_msg
        
    except requests.exceptions.ConnectionError:
        error_msg = "🌐 Connection error. Please check your internet connection or verify the URL is accessible."
        logger.error(f"Connection error for URL: {url}")
        return False, error_msg
        
    except requests.exceptions.HTTPError as e:
        error_msg = f"❌ HTTP Error {e.response.status_code}: {e.response.reason}. The page may not exist or access is denied."
        logger.error(f"HTTP error for URL: {url} - {e}")
        return False, error_msg
        
    except Exception as e:
        error_msg = f"⚠️ Error extracting content: {str(e)}"
        logger.error(f"Unexpected error for URL: {url}", exc_info=True)
        return False, error_msg


def process_input(text: str) -> Tuple[str, bool]:
    """
    Process user input - detect if it's a URL and extract content if needed.
    
    Args:
        text: User input (either plain text or URL)
        
    Returns:
        Tuple of (processed_text: str, is_from_url: bool)
    """
    text = text.strip()
    
    if not text:
        return "", False
    
    # Check if input is a URL
    if is_url(text):
        logger.info(f"URL detected: {text}")
        success, content = extract_text_from_url(text)
        
        if success:
            # Prepend URL source information
            processed_text = f"[Content extracted from: {text}]\n\n{content}"
            return processed_text, True
        else:
            # Return error message if extraction failed
            return content, False
    
    # Not a URL, return as-is
    return text, False
