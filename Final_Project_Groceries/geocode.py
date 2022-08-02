import requests
from requests.structures import CaseInsensitiveDict

def getgeolocation(geostring):

    url = "https://api.geoapify.com/v1/geocode/search?"

    parameter = {'text' : geostring, 'apiKey' : '8a933966d21f44629f8f7f77fd7f5d92'}

    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"

    resp = requests.get(url, headers=headers, params=parameter)

    return(resp.json()["features"][0]["properties"])
