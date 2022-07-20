from newsdataapi import NewsDataApiClient

api = NewsDataApiClient(apikey = "pub_93536ec1f0b8d3847ada7bb60eedb0a2a7f6")

def getnews():
    response = api.news_api (q = 'stock market', country = "us")
    return response['results']


