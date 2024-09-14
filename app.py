import streamlit as st
from termcolor import colored
from typing_extensions import TypedDict
from chains import *
from tools import *  # reddit scraper and comment cleaner
from graph import app
from node import *
# Define the GraphState class


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
    brand_strategy: dict
    branding: str
   


st.set_page_config(page_title='Branding Agent', page_icon="technologist")


# Define the nodes


def google_search(state):
    
    
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
    
    print(colored(f"\n---MARKET STRATEGIST---", 'green'))
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


if "product" and "branding" not in st.session_state:
    st.session_state["product"]= []
    st.session_state["branding"]= []
    
    st.session_state.clear()



import streamlit as st

def main():
    st.title("Branding Agent")

    # Step 1: Gather Product Information
    st.header("Enter Product Details")

    # Use session state to maintain input values across reruns
    product_name = st.text_input("Startup Name", value=st.session_state.get('product_name', ''))
    product_service = st.text_input("Product or Service", value=st.session_state.get('product_service', ''))
    industry = st.text_input("Industry", value=st.session_state.get('industry', ''))
    problem_solved = st.text_input("Problem Solved", value=st.session_state.get('problem_solved', ''))
    competition_website = st.text_input("Competition Website", value=st.session_state.get('competition_website', ''))

    # Check if the product details have changed
    details_changed = (
        product_name != st.session_state.get('product_name') or
        product_service != st.session_state.get('product_service') or
        industry != st.session_state.get('industry') or
        problem_solved != st.session_state.get('problem_solved') or
        competition_website != st.session_state.get('competition_website')
    )

    # Validate the input
    if st.button("GENERATE"):
        if not (product_name and product_service and industry and problem_solved and competition_website):
            st.error("Please provide all required information.")
        else:
            # Store product details in session state
            product_details = f"""
            Product Details:
            - Startup Name: {product_name}
            - Product or Service: {product_service}
            - Industry: {industry}
            - Problem Solved: {problem_solved}
            - Competition Website: {competition_website}
            """

            # Update session state to remember inputs and product details
            st.session_state.update({
                "product": product_details,
                "product_name": product_name,
                "product_service": product_service,
                "industry": industry,
                "problem_solved": problem_solved,
                "competition_website": competition_website
            })

            # Check if branding needs to be regenerated
            if details_changed or "branding" not in st.session_state:
                # Simulate branding generation using app.invoke (replace with actual function)
                with st.spinner(text="Generating, Please Wait!"):
                    inputs = {"product": st.session_state["product"]}
                    output = app.invoke(inputs)  # Replace with actual invoke logic
                    generated_branding = output['branding']

                    # Store branding in session state
                    st.session_state["branding"] = generated_branding
            else:
                st.success("Already Generated")

            # Display product details and branding
            st.subheader(":blue[PRODUCT DETAILS]")
            st.write(st.session_state["product"])

            if "branding" in st.session_state:
                st.subheader(":blue[BRANDING]")
                st.write(st.session_state["branding"])

            # Option to download branding details
            def prepare_download(outputs):
                return outputs

            st.download_button(
                label="Download Branding Strategy",
                data=prepare_download(st.session_state["branding"]),
                file_name=f"{product_name}_Branding.txt",
                mime="text/plain"
            )




def main2():
    st.title("Branding Agent")

    # Step 1: Gather Product Information
    st.header("Enter Product Details")

    # Use session state to maintain input values across reruns
    product_name = st.text_input("Startup Name", value=st.session_state.get('product_name', ''))
    product_service = st.text_input("Product or Service", value=st.session_state.get('product_service', ''))
    industry = st.text_input("Industry", value=st.session_state.get('industry', ''))
    problem_solved = st.text_input("Problem Solved", value=st.session_state.get('problem_solved', ''))
    competition_website = st.text_input("Competition Website", value=st.session_state.get('competition_website', ''))

    # Validate the input
    if st.button("GENERATE"):
        if not (product_name and product_service and industry and problem_solved and competition_website):
            st.error("Please provide all required information.")
        else:
            # Store product details in session state
            product_details = f"""
            Product Details:
            - Startup Name: {product_name}
            - Product or Service: {product_service}
            - Industry: {industry}
            - Problem Solved: {problem_solved}
            - Competition Website: {competition_website}
            """

            # Update session state to remember inputs and product details
            st.session_state.update({
                "product": product_details,
                "product_name": product_name,
                "product_service": product_service,
                "industry": industry,
                "problem_solved": problem_solved,
                "competition_website": competition_website
            })
            if "product" in st.session_state:
                st.subheader(":blue[PRODUCT DETAILS]")
                st.write(st.session_state["product"])
            if "branding" in st.session_state:
                st.subheader(":blue[BRANDING]")
                st.write(st.session_state["branding"])

                # Display product details
                #st.subheader(":blue[PRODUCT DETAILS]")
                #st.write(st.session_state["product"])
            else:
                # Simulate branding generation using app.invoke (replace with actual function)
                with st.spinner(text="Generating, Please Wait!"):
                    inputs = {"product": st.session_state["product"]}
                    output = app.invoke(inputs)  # Replace with actual invoke logic
                    generated_branding = output['branding']

                    # Store branding in session state
                    st.session_state["branding"] = generated_branding

                    # Display branding output
                    #st.subheader(":blue[BRANDING]")
                    #st.write(st.session_state["branding"])

                    # Option to download branding details
                    
        # Ensure product details and branding persist even if the user downloads the file
    

        
            
            def prepare_download(outputs):
                            return outputs

            st.download_button(
                label="Download Branding Strategy",
                data=prepare_download(st.session_state["branding"]),
                file_name=f"{product_name}_Branding.txt",
                mime="text/plain"
            )


# Run the app
if __name__ == "__main__":
    main()
        
            
