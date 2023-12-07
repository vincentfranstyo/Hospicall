from Utils.api_auth import get_token
import requests

url_real = 'https://ca-sereneapp.braveisland-f409e30d.southeastasia.azurecontainerapps.io/'
url_dummy = 'http://127.0.0.1:3000/'


def get_psychologist_list():
    headers = {'Authorization': f'Bearer {get_token()}'}
    psychologist = requests.get(url_real + 'psychologist/', headers=headers)
    return psychologist.json()


def get_psycho_by_id(psycho_id: int):
    headers = {'Authorization': f'Bearer {get_token()}'}
    psychologist = requests.get(url_real + 'psychologist/{psychologist_id}?psy_id=' + str(psycho_id), headers=headers)
    return psychologist.json()
