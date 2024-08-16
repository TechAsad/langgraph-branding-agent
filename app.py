import streamlit as st
from termcolor import colored
from typing_extensions import TypedDict
from chains import *
from tools import *  # reddit scraper and comment cleaner

from node import *
# Define the GraphState class
class GraphState(TypedDict):
    product: str
    sub_reddits_to_search: str
    sub_reddits_to_scrape: str
    comments: str
    market_research: str
    marketing_strategy: dict
    
    target_audiences: dict
    target_audience: str
   
    
    campaign: str
    landing_page: str
    


st.set_page_config(page_title='AI Market Researcher', page_icon="👨🏻")


# Define the nodes
def subreddit_to_search(state):
    print(colored("---POSSIBLE SUB REDDITS---", 'green'))
    product = state["product"]
    subreddit_name_agent = subreddit_name_chain.invoke({"product": product})
    print(subreddit_name_agent)
    return {"sub_reddits_to_search": subreddit_name_agent}


def subreddit_selector(state):
    print(colored("\n\n---SUB-REDDITS SELECTOR---", 'green'))
    sub_reddits_to_search = state["sub_reddits_to_search"]
    product = state["product"]
    sub_reddits = search_subreddits(sub_reddits_to_search)
    subreddit_searcher_agent = subreddit_searcher_chain.invoke({"product": product, "sub_reddits": sub_reddits})
    print(subreddit_searcher_agent)
    print(colored(f"\nSub Reddits:\n\n{subreddit_searcher_agent}", 'green'))
    return {"sub_reddits_to_scrape": subreddit_searcher_agent}


def market_researcher(state):
    print(colored("\n---MARKET RESEARCHER---", 'green'))
    subreddits_to_scrape = state["sub_reddits_to_scrape"]
    product = state["product"]
    comments = reddit_comments(subreddits_to_scrape)
    print(colored("\n---Filtering Comments---", 'blue'))
    filtered_comments = filter_comments(comments[:1000])
    market_researcher_agent = market_researcher_chain.invoke({"filtered_comments": filtered_comments, "product": product})
    return {"market_research": market_researcher_agent}


def market_strategist(state):
    print(colored("\n---MARKET STRATEGIST---", 'green'))
    market_research = state["market_research"]
    product = state["product"]
    marketing_strategist_agent = marketing_strategist_chain.invoke({"market_researcher_agent": market_research, "product": product})
    print(marketing_strategist_agent)
    target_audiences = marketing_strategist_agent['Potential target audience']
    return {"marketing_strategy": marketing_strategist_agent, "target_audiences": target_audiences}


    

def campaign_crafter(state):
    print(colored("\n---CAMPAIGN CRAFTER---\n\n", 'green'))
    market_research = state["market_research"]
    marketing_strategy = state["marketing_strategy"]
    target_audience = state["target_audience"]
    product = state["product"]
    print(colored(f"Target Audience:\n{target_audience}", 'blue'))
    campaign_agent = campaign_chain.invoke({"product": product, "market_researcher_agent": market_research,
                                            "marketing_strategist_agent": marketing_strategy, "target_audience": target_audience})
    print(campaign_agent)
    return {"campaign": campaign_agent}


def landing_page_generator(state):
    print(colored("\n---LANDING_PAGE_GENERATOR---", 'green'))
    market_research = state["market_research"]
    marketing_strategy = state["marketing_strategy"]
    product = state["product"]
    campaign_agent = state["campaign"]
    landing_page_agent = landing_page_chain.invoke({"product": product, "market_researcher_agent": market_research,
                                                    "marketing_strategist_agent": marketing_strategy, "campaign_agent": campaign_agent})
    return {"landing_page": landing_page_agent}




if "product" not in st.session_state or st.button(":red[Clear]"):
    st.session_state["product"]= []
    st.session_state.clear()

