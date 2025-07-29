import requests

API_KEY = "cpk_26741293aa4f4b5c830b38856af3292b.73e768f43e39549f92100ec86342d3dd.CcF7pgLIteGp4NJWYPqg7zs53Dju8RQz"
API_URL = "https://llm.chutes.ai/v1/chat/completions"
MODEL = "deepseek-ai/DeepSeek-V3-0324"

def request(message: str, system: str = "You are a helpful assistant.") -> str:
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": message}
        ]
    }
    response = requests.post(API_URL, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        raise Exception(f"Error {response.status_code}: {response.text}")
