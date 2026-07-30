import requests
from bs4 import BeautifulSoup

url = "https://ipowatch.in/ipo-grey-market-premium-latest-ipo-gmp/"
headers = {'User-Agent': 'Mozilla/5.0'}
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

print("Title:", soup.title.string)
# Find the first few rows in a table
tables = soup.find_all('table')
if tables:
    for row in tables[0].find_all('tr')[:5]:
        cols = row.find_all(['th', 'td'])
        print([col.text.strip() for col in cols])
else:
    print("No tables found")
