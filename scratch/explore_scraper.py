import requests
from bs4 import BeautifulSoup

res = requests.get('https://ipowatch.in/ipo-grey-market-premium-latest-ipo-gmp/', headers={'User-Agent': 'Mozilla/5.0'})
soup = BeautifulSoup(res.text, 'html.parser')

links = []
for tr in soup.find_all('tr')[1:10]:  # Skip header, get first few
    tds = tr.find_all('td')
    if len(tds) > 0:
        a_tag = tds[0].find('a')
        if a_tag and 'href' in a_tag.attrs:
            links.append(a_tag['href'])

print(f"Found links: {links}")

if links:
    # Check the first link
    print(f"Scraping {links[0]}")
    res2 = requests.get(links[0], headers={'User-Agent': 'Mozilla/5.0'})
    soup2 = BeautifulSoup(res2.text, 'html.parser')
    
    # Just print the text of tables to see what data is there
    tables = soup2.find_all('table')
    print(f"Found {len(tables)} tables")
    if len(tables) > 0:
        print(tables[0].text[:500])
