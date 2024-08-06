from state import GraphState
from langgraph.graph import END, StateGraph, START
from node import *


workflow = StateGraph(GraphState)

# Define the nodes
workflow.add_node("subreddit_to_search", subreddit_to_search)  # 
workflow.add_node("subreddit_selector",subreddit_selector)  # 
workflow.add_node("market_researcher", market_researcher)
workflow.add_node("market_strategist", market_strategist)  # 
workflow.add_node("human_in_loop", human_in_loop)
workflow.add_node("campaign_crafter",campaign_crafter)  # 

workflow.add_node("landing_page_generator", landing_page_generator)


# Edges
workflow.set_entry_point("subreddit_to_search")
workflow.add_edge("subreddit_to_search","subreddit_selector")


workflow.add_edge("subreddit_selector","market_researcher")
workflow.add_edge("market_researcher","market_strategist")

workflow.add_edge("market_strategist", "human_in_loop")

workflow.add_edge("human_in_loop", "campaign_crafter")

workflow.add_edge("campaign_crafter", "landing_page_generator")

workflow.add_edge("landing_page_generator", END)



# Compile
app = workflow.compile()