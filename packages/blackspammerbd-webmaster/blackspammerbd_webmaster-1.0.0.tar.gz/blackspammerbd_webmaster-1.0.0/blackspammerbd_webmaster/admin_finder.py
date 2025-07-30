import requests
from .utils import generate_admin_paths

def find_admin(base_url):
    print(f"[+] Searching admin pages at {base_url}...")
    paths = generate_admin_paths()
    found = []

    for path in paths:
        full_url = base_url.rstrip('/') + '/' + path.lstrip('/')
        try:
            r = requests.get(full_url, timeout=3)
            if r.status_code == 200:
                print(f"[!] Found admin page: {full_url}")
                found.append(full_url)
        except Exception:
            continue

    if not found:
        print("[+] No admin pages found with provided paths.")
