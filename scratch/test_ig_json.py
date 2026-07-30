import requests
from bs4 import BeautifulSoup
import json

url = "https://www.investorgain.com/report/live-ipo-gmp/331/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
}
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

script = soup.find('script', id='__NEXT_DATA__')
if script:
    data = json.loads(script.string)
    # Print the keys of the JSON to see structure
    print("Found NEXT DATA")
    try:
        # Usually it's in props -> pageProps
        print(data['props']['pageProps'].keys())
    except:
        print("Keys:", data.keys())
else:
    print("No __NEXT_DATA__ found")
    # Maybe look for table elements manually
    divs = soup.find_all('div', class_=lambda c: c and 'table' in c.lower())
    print(f"Found {len(divs)} divs with 'table' class")
    
    # Try finding rows
    rows = soup.find_all('tr')
    print(f"Found {len(rows)} <tr> tags")
    if len(rows) > 0:
        print(rows[1].text)
