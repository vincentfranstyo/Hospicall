import requests

url_real = 'https://ca-sereneapp.braveisland-f409e30d.southeastasia.azurecontainerapps.io/'
url_dummy = 'http://127.0.0.1:3000/'


def get_token():
    token_url = url_dummy + 'auth/token'
    token_response = requests.post(token_url, data={'username': 'johndoe', 'password': 'password123'})
    token = token_response.json().get('access_token')
    return token
