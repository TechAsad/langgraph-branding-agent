from graph import app

from termcolor import colored

# Define product
product = "AI RAG Chatbot for personal document question answering"


# Function to generate email
def market_research(product):
    inputs = {"product": product}
    output = app.invoke(inputs)  
    #market_strategy= output['marketing_strategy']
    landing_page= output['landing_page']
    return landing_page

product= input("Product Details:" )

landing_page = market_research(product)
print(colored(f"Target Audience:\n {landing_page}", 'cyan'))
