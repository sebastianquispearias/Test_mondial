from requests.structures import CaseInsensitiveDict
import requests

# Registers Acess Token
def save_token(filename='token'):
    url='https://login.alis.solutions/oauth/token'
    headers=CaseInsensitiveDict()
    headers['Content-Type']='application/x-www-form-urlencoded'
    headers['Cookie']='did=s%3Av0%3Af497f6d0-dcf9-11ec-adb4-9fd98fb1a849.ArEBYZVQ630LVp9F279pc6htS5kZDOiEezaSnYBfU7g; did_compat=s%3Av0%3Af497f6d0-dcf9-11ec-adb4-9fd98fb1a849.ArEBYZVQ630LVp9F279pc6htS5kZDOiEezaSnYBfU7g'
    payload='grant_type=http%3A%2F%2Fauth0.com%2Foauth%2Fgrant-type%2Fpassword-realm&username=supermercadomundial%40alis-sol.com.br&password=supermercadomundial%40123&audience=https%3A%2F%2Fworkflows.alis.solutions&scope=&client_id=k9Gc3n6pikzqjituSsvrq9PFDnSJolSo&client_secret=dbYwOcK9wmio7SiVRqdY34G-IdNdRb8_fGmVJCNhf1HZ04Fo-NyqNYajRqxNfJsw&realm=workflows'
    resp = requests.post(url, headers=headers, data=payload)
    data = resp.json()
    token = data['access_token']

    with open(filename, 'w') as file:
        file.write(token)  
    return token