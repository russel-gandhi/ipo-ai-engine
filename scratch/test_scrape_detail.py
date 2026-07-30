import requests
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}
url = "https://www.chittorgarh.com/ipo/gala-precision-engineering-ipo/1844/"
response = requests.get(url, headers=headers)
print(f"URL: {url} -> Status: {response.status_code}")
if response.status_code == 200:
    print(f"Length: {len(response.text)}")
    soup = BeautifulSoup(response.text, 'html.parser')
    print("Title:", soup.title.text if soup.title else "No title")
