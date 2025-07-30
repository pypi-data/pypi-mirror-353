import argparse
from .extractor import extract_links
from .sql_tester import test_sql_injection
from .admin_finder import find_admin
from .brute_forcer import brute_force_login

def main():
    parser = argparse.ArgumentParser(prog='sp', description='BlackSpammerBD Webmaster CLI')
    subparsers = parser.add_subparsers(dest='command')

    # extract
    parser_e = subparsers.add_parser('e', help='Extract all links from site')
    parser_e.add_argument('url', help='Target site URL')

    # sql test
    parser_c = subparsers.add_parser('c', help='Test SQL injection')
    parser_c.add_argument('url', help='Target site URL with parameter (e.g., site.php?id=)')

    # find admin
    parser_find = subparsers.add_parser('find', help='Find admin page')
    parser_find.add_argument('url', help='Base site URL')

    # brute force
    parser_brute = subparsers.add_parser('brute', help='Brute force login')
    parser_brute.add_argument('url', help='Login page URL')

    args = parser.parse_args()

    if args.command == 'e':
        extract_links(args.url)
    elif args.command == 'c':
        test_sql_injection(args.url)
    elif args.command == 'find':
        find_admin(args.url)
    elif args.command == 'brute':
        brute_force_login(args.url)
    else:
        parser.print_help()
