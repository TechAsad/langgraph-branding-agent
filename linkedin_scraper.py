# Import necessary libraries
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup as bs
import time
import pandas as pd

# Initialize Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Optional: run in headless mode

# LinkedIn Credentials
username = "asadiqbal7@icloud.com"
password = "lion7777"

# Set LinkedIn user profile URL for scraping
profile_url = 'https://www.linkedin.com/in/asad18/'

# Initialize WebDriver for Chrome
browser = webdriver.Chrome(options=chrome_options)

# Open LinkedIn login page
browser.get('https://www.linkedin.com/login')

# Enter login credentials and submit
elementID = browser.find_element(By.ID, "username")
elementID.send_keys(username)
elementID = browser.find_element(By.ID, "password")
elementID.send_keys(password)
elementID.submit()

# Navigate to the user's posts page
post_page = profile_url + '/recent-activity/all/'
browser.get(post_page)

# Scroll through the page to load all posts
SCROLL_PAUSE_TIME = 5
MAX_SCROLLS = 5
last_height = browser.execute_script("return document.body.scrollHeight")
scrolls = 0
no_change_count = 0

while True:
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(SCROLL_PAUSE_TIME)
    new_height = browser.execute_script("return document.body.scrollHeight")
    no_change_count = no_change_count + 1 if new_height == last_height else 0
    if no_change_count >= 5 or (MAX_SCROLLS and scrolls >= MAX_SCROLLS):
        break
    last_height = new_height
    scrolls += 1

# Parse the page source with BeautifulSoup
page_source = browser.page_source
soup = bs(page_source.encode("utf-8"), "html.parser")

# Extract post containers from the HTML
containers = [container for container in soup.find_all("div", {"class": "feed-shared-update-v2"}) if 'activity' in container.get('data-urn', '')]

# Function to extract the text from a container
def get_text(container, selector, attributes):
    try:
        element = container.find(selector, attributes)
        if element:
            return element.text.strip()
    except Exception as e:
        print(e)
    return ""

# Function to handle "See more" and get full post text
def get_full_post_text(container):
    try:
        see_more_button = container.find("button", {"aria-label": "See more"})
        if see_more_button:
            browser.execute_script("arguments[0].click();", see_more_button)
            time.sleep(2)  # Wait for the content to expand
            return container.text.strip()
    except Exception as e:
        print(e)
    return get_text(container, "div", {"class": "feed-shared-update-v2__description-wrapper"})

# Function to extract comments from a post
def get_comments(container):
    comments = []
    comment_elements = container.find_all("div", {"class": "comments-comment-item__main-content"})
    for comment_element in comment_elements:
        commenter_name = get_text(comment_element, "span", {"class": "comments-post-meta__name"})
        comment_text = get_text(comment_element, "span", {"class": "comments-comment-item__main-content"})
        comments.append({"commenter_name": commenter_name, "comment_text": comment_text})
    return comments

# List to hold all post data
posts_data = []

# Process each container to extract post information
for container in containers:
    post_text = get_full_post_text(container)
    post_date = get_text(container, "a", {"class": "app-aware-link update-components-actor__sub-description-link"})
    #post_comments = get_comments(container)

    posts_data.append({
        "Post Text": post_text,
        "Post Date": post_date,
        #"Comments": post_comments
    })

# Convert the data into a DataFrame
df = pd.DataFrame(posts_data)

# Save the data to a CSV file
csv_file = f"{profile_url.split('/')[-2]}_posts.csv"
df.to_csv(csv_file, encoding='utf-8', index=False)
print(f"Data exported to {csv_file}")

# Close the browser
browser.quit()
