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
    
    only provide best 7 (seven) subreddits that closely relates with the product information. Choose the sub reddits where we may find product users.
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



### Marketing Strategist Chain


marketing_strategist_prompt = PromptTemplate(
    template=""" 
    product: {product}\n
    Previous knowledge:
    {market_researcher_agent}\n
    
    
## Your rôle

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

List 3 potenial niches/target audience for the product. From most important to least important with key: 'Potential target audience', and each audience with key: 'group'

)

### Format

- [potential group of people] that are struggling with [a potential problem] that what to [achieve a potential goal]
- [potential group of people] that are struggling with [a potential problem] that what to [achieve a potential goal]
- ...

### Important

When picking an audience, be niche, be accurate, don't use broad useless audiences like "busy professional" or "health enthusiast", we want to address a specific part of a big market to solve a specific problem.
   
   
   all information in json with relevant keys. 
   
    
    
    """,
    input_variables=["market_researcher_agent", "product"],
)


marketing_strategist_chain = marketing_strategist_prompt | llm | JsonOutputParser()




### Campaign Crafter Chain


prompt = PromptTemplate(
    template="""
    
    product: {product}\n
    
    Previous knowledge:
    {market_researcher_agent}\n
    
    {marketing_strategist_agent}\n
    
    
    
   From now on, only work with the following potential target audience:
    {target_audience}

## Your new mission

From all the informations in the conversation above, your new mission is to help the user to craft the campaign by providing them with:
- A more accurate definition of the chosen audience
- Their situation (related through market analysis from Breakthrough Advertising)
- Their deep pain point
- Their potential objections

## Structure

USE A MARKDOWN BLOCK TO WRITE YOUR ANSWER NOTHING BEFORE, NOTHING AFTER

Here is the structure to follow:

[

# [Audience Name]

[Expand the definition]
([potential group of people] that are struggling with [a potential problem] that what to [achieve a potential goal])

## Situation

*Market Desire:* (Identify the dominant desire the product fulfills, we are talking here of a deep desire (cf breakthrough advertising), not something obvious that the product does)

*Awareness Level:* (Determine how familiar the audience is with the problem, the solution, and the product.)

*Sophistication Level:* (Assess how familiar the audience is with competing solutions and how complex their needs are.)
(market desire: We are talking here of a deep desire (cf breakthrough advertising), not something obvious that the product does)
(awareness level & Sophistication level: Make it actionable one clear sentence with a quick advice to approach advertising (cf breakthrough advertising))

#### Deep pain point

(List the 3 main problem that [audience] is facing regarding [product])

#### Potential objection

(List the 3 potential objections that [audience] could have when it comes to buying [product])

]
    
    """,
    input_variables=["product", "comment_organizer_agent","copywriter_agent", "target_audience"],
)


# Chain
campaign_chain = prompt | llm | StrOutputParser()




### Landing Page Chain

