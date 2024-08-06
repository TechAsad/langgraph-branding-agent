from typing_extensions import TypedDict


### State


class GraphState(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
            product: str
            sub_reddits_to_search: str
            sub_reddits_to_scrape: List[str]
            comments: str
            market_research: str
            marketing_strategy: str
            campaign: str
            landing_page: str
    """

    product: str
    sub_reddits_to_search: str
    sub_reddits_to_scrape: str
    comments: str
    market_research: str
    marketing_strategy: dict
    target_audience: dict
    campaign: str
    landing_page: str
   
    