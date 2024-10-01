import requests

response = requests.get("http://127.0.0.1:5000/stream", stream=True)

for line in response.iter_lines():
    if line:
        print(line.decode('utf-8'))