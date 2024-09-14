import os

from datetime import date

from langchain_community.tools.tavily_search import TavilySearchResults

from google_serper import serper_search

import re
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_community.chat_models import ChatOllama, ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser


from dotenv import load_dotenv
load_dotenv()


os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY") #"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"
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

web_search_tool = TavilySearchResults(k=2, max_results=4)
#web_search_tool.invoke({"query": "latest Portland, Maine, United States "})




### LLM

local_llm = "llama3"
#llm = ChatOllama(model=local_llm, temperature=0.1)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)



## subreddit name chain


product = "AI personalized cold Email writer for business leads. Writes emaiil for every lead by researching on them using their website and linkedin "
# LLM
#llm = ChatOllama(model=local_llm,temperature=0.1)





info_collector_prompt = PromptTemplate(
    template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

### **Agent Role:**
You are the Startup Information Collector. Your role is to gather key details about the user's startup and ensure all essential information is provided before passing it on for the next steps.

### **Agent Mission:**
Ask the user questions to collect details about their startup. Your goal is to output responses with one sigle key "product" or "question":


---

### **Instructions:**

1. Questions to Ask the User:
   - What is the name of your agency? (Required)
   - What product or service does your business offer? (Required)
   - What industry does your business operate in? (Required)
   - What problem does your startup solve for its clients? (Required)
   - Please attach any competion website url if you know.
   

2. Logic for Responses:
   - If all required fields (name, product, industry, and problem) are provided, output with key 'product':
     ```json
     {
       "product": {
         "name": "[Startup Name]",
         "product_service": "[Product or Service]",
         "industry": "[Industry]",
         "problem_solved": "[Problem]"
         "Competition Website": "[url]"
       }
     }
     ```

   If some required information is missing, ask 'question' the user to provide it by stating what is missing:
    
     "Please provide more information about {missing field(s)}."
    

   Once the missing information is provided, re-check and either proceed with "product_details" or ask again until all required fields are filled.

3. JSON Output Format (if all required fields are complete):
   ```json
   {
       "product": {
         "name": "[Startup Name]",
         "product_service": "[Product or Service]",
         "industry": "[Industry]",
         "problem_solved": "[Problem]"
         "Competition Website": "[url]"
       }
     }
   ```

---

Key Considerations:
- Be polite and guide the user in a friendly manner.
- Ask one question at a time and ensure the user’s answers are clear.
- Loop back to the missing questions if any required information is incomplete.

---
    <|eot_id|><|start_header_id|>user<|end_header_id|>
    
    previously: {chat_history}
    
    USER: \n\n {prompt} \n\n <|eot_id|><|start_header_id|>assistant<|end_header_id|>
    """,
    input_variables=[ "prompt", "chat_history"],
)


info_collector_chain = info_collector_prompt | llm | JsonOutputParser()








subreddit_name_prompt = PromptTemplate(
    template=""" you are market researcher.
    
    Given the product information, understand the core product and the problem it solves.
    your task is to write five search words from the product that closely relates to the core product.\n\n
    
    
    such as:
    
    dog trainer
    medical billing
    ai chatbot
    
    
    
    Provide the keywords separated by comma and no preamble or explanation.
    
    
    
    product details: \n\n {product} \n\n 
    """,
    input_variables=[ "product"],
)


subreddit_name_chain = subreddit_name_prompt | llm | StrOutputParser()



### Reddit Searcher Chain

reddit_searcher_prompt = PromptTemplate(
    template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|> You are a reddit expert. you have been given some subreddits.
    
    only provide best 3 (three) subreddits that closely relates with the product information. Choose the sub reddits where we may find product users.
    do not create any name from yourself. 
    you have been given available subreddits from reddit search.
    choose only closely match with keywords of our product.
    
    Provide the subbreddits separated by comma without 'r/'. and no preamble or explanation.
    
    
    <|eot_id|><|start_header_id|>user<|end_header_id|>
    available subreddits:{sub_reddits}\n\n
    product: \n\n {product} \n\n <|eot_id|><|start_header_id|>assistant<|end_header_id|>
    """,
    input_variables=[ "product", "sub_reddits"],
)


