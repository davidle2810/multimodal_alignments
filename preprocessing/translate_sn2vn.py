import json
import requests

def sn_transliteration_api(text):
    headers = {"User-Agent": "transliteration"}
    url_transliteration = "https://tools.clc.hcmus.edu.vn/api/web/clc-sinonom/sinonom-transliteration"
    data = {"text":text}
    response = requests.post(url_transliteration, headers=headers, json=data)  
    data = json.loads(response.text)
    if data['is_success']:
        result_text = data['data']['result_text_transcription']
    return result_text
