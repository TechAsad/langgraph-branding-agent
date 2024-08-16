import requests
from bs4 import BeautifulSoup

def get_quora_questions(query):
    url = f'https://www.quora.com/search?q={query.replace(" ", "+")}'
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print("Failed to retrieve data")
        return []
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extract questions and answers
    questions = []
    for item in soup.find_all('div', class_='q-box qu-mb--tiny'):
        question = item.find('span')
        answer_snippet = item.find('div', class_='q-box qu-mt--tiny qu-cursor--pointer')
        if question and answer_snippet:
            questions.append({
                'question': question.text.strip(),
                'answer_snippet': answer_snippet.text.strip()
            })
        
        if len(questions) >= 10:
            break
    
    return questions

query = "How does AI work in inventory management?"
questions = get_quora_questions(query)

for i, q in enumerate(questions, 1):
    print(f"{i}. Question: {q['question']}")
    print(f"   Answer Snippet: {q['answer_snippet']}")
    print("-" * 80)
