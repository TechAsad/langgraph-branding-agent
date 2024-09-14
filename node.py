
from termcolor import colored

from chains import *

from tools import * #reddit scraper and commeent claner 



    
    
 


### Nodes


def google_search(state):
    #agency_type="AI Automation Agency"
    
    product = state["product"]
    
    print(colored(f"\n---GOOOGLE SEARCHER---", 'green'))
    
    results=serper_search(f"branding stratergies for {product} ")
    print(results)
    web_text = detect_and_scrape_url(results)
    
    google_summary_agent= web_summary_chain.invoke({"web_text":web_text, "product": product})
    
    return {"google_search_summary":google_summary_agent}

#google_search(agency_type)


def subreddit_to_search(state):
    """
    
    """
    print(colored(f"---POSSIBLE SUB REDDITS---", 'green'))
    
    product = state["product"]

    subreddit_name_agent= subreddit_name_chain.invoke({"product": product})
    print(subreddit_name_agent)
    
    
    return {"sub_reddits_to_search": subreddit_name_agent}


def subreddit_selector(state):
    """
    
    """
    
    print(colored(f"\n\n ---SUB-REDDITS SELECTOR---", 'green'))
    sub_reddits_to_search = state["sub_reddits_to_search"]
    product= state["product"]
   
    
    sub_reddits = search_subreddits(sub_reddits_to_search)
    

    #google_search=web_search_tool.invoke({"query": "latest {location} "})
    subreddit_searcher_agent= subreddit_searcher_chain.invoke({"product": product, "sub_reddits":sub_reddits})
    print(subreddit_searcher_agent)
    print(colored(f"\nSub Reddits:\n\n {subreddit_searcher_agent} ", 'green'))
    
    return {"sub_reddits_to_scrape": subreddit_searcher_agent}


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



def web_summarizer(state):
    """
    
    """
    
    print(colored(f"\n---COMPETITION WEB SUMMARY---", 'green'))
    
    
    
    product = state["product"]
    

    # summary generation
    web_text= detect_and_scrape_url(product)
    
    
    web_summary_agent= web_summary_chain.invoke({"web_text":web_text, "product": product})
    print(web_summary_agent[:300])
    return { "web_summary": web_summary_agent}




def market_researcher(state):
    """
    
    """
    
    print(colored(f"\n---MARKET RESEARCHER---", 'green'))
    subreddits_to_scrape = state["sub_reddits_to_scrape"]
    product = state["product"]
    

    # summary generation
    comments= reddit_comments(subreddits_to_scrape)
    
    print(colored(f"\n---Filtering Comments---", 'blue'))
    
    filtered_comments= filter_comments(comments)
    market_researcher_agent= market_researcher_chain.invoke({"filtered_comments":filtered_comments[:1000], "product": product})
    return { "market_research": market_researcher_agent}



def strategist(state):
    """
    
    """
    
    print(colored(f"\n---BRAND STRATEGIST---", 'green'))
    market_research = state["market_research"]
    product = state["product"]
    

    # summary generation
    brand_strategist_agent=  brand_strategist_chain.invoke({"market_researcher_agent": market_research, "product": product})
    print( brand_strategist_agent)
    #target_audience=  brand_strategist_agent['Potential target audience']
    
    return { "brand_strategy":  brand_strategist_agent}






def branding_creator(state):
    """
    
    """
    
    print(colored(f"\n---BRAND CRAFTER---\n\n", 'green'))
    market_research = state["market_research"]
    brand_strategy = state["brand_strategy"]
    web_summary =state["web_summary"]
    google_search_summary = state["google_search_summary"] 
    product = state["product"]
    
    

    # summary generation
    branding_agent = branding_chain.invoke({"product":product, "google_summary": google_search_summary, "web_summary_agent":web_summary, "market_researcher_agent": market_research,"brand_strategist_agent":brand_strategy})

    return { "product":product, "branding": branding_agent}




 
 
 


