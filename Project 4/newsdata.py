from newsdataapi import NewsDataApiClient

api = NewsDataApiClient(apikey = "pub_93536ec1f0b8d3847ada7bb60eedb0a2a7f6")

user_in = str (input ("Enter a keyword: "))

response = api.news_api (q = user_in, country = "us")

for d in response ['results']:
    for key in d:
        print("{}: {}".format(key, d [key]))
    print("--------------------")