subreddit_searcher_chain = reddit_searcher_prompt | llm | StrOutputParser()







web_summary_prompt = PromptTemplate(
    template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|> 
    
### **Agent Role:**
You are the Competitive Insights Summarizer. Your task is to gather and summarize key information from a competitor's website content. The output should be a concise, plain text summary of the business's key details, focusing on its products/services, target audience, and market positioning.

### **Agent Mission:**
Analyze the provided content from the competitor’s website and extract essential business information, which could be helpful for building our product. Summarizing it in plain text format.

---

### **Instructions:**

1. **Key Information to Extract:**
   - **Company Name**: Identify the name of the competing business.
   - **Product/Service Offerings**: Summarize the primary products or services the company offers.
   - **Target Audience**: Determine the audience the company is serving.
   - **Industry**: Identify the business's operating industry or market.
   - **Competitive Positioning**: Summarize how the business positions itself in the market (e.g., pricing, unique selling points, customer focus).
   - **Key Features/Benefits**: Highlight the key features or benefits of the company's products or services.


2. **Logic for Responses**:
   - If the website content provides sufficient information for all fields, the agent will output the full plain text summary.
   - If some details are missing or unclear, the agent should output the summary with the available details, and mark missing parts as “Unclear.”

3. **Guiding Questions for Summarization**:
   - What products or services does this company offer?
   - Who is their target audience or customer base?
   - In what industry or market is this business operating?
   - How does the company position itself competitively (e.g., pricing strategy, unique features, customer service)?
   - What are the key features or benefits that they highlight to their customers?



    <|eot_id|><|start_header_id|>user<|end_header_id|>
    competiton website:{web_text}\n\n
    oour product: \n\n {product} \n\n <|eot_id|><|start_header_id|>assistant<|end_header_id|>
    """,
    input_variables=[ "product", "web_text"],
)

web_summary_chain = web_summary_prompt | llm | StrOutputParser()






### Market Researcher Expert


market_researcher_prompt = PromptTemplate(
    template="""
    ## My goal

I'm looking for customer insights for my business idea:
“{product} ”

## Your role

You are a market researcher expert in finding customer insights

## Your mission

I'm either going to provide you with a copy and paste of Reddit posts from related subreddits, or, a list of YouTube comments from a related video (or any type of document).

Please extract any gold nuggets that I can use in my marketing.

## Instructions and formatting

I want to have the exact customer wording, create a simple list, and list all of them.

Use a Markdown block dto display your answer, nothing before, nothing after.

## EXTREMELY IMPORTANT

- Only select the sentences that have a direct link to my business idea
- Only mention short impactful sentence with wording that every person in my audience can rely to.
- DO NOT WRITE ANY SENTENCE THAT HAS NOT A DIRECT LINK WITH MY BUSINESS IDEA

## Format example
[
## (Give a name to the pain point)
“Gold nugget related to the pain point”
“Gold nugget related to the pain point”
“Gold nugget related to the pain point”

## (Give a name to the pain point)
“Gold nugget related to the pain point”
“Gold nugget related to the pain point”
“Gold nugget related to the pain point”

... ]



## Document to work from

{filtered_comments}

   
    """,
    input_variables=["filtered_comments", "product"],
)


market_researcher_chain = market_researcher_prompt | llm | StrOutputParser()



### Brand Strategist Chain



brand_strategist_prompt = PromptTemplate(
    template=""" 
    product: {product}\n

    Previous knowledge:
    {market_researcher_agent}\n
    
    
## Your role

You are a marketing strategist with a deep understanding of copywriting, psychological behaviors and Meta advertising.
You know perfectly the market analysis and advertising principles from 'Breakthrough Advertising' by Eugene M. Schwartz, and from David Ogilvy.

## Context

I’m in the process of validating a product idea using a Meta advertising campaign as well as a landing page.
At this stage, I only have very little knowledge about who is the customer and what do they really need., only the information previously mentioned in our conversation.

## Your mission

Your mission is to help me to craft the both the landing page and the advertising campaign by providing them with different potential target audiences, marketing angles and hooks, following the definitions and process described


## Methodology: Think step by step

1. Understand the insight provided earlier in this conversation
2. Think of potential markets the product/offer could address, the mass desires behind it, market awareness, and market sophistication
3. Think of the potential customers, who are they, what are they struggling with, what do they really want
4. Think of the best potential target audiences
5. Generate your answer

After gathering this information, generate a clear and simple product description that includes the following:

### Structure of your answer


Here is the structure to follow:

(

## Name

(Give it a nice but self explanatory name)

## Colors

(The background is going to be white, pick 1 HEX colors that fit the product, that should create a strong constrast to use on the call to action)

## Font

(Pick 2 Google fonts, one for heading, distinctive enough to create a real identity, and another more classic for paragraphs)

## Product

(Describe what the product is and what it does.)

### Features:

(List the 3 main potential features or components of the product.)

### Benefits

(Highlight the 3 potential key benefits the product provides.)

## Potential target audience

List 3 potenial niches/target audience for the product. From most important to least important

)

### Format

- [potential group of people] that are struggling with [a potential problem] that what to [achieve a potential goal]
- [potential group of people] that are struggling with [a potential problem] that what to [achieve a potential goal]
- ...

### Important

When picking an audience, be niche, be accurate, don't use broad useless audiences like "busy professional" or "health enthusiast", we want to address a specific part of a big market to solve a specific problem.

    respond in plain english, do not use brackets.
    
    """,
    input_variables=["market_researcher_agent", "product"],
)


brand_strategist_chain =  brand_strategist_prompt | llm | StrOutputParser()



branding_prompt = PromptTemplate(
    template="""
    
    product: {product}\n
    
    competition website: {web_summary_agent}
    
    About this domain: {google_summary}
    
    
    
    Previous knowledge:
    {market_researcher_agent}\n
    
    

## Your new mission

Your Role:
You are an expert in brand strategy and communications, specializing in helping businesses build compelling brands and messaging.

Your Mission:
Based on my business, industry, market research and market strategy, your task is to generate the following:

1. Company Briefing:
Summarize the core mission, vision, and values of my business.
Provide a brief overview of what the company offers and its unique position in the market.
Highlight the key problem my business solves for its target clients and why it matters.

2. Company Branding:
Develop the brand identity, including the tone, personality, and values that define my business.
Suggest elements like colors, fonts, and imagery that represent the brand.

3. Brand Story:
Craft a compelling narrative that explains the history, inspiration, and journey of the brand.
Include why the brand was created, its mission, and what drives it forward.
Ensure the story emotionally connects with the target audience, showing how the brand solves a critical problem for them.

4. Company/Brand Messages:
Create a series of concise and impactful brand messages that communicate the business's value proposition.
Develop key phrases or taglines that resonate with the target audience, addressing their needs and showcasing how the company provides the solution.
Ensure the messaging aligns with the brand's identity and tone.

Instructions:
Keep the tone professional but relatable to the target audience.
Ensure the company briefing and story are detailed but easy to understand.
Make sure the branding and messages are unique, memorable, and align with the company’s mission.
Example Format:

## Company Briefing:
[Company Briefing Summary]

## Company Branding:
- Brand Personality: [Description]
- Tone: [Description]
- Suggested Elements: [Colors, Fonts, Imagery]

## Brand Story:
[Narrative of the brand's journey, inspiration, and mission]

## Company/Brand Messages:
- Message 1: [Key message or tagline]
- Message 2: [Key message or tagline]
- Message 3: [Key message or tagline]

    
    """,
    input_variables=["product", "web_summary_agent","google_summary", "market_researcher_agent","brand_strategist_agent"],
)


# Chain
branding_chain = branding_prompt | llm | StrOutputParser()
