'''
deadseeker.py
Seeking out your 404s in around 100 lines of Python.
'''

import sys
import os
import urllib
import time
import json
from urllib import request, parse
from urllib.parse import urlparse, urljoin
from urllib.request import Request
from html.parser import HTMLParser
from collections import deque
import backoff
import logging

search_attrs = set(['href', 'src'])
excluded_link_prefixes = set()
agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'

class LinkParser(HTMLParser):
    def __init__(self, home, verbose):
        ''':home:    a homepage, e.g. 'https://healeycodes.com/'
           :verbose: boolean for for verbose mode'''
        super().__init__()
        self.home = home
        self.verbose = verbose
        self.checked_links = set()
        self.pages_to_check = deque()
        self.pages_to_check.appendleft(home)
        self.error_occured = False
        self.scanner()
        if self.error_occured:
            print("::error ::Found some broken links!")
            sys.exit(1)

    def scanner(self):
        '''Loop through remaining pages, looking for HTML responses'''
        while self.pages_to_check:
            page = self.pages_to_check.pop()
            req = Request(page, headers={'User-Agent': agent})
            try:
                res = self.make_request(req)
                if 'html' in res.headers['content-type']:
                    with res as f:
                        body = f.read().decode('utf-8', errors='ignore')
                        self.feed(body)                
            except urllib.error.HTTPError as e:
                print(f'::error ::HTTPError: {e.code} - {page}')  # (e.g. 404, 501, etc)
                self.error_occured = True
            except urllib.error.URLError as e:
                print(f'::error ::URLError: {e.reason} - {page}')  # (e.g. conn. refused)
                self.error_occured = True
            except ValueError as e:
                print(f'::error ::ValueError {e} - {page}')  # (e.g. missing protocol http)
                self.error_occured = True            
            

    def handle_starttag(self, tag, attrs):
        '''Override parent method and check tag for our attributes'''
        for attr in attrs:
            # ('href', 'http://google.com')
            if attr[0] in search_attrs and attr[1] not in self.checked_links and not attr[1].startswith(tuple(excluded_link_prefixes)):
                self.checked_links.add(attr[1])
                self.handle_link(attr[1])

    def handle_link(self, link):
        '''Send a HEAD request to the link, catch any pesky errors'''
        if not bool(urlparse(link).netloc):  # relative link?
            link = urljoin(self.home, link)
        try:
            req = Request(link, headers={'User-Agent': agent}, method='HEAD')
            start = time.time() # measure load time (HEAD only)
            statusCode = self.make_statuscode_request(req)
            end = time.time()
        except urllib.error.HTTPError as e:
            print(f'::error ::HTTPError: {e.code} - {link}')  # (e.g. 404, 501, etc)
            self.error_occured = True
        except urllib.error.URLError as e:
            print(f'::error ::URLError: {e.reason} - {link}')  # (e.g. conn. refused)
            self.error_occured = True
        except ValueError as e:
            print(f'::error ::ValueError {e} - {link}')  # (e.g. missing protocol http)
            self.error_occured = True
        else:
            if self.verbose:
                elapsedTime = "{0:.2f} ms".format((end - start)*1000)
                print(f'{statusCode} - {link} - {elapsedTime}')
        if self.home in link:
            self.pages_to_check.appendleft(link)
    
    @backoff.on_exception(backoff.expo, (urllib.error.HTTPError, urllib.error.URLError), max_time=int(os.environ['INPUT_MAX_RETRY_TIME']), max_tries=int(os.environ['INPUT_MAX_RETRIES'])) # retry on error
    def make_request(self, req):
        res = request.urlopen(req)
        return res

    @backoff.on_exception(backoff.expo, (urllib.error.HTTPError, urllib.error.URLError), max_time=int(os.environ['INPUT_MAX_RETRY_TIME']), max_tries=int(os.environ['INPUT_MAX_RETRIES'])) # retry on error
    def make_statuscode_request(self, req):
        statusCode = request.urlopen(req).getcode()
        return statusCode

# read env variables
website_url = os.environ['INPUT_WEBSITE_URL']
verbose = os.environ['INPUT_VERBOSE']
exclude_prefix = os.environ['INPUT_EXCLUDE_URL_PREFIX']
print("Checking website: " + str(website_url))
print("Verbose mode on: " + str(verbose))
if exclude_prefix and exclude_prefix != '':
    for el in exclude_prefix.split(","):
        excluded_link_prefixes.add(el.strip())
    print(f"Excluding prefixes: {excluded_link_prefixes}")

if verbose:
    logging.getLogger('backoff').addHandler(logging.StreamHandler())
LinkParser(website_url, verbose)
