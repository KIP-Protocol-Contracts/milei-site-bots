import requests
import json

def ret(query, top_k=10):
    url = "http://154.26.128.4:9060/get_relevant_document"

    payload = json.dumps({
        "kb_id": "d548c0d8-2bd3-4251-8e79-d835d290fbf4",
        "query": query,
        "top_k": top_k
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    return json.loads(response.text)['data']

def ret_yat(query, top_k=10):
    url = "https://opencampus-university-be-2.fly.dev/context-ret/get_relevant_document"

    payload = json.dumps({
        "kb_id": "f47f5f14-cc12-40a5-a3c7-4091acf789e4", # yat id pkl 
        "query": query,
        "top_k": top_k
        })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    return json.loads(response.text)['data']