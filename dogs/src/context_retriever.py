import requests
import json

def ret(query, top_k=10):
    url = "http://154.26.128.4:9060/get_relevant_document"

    payload = json.dumps({
        "kb_id": "26c9a465-f3af-4b91-91e0-7731c9b1403c",
        "query": query,
        "top_k": top_k
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    return json.loads(response.text)['data']