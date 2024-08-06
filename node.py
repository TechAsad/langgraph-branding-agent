
from termcolor import colored

from chains import *

from tools import * #reddit scraper and commeent claner 



    
    
 


### Nodes


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



def market_strategist(state):
    """
    
    """
    
    print(colored(f"\n---MARKET STRATEGIST---", 'green'))
    market_research = state["market_research"]
    product = state["product"]
    

    # summary generation
    marketing_strategist_agent= marketing_strategist_chain.invoke({"market_researcher_agent": market_research, "product": product})
    print(marketing_strategist_agent)
    target_audience= marketing_strategist_agent['Potential target audience']
    
   
    return { "marketing_strategy": marketing_strategist_agent, "target_audience":target_audience}



## decide which audience to target

def human_in_loop(state):
    """
    A function to select the target audience.
    """

    print(colored(f"\n---SELECT AUDIENCE ---", 'green'))

    target_audience = state["target_audience"]

    
    
    one = target_audience[0]
    two = target_audience[1]
    three = target_audience[2]
    
    input_msg = (
        f"Choose one number:\n 1. {one}\n\n  2. {two}\n\n  3. {three}\n"
    )

    selected_audience = input(input_msg)
    
    
    

    if selected_audience == '1':
        return {"target_audience": one}
    elif selected_audience == '2':
        return {"target_audience": two}
    elif selected_audience == '3':
        return {"target_audience": three}
    else:
        return {"target_audience": one}



def campaign_crafter(state):
    """
    
    """
    
    print(colored(f"\n---CAMPAIGN CRAFTER---\n\n", 'green'))
    market_research = state["market_research"]
    marketing_strategy = state["marketing_strategy"]
    target_audience= state["target_audience"]
    product = state["product"]
    
    print(colored(f"Target Audience:\n {target_audience}", 'blue'))

    # summary generation
    campaign_agent = campaign_chain.invoke({"product":product, "market_researcher_agent": market_research,"marketing_strategist_agent":marketing_strategy, "target_audience":target_audience})
    print(campaign_agent)
    
    return { "campaign": campaign_agent}


def landing_page_generator(state):
    """
    
    """
    
    print(colored(f"\n---LANDING_PAGE_GENERATOR---", 'green'))
    market_research = state["market_research"]
    marketing_strategy = state["marketing_strategy"]

    product = state["product"]
    campaign_agent = state["campaign"]
    

    # summary generation
    landing_page_agent = landing_page_chain.invoke({"product":product, "market_researcher_agent":market_research,"marketing_strategist_agent":marketing_strategy, "campaign_agent":campaign_agent})
    
    return { "landing_page": landing_page_agent}




 
 
 


