import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv('.env')

def refine_commentary(raw_commentary):
    import requests

    api_key = os.getenv("API_KEY")

    comm = raw_commentary

    example_input = 'Zampa to Babar, Good length, Leg stump, Babar plays at Fine Leg region. Wicket. Now 175 for 3'
    example_output = 'Zampa to Babar, Zampa placed the ball on good length and leg stump and Babar plays it at fine leg. Oh no Babar has to walk back to pavilion. After this loss score becomes 175 for 3'

    url = 'https://api.pawan.krd/v1/chat/completions'
    headers = {
        'Authorization': f'{api_key}',
        'Content-Type': 'application/json',
    }
    data = {
        "model": "pai-001",
        "max_tokens": 200,
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant. Improve the grammar and follow the structure of the example provided. Do not include the word 'Example' in the response."
            },
            {
                "role": "user",
                "content": f"Revise the sentence and enhance the description: {comm}. Example: {example_input} Output: {example_output}"
            }
        ]
    }
    
    response = requests.post(url, headers=headers, json=data)

    output = ''
    try:
        output = response.json()['choices'][0]['message']['content']
    except:
        output = response.json()

    print(output)
    return output
