from request import *
from utils import *


def main():
    url = "https://example.com/api/data"
    headers = {
        "User-Agent": "MyApp/1.0",
        "Accept": "application/json"
    }
    params = {
        "query": "test",
        "limit": 10
    }

    response = make_get_request(url, headers=headers, params=params)
    if response.status_code == 200:
        data = parse_json_response(response)
        processed_data = process_data(data)
        print(processed_data)
    else:
        print(f"Error: Received status code {response.status_code}")
        
if __name__ == "__main__":
    main()  