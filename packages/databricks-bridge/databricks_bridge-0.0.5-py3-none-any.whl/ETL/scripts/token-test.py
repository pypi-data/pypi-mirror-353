import requests

username = 'mat.shephard@y-tree.com'
password = 'aD7Z4sztr@8FpRl'
url = 'https://ms-cas.y-tree.com/oauth/token'
headers = {
  'Authorization': 'Basic Ym8tdXNlci1jbGllbnQ6MSNuZVdIZ347NTAvdDYu'
}

body = {'username':username,'password':password,'scope':'api.bo','grant_type':'password'}

response = requests.post(url=url,headers=headers,data=body)
print(response.json())