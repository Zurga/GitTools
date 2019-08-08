#!/usr/bin/python
import sys, os, argparse
from urllib.request import urlopen
from functools import partial
import requests
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import re
from tqdm import tqdm


def findgitrepo(domain):
    if domain:
        domain = domain.strip()

        try:
            # Try to download http://target.tld/.git/HEAD
            req = requests.get('http://{}/.git/HEAD'.format(domain), timeout=2)

            # Check if refs/heads is in the file
            if 'refs/heads' in req.text:
                return req.url.replace('HEAD', '')
            else:
                return False

        except Exception as e:
            return

def checkdotenv(domain):
    if domain:
        domain = domain.strip()

        try:
            # Try to download http://target.tld/.git/HEAD
            req = requests.get('http://{}/.env'.format(domain), timeout=10)

            # Check if refs/heads is in the file
            if 'DB_PASS' in req.text:
                return req.url
            else:
                return False

        except Exception as e:
            return

def findsvn(domain):
    if domain:
        domain = domain.strip()
    try:
        # Try to download http://target.tld/.git/HEAD
        req = requests.get('http://{}/.svn/wc.db'.format(domain), timeout=10)

        # Check if refs/heads is in the file
        if req and 'wc.db' in req.url and 'text/html' \
                not in req.headers['Content-Type']:
            return req.url
        else:
            return False

    except Exception as e:
        return

def testphp(domain):
    if domain:
        domain = domain.strip()
    try:
        # Try to download http://target.tld/.git/HEAD
        req = requests.get('http://{}/test.php'.format(domain), timeout=10)

        # Check if refs/heads is in the file
        title = re.findall('<title>(.*)</title>', req.text)
        if req and 'phpinfo()' in title:
            return req.url
        else:
            return False

    except Exception as e:
        return

def clean_url(url)
    return url.replace('\n', '').replace('"', '')

def prepare_requests(domain_file, executor, n):
    return {executor.submit(globals()[func], clean_url(url)): clean_url(url)
            for url in fle.readlines(n * 2)}

def main():
    print("""
###########
# Finder is part of https://github.com/internetwache/GitTools
#
# Developed and maintained by @gehaxelt from @internetwache
#
# Use at your own risk. Usage might be illegal in certain circumstances.
# Only for educational purposes!
###########
""")

    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--inputfile', default='input.txt', help='input file')
    parser.add_argument('-o', '--outputfile', default='output.txt', help='output file')
    parser.add_argument('-t', '--threads', default=200, help='threads')
    parser.add_argument('-f', '--function', default='findgitrepo',
                        help='functions: \n\tcheckdotenv \n\tfindgitrepo')
    args = parser.parse_args()

    try:
        max_processes = int(args.threads)
    except ValueError as err:
        sys.exit(err)


    DOMAINFILE=args.inputfile
    OUTPUTFILE=args.outputfile
    MAXPROCESSES=int(args.threads)
    func = args.function
    found_repos = []

    print('Reading urls from {file}.'.format(file=DOMAINFILE))
    with open(DOMAINFILE, "r", buffering=1) as fle, ThreadPoolExecutor(max_workers=MAXPROCESSES) as executor:
        future_to_url = prepare_requests(fle, executor, MAXPROCESSES)
        while future_to_url:
            print("Scanning...")
            for future in tqdm(as_completed(future_to_url)):
                url = future_to_url[future]
                result = future.result()
                if result:
                    print("[*] Found: " + result)
                    found_repos.append(result)
            future_to_url = prepare_requests(fle, executor, MAXPROCESSES)
    with open(OUTPUTFILE, 'w') as fle:
        fle.writelines('\n'.join(found_repos))

    print("Finished")
    # Write match to OUTPUTFILE

if __name__ == "__main__":
    main()
