import requests

url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=-33.8670522%2C151.1957362&radius=1500&type=restaurant&keyword=cruise&key=AIzaSyCKaLfaVA-hOcZXx1dnrPdGaB1nKCe0vOE"

payload={}
headers = {}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)