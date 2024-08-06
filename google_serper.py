import os
import json
import requests



from dotenv import load_dotenv
load_dotenv()


serper_api = os.getenv("SERPER_API_KEY") #"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"


def format_results(organic_results: str) -> str:
    result_strings = []
    for result in organic_results:
        title = result.get('title', 'No Title')
        link = result.get('link', '#')
        snippet = result.get('snippet', 'No snippet available.')
        result_strings.append(f"Title: {title}\nLink: {link}\nSnippet: {snippet}\n---")
    
    return '\n'.join(result_strings)

def serper_search(query: str) -> str:
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.yaml')
    
    search_url = "https://google.serper.dev/search"
    headers = {
        'Content-Type': 'application/json',
        'X-API-KEY': serper_api  # Make sure to set this environment variable
    }
    payload = json.dumps({"q": query})
    
    try:
        response = requests.post(search_url, headers=headers, data=payload)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4XX, 5XX)
        results = response.json()
        
        if 'organic' in results:
            formatted_results = format_results(results['organic'])
            return formatted_results
        else:
            return "No organic results found."

    except requests.exceptions.HTTPError as http_err:
        return f"HTTP error occurred: {http_err}"
    except requests.exceptions.RequestException as req_err:
        return f"Request error occurred: {req_err}"
    except KeyError as key_err:
        return f"Key error occurred: {key_err}"
    except json.JSONDecodeError as json_err:
        return f"JSON decoding error occurred: {json_err}"

# Example usage
if __name__ == "__main__":
    search_query = "latest Portland, Maine, United States "
    results = serper_search(search_query)
    print(results)