import urllib.request, json
url = 'https://gateway-529295899189.us-east1.run.app/api/chat'
data = json.dumps({'message': 'Hola, funciona?', 'session_id': 'test2'}).encode('utf-8')
req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
try:
    with urllib.request.urlopen(req) as response:
        print(response.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print('HTTPError:', e.code, e.read().decode('utf-8'))

