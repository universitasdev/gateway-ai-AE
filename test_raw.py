
import os
import google.auth
from google.auth.transport.requests import Request
import requests

creds, _ = google.auth.default()
if not creds.valid:
    creds.refresh(Request())

project_id = '951100463087'
location = 'us-east1'
engine_id = '6284579765949038592'
url = f'https://{location}-aiplatform.googleapis.com/v1beta1/projects/{project_id}/locations/{location}/reasoningEngines/{engine_id}:streamQuery'

headers = {'Authorization': f'Bearer {creds.token}', 'Content-Type': 'application/json'}
payload = {'classMethod': 'stream_query', 'input': {'message': 'hola', 'user_id': 'test-session-local'}}

print('Sending request to:', url)
response = requests.post(url, headers=headers, json=payload)
print('Status:', response.status_code)
print('Response text:')
print(repr(response.text))

