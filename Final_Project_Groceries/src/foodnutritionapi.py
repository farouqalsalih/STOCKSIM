import requests

api_url = 'https://api.calorieninjas.com/v1/nutrition?query='

#api name calorie ninjas
#10,000 calls a month keep track of that i guess

def get_nutrition_data(querystring):
    response = requests.get(api_url + querystring, headers={'X-Api-Key': 'DHYTMZd4WuLvBig6WTIL7A==UV3sctHWPSAKkAH0'})
    if response.status_code == requests.codes.ok:
        print(response.text)
    else:
        print("Error:", response.status_code, response.text)

print(get_nutrition_data("apple"))