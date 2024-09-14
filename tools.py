import praw
import pandas as pd

import os
import re
from dotenv import load_dotenv


import json

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time

from fake_useragent import UserAgent
import pandas as pd

import asyncio


load_dotenv()

# Replace with your Reddit app credentials
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET =  os.getenv("CLIENT_SECRET")
USER_AGENT = os.getenv("USER_AGENT") # You can use any descriptive user agent 


# Initialize PRAW with credentials
reddit = praw.Reddit(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    user_agent=USER_AGENT
)

## get subreddits

def search_subreddits(query, limit_per_word=5):
    words = query.split(',')
    all_subreddits = []
    
    for word in words:
        try:
            subreddits = reddit.subreddits.search(word, limit=limit_per_word)
            all_subreddits.extend([subreddit.display_name for subreddit in subreddits])
        except Exception as e:
            print(f"Error searching subreddits with query '{word}': {e}")

    return list(set(all_subreddits))




## get comments


def get_top_posts(subreddit_name, limit=3):
    try:
        subreddit = reddit.subreddit(subreddit_name)
        # Check if the subreddit exists by attempting to access its posts
        if subreddit.display_name != subreddit_name:
            raise Exception(f"Subreddit {subreddit_name} does not exist.")
        top_posts = subreddit.top(limit=limit)
        return list(top_posts)  # Convert to list
    except Exception as e:
        print(f"Error fetching top posts from {subreddit_name}: {e}")
        return []

def get_comments_from_post(post):
    try:
        post.comments.replace_more(limit=100)
        comments = [comment.body for comment in post.comments.list()]
        return comments
    except Exception as e:
        print(f"Error fetching comments from post {post.id}: {e}")
        return []

def scrape_reddit_comments(subreddits):
    all_comments = []
    failed_subreddits = []
    
    for subreddit_name in subreddits:
        print(f"Scraping subreddit: {subreddit_name}")
        top_posts = get_top_posts(subreddit_name)
        if not top_posts:  # Skip if no posts were retrieved
            failed_subreddits.append(subreddit_name)
            continue
        for post in top_posts:
            comments = get_comments_from_post(post)
            sub_comments= comments[:80]
            all_comments.extend(sub_comments)
    
    if failed_subreddits:
        print(f"Failed to retrieve data from these subreddits: {', '.join(failed_subreddits)}")
    
    return all_comments

def reddit_comments(sub_reddits):
    output_file=f"{sub_reddits}_comments.csv"
    subreddits = sub_reddits.split(',')
    subreddits = [sub.strip() for sub in subreddits]
    
    comments = scrape_reddit_comments(subreddits)
    print(comments)
    print(f"Total comments scraped: {len(comments)}")
    
    if comments:
       
        print(f"Comments for {subreddits} scraped")
    else:
        print("No comments scraped from {subreddits}.")
    return comments




### filter comments tool


from fuzzywuzzy import fuzz

def filter_comments(comments):
    unwanted_keywords = ['https']
    # Filter out comments containing unwanted keywords and comments with less than 4 words
    filtered_comments = []
    for comment in comments[:250]:
        if len(comment.split()) >= 4 and not any(keyword.lower() in comment.lower() for keyword in unwanted_keywords):
            filtered_comments.append(comment)

    # Remove comments with links
    filtered_comments = [comment for comment in filtered_comments if 'http' not in comment and 'https' not in comment]
    
    # Remove duplicate comments that are 80% similar or more
    def is_duplicate(comment, existing_comments, threshold=80):
        for existing_comment in existing_comments:
            if fuzz.ratio(comment, existing_comment) >= threshold:
                return True
        return False
    
    unique_comments = []
    for comment in filtered_comments:
        if not is_duplicate(comment, unique_comments):
            unique_comments.append(comment)
    
    return unique_comments



def detect_and_scrape_url(message):
    # Regular expression to detect URLs
    url_pattern = re.compile(r'(https?://[^\s]+)')
    
    # Search for URLs in the message
    match = url_pattern.search(message)

    # Check if a URL was found
    if match:
        url = match.group(0)
        
        # Check if the URL has already been scraped
        
        print(f"\nScraping {url}")
        website_text = get_links_and_text(url)
        # Store the scraped content
        
    
        result = {"URL": url, "text": website_text}
    else:
        result = {}

    # Convert to JSON format
    result_json = json.dumps(result)
    print(result_json)
    return result_json




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

def scrape_new_website(url: str, base_domain: str, max_retries: int = 3, backoff_factor: float = 0.3, timeout: int = 10) -> dict:
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
            text = 'joined '.join(chunk for chunk in chunks if chunk)
            
            # Extract links within the same domain
            links = [urljoin(url, a.get('href')) for a in soup.find_all('a', href=True)]
            sublinks = [link for link in links if urlparse(link).netloc == base_domain]
            
            print(len(sublinks))
            return {
                "source": url,
                "content": text,
                "links": sublinks[:1]
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

def get_links_and_text(url: str, max_depth: int = 1, max_retries: int = 3, backoff_factor: float = 0.3, timeout: int = 10):
    visited_urls = set()
    results = []

    def scrape_recursive(url: str, depth: int):
        if depth > max_depth or url in visited_urls:
            return

        visited_urls.add(url)
        base_domain = urlparse(url).netloc
        result = scrape_new_website(url, base_domain, max_retries, backoff_factor, timeout)
        
        if "error" not in result:
            results.append({"source": result["source"], "content": result["content"]})
            for link in result.get("links", []):
                scrape_recursive(link, depth + 1)

    scrape_recursive(url, 0)
    return results
