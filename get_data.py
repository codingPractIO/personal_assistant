import requests
import json

# URL to send the GET request to
url = "https://suf.purs.gov.rs/v/?vl=A1lYSDhMTlNQWVhIOExOU1AgngAAFZ4AAEAaVwMAAAAAAAABlt36jPgAAAAUlq1%2FRXOe2F3L5D5KqjKAcJ2MDse27NscFA4lCGS46yYjmGDhD8IhaI4dpxXUI9sc4rCq2aDAW1UTBSunNPS1H8hNm9h6xvCkamyvwizpVmZuEQa9%2FQbQU5OS1Ym2m67egjEzz%2BjUgdXfZ2LyADDbgshbGbsoIFsXsCoqFvPLGXmh80vP3EKSRxX0blOj2MccRtd2jAVO5ZWj%2FGn4YzpFTSkhOSa9EBx43nDOX3%2BEY5GIZ%2Br5rQLXgVvxLaKAy%2BkoEhXrv9cBzmEXapf0tA6Fbc3%2FGPYBw6ZNxWOs322rpp68tu%2Bu9En%2BmYbDElAzITN5cld9t%2F9t%2FPz7F5hdluBeNIJ3BR2BNQ5RIdvcytd1bkhSij%2BDKkCj4%2FQ2KnLmCNmFvo2bQS7Yu%2Fev7xYqYyIX357TfoV1yCtQIFNpzxjUqIFYHDSg0omNecW7xQIxu52slxhBet9ueXmYrpwJrolIuK8YOAWUQYxqwguZ%2Fo2GvavHXJ7endUn6jbnnVqsbEiq%2BUDem%2BXeNjUMT%2BjT5pwicbst7xBS%2FgHGCDBaoZ7b3rt60CkFW7lZGJzz%2BKtBe3hVsnzIzU3L%2BBi88yL7zD8rO3TiTpEGDrfAC6F%2Bj1e%2FP70K7Xi1DlIiMK%2BaRFRjZGnm4ddT%2F1QTGGupT%2BeKw3YipyrCwtiEIvpeQvnMQy5N3Pm7V0Fxp2bMEQsU%2Fo8l8pI%3D"

# Headers for the request
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}

# Send the GET request
response = requests.get(url, headers=headers)

# Check if the request was successful
if response.status_code == 200:
    # Parse JSON response
    data = response.json()
    
    # Save to a file with proper encoding
    with open("/home/soimimozo/Code/VSCode/reciept_bot/response_vero.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print("Response saved to response.json with UTF-8 encoding. Code: {response.status_code}")
else:
    print(f"Request failed with status code {response.status_code}")
    print(response.text)
