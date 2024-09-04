import requests


url = f"http://127.0.0.1:5000/match"


response = requests.get(url)
print("Status Code:", response.status_code)
print("Response JSON:", response.json())
