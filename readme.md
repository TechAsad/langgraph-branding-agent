# Market Researcher AI Application

This application is a Market Researcher AI that helps generate marketing strategies, campaigns, and landing pages based on the input product details. It guides users through various stages of market research, providing outputs at each step and allowing user interaction to refine the results.

## Features

- Identify potential subreddits for market research.
- Select relevant subreddits for scraping.
- Generate market research reports.
- Develop marketing strategies.
- Allow user input to choose the target audience.
- Create marketing campaigns.
- Generate landing pages based on the campaign.

## Getting Started

### Prerequisites

- Python 3.11
- Streamlit
- Docker (for Docker-based setup)

### Installation

#### Clone the Repository


## crate your env file in the same folder (.env)

OPENAI_API_KEY= 
SERPER_API_KEY= 
TAVILY_API_KEY=



```sh
git clone https://github.com/yourusername/market-researcher-ai.git
cd market-researcher-ai

## With Docker ###
docker build -t market-research-app .

docker-compose up --build

## Without Docker ###

##Create and activate a virtual environment:
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

pip install -r requirements.txt
streamlit run app.py

##Open your web browser and navigate to http://localhost:8501 to access the app.

```


## Application Workflow
```
Enter Product Details: The user inputs the product details.

Subreddit Selection: The application suggests possible subreddits related to the product and allows the user to select relevant ones.

Market Research: The app scrapes comments from the selected subreddits and generates a market research report.

Marketing Strategy: Based on the market research, the app creates a marketing strategy.

Select Target Audience: The user selects the target audience from the suggested options.

Campaign Creation: The app generates a marketing campaign for the selected audience.

Landing Page Generation: The final step is generating a landing page based on the campaign.
```