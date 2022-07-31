import requests
def getphoto(searchtext):
    r = requests.post(
        "https://api.deepai.org/api/text2img",
        data={
            'text': searchtext,
        },
        headers={'api-key': 'bbcea0ef-9684-48ed-b9b3-d2533812214e'}
    )   
    r = r.json()
    return r["output_url"]

print(getphoto("apple"))
