import requests
from .utils import generate_sql_payloads

def test_sql_injection(url):
    print(f"[+] Testing SQL injection on {url}...")
    payloads = generate_sql_payloads()
    vulnerable = []

    for payload in payloads:
        test_url = url + payload
        try:
            r = requests.get(test_url, timeout=5)
            lower_text = r.text.lower()
            if any(err in lower_text for err in ['sql syntax', 'mysql fetch', 'warning']):
                vulnerable.append((payload, test_url))
                print(f"[!] Potentially vulnerable with payload: {payload}")
        except Exception:
            continue

    if vulnerable:
        print("[!] Vulnerabilities detected:")
        for p, u in vulnerable:
            print(f"    Payload: {p} => {u}")
    else:
        print("[+] No vulnerabilities detected with provided payloads.")