landing_page_prompt = PromptTemplate(
    template="""
    
    product: {product}\n
    
    Previous knowledge:
    
    {market_researcher_agent}\n
    
    {marketing_strategist_agent}\n
    
    Target Audince:
    {campaign_agent}\n\n

## Your new mission

From all the informations in the conversation above, your new mission is to help the user to craft the landing page to display the product/offer.
The landing page is using the Before-After-Bridge copywriting framework

IT IS EXTREMELY IMPORTANT THAT YOU USE THE WORDING OF THE CUSTOMER AS MUCH AS POSSIBLE IN YOUR COPY

### Think step by step

1. Summarize the conversation for yourself
2. Think of the potential target audience, who are the customers, what are their current believes, what are they struggling with, what do they really want, what have they potentially tried to solve the problem
3. Generate your answer

## Basic rules for crafting landing pages

- Be crystal clear in your writing - Don’t assume “they will understand”, write simple things, do not use metaphores.
- Write for a 10 years old - Avoid jargon at all cost use only simple words and formulation.
- Say everything in the titles, back it up with the paragraphs - Most people only scan the page, everything should be said only with the titles.
- No one cares about the product, people care about themselves - Write using “You” or “Your” not “Us”, customer centric.
- Write with one single person in mind.
- Create mental pictures as much as possible, the more the visitor visualize a situation they can relate to, the more likely they will understand the benefits the product can bring them.
- If possible, pick a side, declare an ennemy, it's us versus them, do it subltely.
- Never use buzzword, or power verbs like unleash, unveil, discover, unlock and all similar bullshit words

## Definitions
[
### Above the fold

The Above the fold part of the landing page is the first part the visitors sees when landing on the page, before scrolling. This section should should contain all the pieces, the visitor should understand they are in the right place in a blink of an oeil.
It contains the following pieces

#### Headline


ALWAYS USE THE WORDS OF THE CUSTOMERS IN THE HEADLINE
Here are 3 types of headlines that work well:

1. Short straight to the point headlines

Good short straight to the point headlines describe what the business does in a super creative way. They don't use buzzwords. They're short and consumable, while generating curiosity. They orient towards the business outcomes that customers would get. 

2. Question headlines

Question headlines are a simple question making the visitor directly connect to a specific situation or relate to a fact they know about, related to the problem the product/offer solves, If possible make the visitor visulaze a scene they are familiar with or trigger an emotion.

3. The desired outcome headlines

Desired outcome headlines are short and designed to make the visitor feel the emotion they would feel if they finally solve the problem the product/offer is solving. It's not about the direct benefits of the product/offer, it's about how would their life look like once the problem is solved and how would they feel about that


#### Subheadline

The subheadline is meant to be placed right below the headline and should describe the solution for the target audience in a more objective way so the visitor knows exactly what to expect. It should confirm the user expectation by mentioning clearly for who it is for and what the product/offer does, if possible by adding some uniqueness or time period, and always make it feel easy as a breath.

#### Bullet points

Generally, depending on the product/offer, the above the fold will contain 3-5 bullet points
They are short (about 15 words) and straight to the point stating a benefits the customer will get backed up with a feature from the product

Example: "
Learn how to relieve your jaw tension and feel refreshed and ready to face the day in the morning.
Experience deep relaxation and improved mobility in the jaw, head and neck area
Discover how a new jaw feeling fundamentally improves your quality of life.
"

#### Call to action

The call to action is the text of a button to go to the next step, it should be very short, and adapted to any kind of next step

Example:
"
- Tell me more!
- Yes, I want...
- Find out if [product] is made for you?
"

### Message from the founder

Since we don't have testimonial yet, this section is going to show a sentence from the founder to humanize and rationalize the product/offer, it should act as if it would be a testimonial but it's not, it is directly from the founder.


### The current situation (Before)

This section is the "Before" in the BAB copywriting framework.
It should described vividly the current situation and pain of the visitor, using visual words, creating images and linking them to the effect that these situation have on their life.
The goal is to clearly picture the life of the customer with the pain, and the believes they have, and what solution they already tried, so we can deconstruct these believes.

It contains:

#### A title grabbing attention

Like "Does any of this ring a bell?", "Do you know that?"


#### 3 title-paragraph blocks

All containing a short and vivid description of scene the customer can rely to, that shows them in the pain related to the product.
"Every night, you lie awake, your mind racing with worries. The insomnia keeps you tossing and turning, frustration building as the hours slip by without sleep."

### A Believes deconstruction block

The goal here is to get the customer where they are with one current belief, aknoledge it and explain why it is wrong.
Mention the solution they have tried to solve the problem, and back it up with scientific studies if possible, or with a statement.

#### Believes deconstruction - headline

It starts by a statement like "You are not alone", or "In fact 80% of the population..."

#### Believes deconstruction - paragraph

Then comes a short paragraph to further expand the headline.

### Message from the founder

Same principle as previous message

### Desired outcome (After)

This section is the "after" from the BAB copywriting framework.
It is the exact opposite of the "Before", it should describe how the customer's life would look like after they obtained the result provided by the product/offer.

Some clarification to avoid confusion:
"
Problem: Muscle tension creating pain
Solution: A course that teaches you to relax every muscle of your body
Benefits: Pain free, you feel better
Desired outcome: Finally play with your grankids and enjoy life on your own terms
"

It contains:

#### A title grabbing attention

Like "And now, imagine..."

#### 3 title-paragraph blocks

All containing a short description of the scene and a small text like "You start every morning positive and full of energy - You enjoy breakfast, are in a good mood and start the day with a positive attitude. This new morning routine will not only boost your self-confidence, but also improve your overall mood and boost your social and professional interactions."

### A new paradigm block

We deconstructed the customers believes earlier in the page, now it's time to reconstruct new believes by introducing something they haven't thought about before,a new way,  a new vehicule to move from the place they are to the place they want to be. We are not introducing the solution or the product yet, only 

##### New paradigm - Healdline

Should be directly related to the "Believes deconstruction"

Here is an example: "Introducing [Product] A new way...

##### New paradigm - paragraph

Backing up the headline, explaining why this solution is different and can make a real change, based on the secret sauce
Not only we explain it but we want the solution to feel like it's a new paradigm, a new solution that is going to solve their problem.
Following the deconstruction of the believes, the construction of the new ones, and the introduction of the uniqueness of the solution, the paragraph should rationalize the excitment of finding out this new believe by facts, if possible backed up by science


#### Solution 3-Steps blocks

Each of these blocks are made from a Title and a short paragraph.
Depending on the product/offer, it can be a 3-steps blocks showing the different steps to get from current to new situation, or, if it is not possible, the blocks should emphasize the benefits of the solution, backed up by the features of the solution


### Message from the founder

Same principle as previous message


### Connection block

This block is made to define the WHY behing the product/offer, while, at the same time, creating a connection between the founder and the customer.
It is made with a Picture of the founder, a catchy headline and a paragraph

#### Connection block headline

Own words of the founders shortly explaining why the idea of creating this new product came up

#### Connection block paragraph

A semi-long paragraph telling the story and experience of the founder leading them to create the solution, in their own words.

### Last call to action

At this step, the customer went through all the emotion phases, and understand perfectly what the product/offer does, and how it will change their life.
This block is the last push to rationally make them take the next step.

#### Last call to action Headline

A short sentence pushing on the timing to change, to take the next step

#### Last call to action Subheadline

A short sentence backing up the headline

#### Last call to action CTA

A clear action (button text)
]



### The format of your answer

DO NOT USE EMOJIES
USE A MARKDOWN BLOCK TO WRITE YOUR ANSWER NOTHING BEFORE, NOTHING AFTER
JUST WRITE THE ANSWER (e.g. do not write "Hook 1: This is the hook", instead write: This is the hook)

Example format for the campaign structure:

[
Title: Landing page for [Product/offer name]
- Above the fold
	- Headline
		- Short straight to the point headlines
			- [Short straight to the point headline version 1]
			- [Short straight to the point headline version 2]
		- Question headlines
			- [Question headline version 1]
			- [Question headline version 2]
		- Desired outcome headlines
			- [Desired outcome headline version 1]
			- [Desired outcome headline version 2]
	- Subheadline
		- [Subheadline version 1]
		- [Subheadline version 2]
	- Bullet points
		- [Bullet point 1]
		- [Bullet point 2]
		- [Bullet point 3]
		- [Bullet point 4]
		- [Bullet point 5]
		- [Bullet point 6]
	- Call to action
		- [Call to action version 1]
		- [Call to action version 2]
		- [Call to action version 3]
- Message from the founder
	- [Message from the founder]
- The current situation
	- Title grabbing attention
		- [Title grabbing attention version 1]
		- [Title grabbing attention version 2]
	- Title-paragraph blocks
		- [Title-paragraph block version 1]
		- [Title-paragraph block version 2]
		- [Title-paragraph block version 3]
		- [Title-paragraph block version 4]
- Believes deconstruction block
	- Believes deconstruction - headline
		- [Believes deconstruction - headline]
	- Believes deconstruction - paragraph
		- [Believes deconstruction - paragraph]
- Message from the founder
	- [Message from the founder]
- Desired outcome
	- Title grabbing attention
		- [Title grabbing attention version 1]
		- [Title grabbing attention version 2]
	- Title-paragraph blocks
		- [Title-paragraph block version 1]
		- [Title-paragraph block version 2]
		- [Title-paragraph block version 3]
		- [Title-paragraph block version 4]
- New paradigm block
	- New paradigm - headline
		- [New paradigm - headline]
	- New paradigm - paragraph
		- [New paradigm - paragraph (Starting with for example: "this is not just another..." This section is about how this new solution will help the customer, don't use "our product", about 70 words)]
- Solution
	- Solution 3-Steps blocks
			- [Solution 3-Steps block 1 ]
			- [Solution 3-Steps block 2]
			- [Solution 3-Steps block 3]
- Message from the founder
	- [Message from the founder]
- Connection block
		- [Connection block headline]
		- [Connection block paragraph]
- Last call to action
		- [Last call to action Headline]
		- [Last call to action Subheadline]
		- [Last call to action CTA]
]    
    """,
    input_variables=["product","market_researcher_agent","marketing_strategist_agent", "campaign_agent"],
)


# Chain
landing_page_chain = landing_page_prompt | llm | StrOutputParser()



