import os
import requests
import json
groq_api_key = os.getenv('GROQ_API_KEY')
headers = {'Authorization': f'Bearer {groq_api_key}', 'Content-Type': 'application/json'}
payload = {
    'model': 'llama-3.1-70b-versatile',
    'messages': [{'role': 'system', 'content': 'You output JSON.'}, {'role': 'user', 'content': 'Output valid JSON.'}],
    'response_format': {'type': 'json_object'},
    'temperature': 0.1
}
response = requests.post('https://api.groq.com/openai/v1/chat/completions', headers=headers, json=payload)
print(response.status_code, response.text)
