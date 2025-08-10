import requests

endpoint = "http://localhost:8000/api/employer_api_view/"

data = {
    "nom":"Zidane",
    "email": "zidane@gmail.com",
}

response = requests.post(endpoint, json=data)

print(response.json())
print(response.status_code)