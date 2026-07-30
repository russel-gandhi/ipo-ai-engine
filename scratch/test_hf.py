import requests
import json

url = "https://datasets-server.huggingface.co/rows?dataset=sohomghosh%2FIndian_IPO_datasets&config=default&split=train&offset=0&length=10"
response = requests.get(url)
if response.status_code == 200:
    data = response.json()
    print(json.dumps(data['features'], indent=2))
    print(json.dumps(data['rows'][0], indent=2))
else:
    print(response.status_code)
