import time
import json
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

URL = 'https://gateway-529295899189.us-east1.run.app/api/chat'
HEADERS = {'Content-Type': 'application/json'}

def send_request(idx):
    payload = {
        'message': f'Dime una sola palabra inventada corta #{idx}',
        'session_id': f'test-concurrency-{idx}'
    }
    print(f'Sending request {idx}...')
    start = time.time()
    try:
        resp = requests.post(URL, headers=HEADERS, json=payload, timeout=60)
        elapsed = time.time() - start
        print(f'Request {idx} finished in {elapsed:.2f}s with status {resp.status_code}')
        if resp.status_code == 200:
            data = resp.json()
            response_text = data.get('response', resp.text)
            print(f'  Response {idx}: {response_text.strip()[:60]}...')
        else:
            print(f'  Error {idx}: {resp.text}')
        return resp.status_code
    except Exception as e:
        print(f'Exception in request {idx}: {e}')
        return 500

def main():
    print('Starting concurrency test (5 simultaneous requests)...')
    start_time = time.time()
    results = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(send_request, i) for i in range(1, 6)]
        for future in as_completed(futures):
            results.append(future.result())
            
    total_time = time.time() - start_time
    print(f'\nTest finished in {total_time:.2f}s')
    print(f'Success count (200 OK): {results.count(200)}')
    print(f'Failed count: {5 - results.count(200)}')

if __name__ == '__main__':
    main()
