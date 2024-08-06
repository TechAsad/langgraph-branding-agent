import praw
import pandas as pd

import os

from dotenv import load_dotenv
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
            sub_comments= comments[:100]
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
        df = pd.DataFrame(comments, columns=['Comment'])
        df.to_csv(output_file, index=False)
        print(f"Comments for {subreddits} scraped and saved to {output_file}")
    else:
        print("No comments scraped from {subreddits}.")
    return comments




### filter comments tool


from fuzzywuzzy import fuzz

def filter_comments(comments):
    unwanted_keywords = ['https']
    # Filter out comments containing unwanted keywords and comments with less than 4 words
    filtered_comments = []
    for comment in comments:
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

