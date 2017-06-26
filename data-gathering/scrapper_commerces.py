""" Crawls extensively a website for all urls from same domain it can find """

# starting from the home page, this script crawls every link
# looking for more links from the same domain
# saving the content of each url in local files

# examples
# executing this script using
# nohup python3 -u scrapper_commerces.py "http://www.ricardoeletro.com.br/" "get-proxy" >> log-scrapper_commerces.log &
# nohup python3 -u scrapper_commerces.py "https://www.petz.com.br/" "selenium" >> log-scrapper_commerces.log &

from bs4 import BeautifulSoup
import datetime
import gc
import hashlib
import os
import requests
import sys
import urllib


def print_now(text):
    "prints and flushes the output"
    sys.stdout.write(str(text))
    sys.stdout.write('\n')
    sys.stdout.flush()


def RemoveFirstLinkFromToreadList():
    "removes defectuous urls from toread list"
    # getting list of links to read next
    toread = []
    with open(to_read_file, 'r') as f:
        for line in f:
            toread.append(line.strip('\n'))
    # removing first url
    del toread[0]
    # writing new list of to read docs
    with open(to_read_file, 'w') as f:
        for url in toread:
            f.write('{}\n'.format(url))
    # returning new first url
    return toread[0]



to_read_file = 'partial_data/toread_13'
read_urls_list = 'partial_data/links_list_13'
# setting initial variables for this script
target_url = sys.argv[1]
# target_url = "http://www.ricardoeletro.com.br/"  # TESTS

# reading actual working directory for dealing with files
sys.path.append(os.getcwd())
# setting string to search in domains
domain = urllib.parse.urlsplit(target_url).netloc.replace('www.', '').split('.')[0]
# setting retries
retries = 0

# loop
while True:
    # checking if there is a new link to crawl
    if target_url is None:
        break
    # checking retries to remove bad urls
    if retries >= 5:
        target_url = RemoveFirstLinkFromToreadList()
        # resetting retries
        retries = 0
        continue
    # reading page
    try:
        # requesting page source
        page = requests.get(target_url)
        # parsing page
        page_html = BeautifulSoup(page.text, 'html.parser')
        # testing request return status
        if page.status_code != 200:
            print_now('{} | erro no request, cod {}'.format(datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S'),
                                                            str(page.status_code)))
            retries += 1
            continue
    except:
        retries += 1
        continue
    # reseting retries count
    retries = 0
    # creating link's raw content id
    link_id = hashlib.sha1(target_url.encode('utf-8')).hexdigest()
    # writing webpage content to file
    if os.system('[ -f websites_data/{} ]'.format(link_id)) > 0:
        with open('websites_data/{}'.format(link_id), 'w') as f:
            f.write(' '.join(str(page_html).split()))
        print_now('{} | scrapped link {}'.format(datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S'),
                                                target_url))
        # storing link with url and sha id
        with open(read_urls_list, 'a') as f:
            f.write('{},{}\n'.format(link_id, target_url))
    # generating empty list
    new_urls = []
    # getting all links from page
    for anchor in page_html.find_all('a'):
        # getting link
        link = anchor.get('href')
        # parsing urls
        url = urllib.parse.urlsplit(link)
        # filtering only ones with domain www1.folha.uol.com.br
        if type(link) == str and url.netloc.find(domain) >= 0:
            # filtering only links in target categories
            new_urls.append(urllib.parse.urlunsplit((url.scheme, url.netloc, url.path, None, None)))
    # removing duplicates
    new_urls = list(set(new_urls))
    # getting list of links already read
    didread = []
    with open(read_urls_list, 'r') as f:
        for line in f:
            didread.append(line.split(',')[0])
    # getting list of links to read next
    toread = []
    with open(to_read_file, 'r') as f:
        for line in f:
            toread.append(line.strip('\n'))
    # generating new list of urls to read
    for url in new_urls:
        if hashlib.sha1(url.encode('utf-8')).hexdigest() not in didread and url not in toread:
            toread.append(url)
    print_now('{} | read: {} | toread: {}'.format(datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S'),
                                        str(len(didread)),
                                        str(len(toread))))
    # removing url just read
    del toread[0]
    # writing new list of to read docs
    with open(to_read_file, 'w') as f:
        for url in toread:
            f.write('{}\n'.format(url))
    # getting next url
    try:
        target_url = toread[0]
    except:
        target_url = None
    # garbage collector
    gc.collect()

print_now('{} | bye'.format(datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')))

