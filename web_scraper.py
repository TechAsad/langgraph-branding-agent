
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import random
from requests.exceptions import RequestException
from langchain.tools import tool
from fake_useragent import UserAgent
import pandas as pd
import re

def get_random_user_agent():
    ua = UserAgent()
    return ua.random



def extract_url(web_str):
    # Use regular expression to find the URL
    url_match = re.search(r'http[s]?://\S+', web_str)
    if url_match:
        return url_match.group()
    else:
        return None






def scrape_website(url: str, max_retries: int = 3, backoff_factor: float = 0.3, timeout: int = 10) -> dict:
    headers = {'User-Agent': get_random_user_agent()}
    session = requests.Session()
    # Extract the URL
    url = extract_url(url)
    for attempt in range(max_retries):
        try:
            response = session.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text content
            text = soup.get_text(separator=' ', strip=True)
            
            # Basic content cleaning
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            # Extract links
            links = [urljoin(url, a.get('href')) for a in soup.find_all('a', href=True)]
            
            return {
                "source": url,
                "content": text,
                "links": links[:4]
            }
        
        except requests.RequestException as e:
            if attempt == max_retries - 1:
                return {
                    "source": url,
                    "error": f"Failed to scrape website after {max_retries} attempts: {str(e)}"
                }
            else:
                time.sleep(backoff_factor * (2 ** attempt))
                continue

def get_links_and_text(url: str, max_depth: int = 2, max_retries: int = 3, backoff_factor: float = 0.3, timeout: int = 10):
    visited_urls = set()
    results = []

    def scrape_recursive(url: str, depth: int):
        if depth > max_depth or url in visited_urls:
            return

        visited_urls.add(url)
        result = scrape_website(url, max_retries, backoff_factor, timeout)
        
        if "error" not in result:
            results.append({"source": result["source"], "content": result["content"]})
            for link in result.get("links", []):
                scrape_recursive(link, depth + 1)

    scrape_recursive(url, 0)
    return results

