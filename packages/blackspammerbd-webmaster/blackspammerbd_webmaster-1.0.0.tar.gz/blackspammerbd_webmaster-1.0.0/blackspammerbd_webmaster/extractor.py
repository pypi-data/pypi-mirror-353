import requests
from bs4 import BeautifulSoup
import os
from .utils import sanitize_filename

def extract_links(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    links = set()
    for a in soup.find_all('a', href=True):
        links.add(a['href'])

    # Create folder to store
    folder_name = sanitize_filename(url.replace('http://', '').replace('https://', ''))
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    filepath = os.path.join(folder_name, 'links.txt')
    with open(filepath, 'w') as f:
        for link in links:
            f.write(f"{link}\n")

    print(f"[+] Extracted {len(links)} links and saved to {filepath}")
