from typing_extensions import TypedDict


### State


class GraphState(TypedDict):
    """
    Represents the state of our graph.

   """
    product: str
    
    
      
    sub_reddits_to_search: str
    sub_reddits_to_scrape: str
    
    comments: str
    google_search_summary: str
    web_summary: str

    market_research: str
    branding_rag: str
    brand_strategy: str
    branding: str
   