def main():
    st.title("AI Market Researcher")

    product = st.text_input("Enter Product Details:")
    
    if product:
        st.subheader(":blue[PRODUCT]")
        
        st.write(product)
        
        st.subheader(":violet[You can edit the output before continuing to next step]")
        
    state = GraphState({"product": product})
    st.session_state.update({"product": product})

    # Step 1: Subreddit to Search
    if "sub_reddits_to_search" not in st.session_state:
        if st.button("Continue", key="step1"):
            st.session_state.update(subreddit_to_search(state))
    if "sub_reddits_to_search" in st.session_state:
        
        st.subheader(":blue[POSSIBLE SUBREDDITS]")
        sub_reddits_to_search = st.text_area("Sub Reddits to Search (add/remove as you find appropriate):", st.session_state["sub_reddits_to_search"])
        st.session_state["sub_reddits_to_search"] = sub_reddits_to_search

    # Step 2: Subreddit Selector
    if "sub_reddits_to_scrape" not in st.session_state and "sub_reddits_to_search" in st.session_state:
        if st.button("Continue", key="step2"):
            st.session_state.update(subreddit_selector(st.session_state))
    if "sub_reddits_to_scrape" in st.session_state:
        
        st.subheader(":blue[SELECTED SUBREDDITS TO SCRAPE]")
        sub_reddits_to_scrape = st.text_area("Sub Reddits to Scrape(add/remove as you find appropriate):", st.session_state["sub_reddits_to_scrape"])
        st.session_state["sub_reddits_to_scrape"] = sub_reddits_to_scrape

        # Step 3: Market Researcher
        if "market_research" not in st.session_state and "sub_reddits_to_scrape" in st.session_state:
            if st.button("Continue", key="step3"):
                st.session_state.update(market_researcher(st.session_state))
        if "market_research" in st.session_state:
            
            st.subheader(":blue[MARKET RESEARCH]")
            market_research = st.text_area("Market Research:", height=300, value=  st.session_state["market_research"])
            st.session_state["market_research"] = market_research      
            
            

        # Step 4: Market Strategist
        if "marketing_strategy" not in st.session_state and "market_research" in st.session_state:
            if st.button("Continue", key="step4"):
                st.session_state.update(market_strategist(st.session_state))
                
                
                
                #target_audiences = marketing_strategist['Potential target audience']
                #st.session_state.update({"target_audiences":target_audiences})
                #st.session_state["marketing_strategist"] = marketing_strategist
                
        if "marketing_strategy" in st.session_state:
            
            st.subheader(":blue[MARKETING STRATEGY]")
            #marketing_strategy = st.text_area("Marketing Strategy:", height=300, value= st.session_state["marketing_strategy"], key="1")
            
            #st.session_state["marketing_strategy"] = marketing_strategy
            marketing_strategy = st.session_state["marketing_strategy"]
            
            st.markdown(f"""
            **Name:** {marketing_strategy['Name']}\n
            **Colors:** {marketing_strategy['Colors']}\n
            **Font:** Heading: {marketing_strategy['Font']['Heading']}, Paragraph: {marketing_strategy['Font']['Paragraph']}\n
            **Product:** {marketing_strategy['Product']}\n
            **Features:**
            """)
            for feature in marketing_strategy['Features']:
                st.write(f"- {feature}")
            st.markdown("**Benefits:**")
            for benefit in marketing_strategy['Benefits']:
                st.write(f"- {benefit}")
            st.markdown("**Potential target audience:**")
            target_audiences = marketing_strategy['Potential target audience']
            for audience in target_audiences:
                st.write(f"- {audience['group']}")
            st.session_state["target_audiences"] = target_audiences


        # Step 5: Human in Loop for Target Audience Selection
        if "marketing_strategy" in st.session_state:
            
            
            
            target_audiences = st.session_state["target_audiences"]
            
            target_audience_mapping = { 
                f"Group: {ta['group']}": ta 
                for ta in target_audiences 
            }

            target_audience_display = list(target_audience_mapping.keys())

            st.subheader(":violet[Choose a Target Audience]")
            target_audience = st.radio("Audiences:", options=target_audience_display, index=None)

            if target_audience:
                st.session_state["target_audience"] = target_audience_mapping[target_audience]


                
                selected_audience = st.session_state.get('target_audience')
                if selected_audience:
                    st.write("Selected Audience:")
                    st.write(f"Group: {selected_audience['group']}")
                    


        # Step 6: Campaign Crafter
        if "campaign" not in st.session_state and "target_audience" in st.session_state:
            if st.button("Continue", key="step6"):
                st.session_state.update(campaign_crafter(st.session_state))
        if "campaign" in st.session_state:
            
            st.subheader(":blue[MARKETING CAMPAIGN]")
            campaign = st.text_area("Campaign:", height=300, value= st.session_state["campaign"])
            st.session_state["campaign"] = campaign

            # Step 7: Landing Page Generator
            if "landing_page" not in st.session_state and "campaign" in st.session_state:
                if st.button("Continue", key="step7"):
                    st.session_state.update(landing_page_generator(st.session_state))
            if "landing_page" in st.session_state:
                
                st.subheader(":blue[LANDING PAGE CONTENT]")
                st.write(st.session_state["landing_page"])
              

                # Save generated text
                product_title= product[:20]
                outputs = st.session_state

                        # Prepare content for download
                def prepare_download(outputs):
                    content = ""
                    for section, text in outputs.items():
                        content += f"{section} Output:\n"
                        content += f"{text}\n\n"
                    return content

                # Add a download button
                st.download_button(
                    label="Download Generated Texts",
                    data=prepare_download(outputs),
                    file_name=f"Saved_{product_title}.txt",
                    mime="text/plain"
                )


if __name__ == "__main__":
    main()
