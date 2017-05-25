""" Crawls folha for article old pages """

# starting from the home page, this script crawls every link
# looking for more lings in the target categories and date (2017-04)
# saving all of them in the local elasticsearch database

# executing this script using
# nohup python3 -u scrapper_commerces.py "http://www.ricardoeletro.com.br/" "proxy" >> log-scrapper_commerces.log &
# nohup python3 -u scrapper_commerces.py "https://www.petz.com.br/" "regular" "selenium" >> log-scrapper_commerces.log &

from bs4 import BeautifulSoup
import datetime
import elasticsearch
import hashlib
import requests
import sys
import urllib
from selenium import webdriver


def print_now(text):
    "prints and flushes the output"  # sometimes the pint function has delays, this solves that problem
    sys.stdout.write(str(text))
    sys.stdout.write('\n')
    sys.stdout.flush()


# initial_link = "https://www.petz.com.br/"
initial_link = sys.argv[1]
# setting string to search in domains
domain = urllib.parse.urlsplit(initial_link).netloc.replace('www.', '').split('.')[0]
# initializing url's list to crawl
all_links = [initial_link]
# connecting to elasticsearch
es = elasticsearch.Elasticsearch()
# initializing browser
if len(sys.argv) > 3 and sys.argv[3] == 'selenium':
    driver_count = 0
    driver = webdriver.PhantomJS()
# initializing list index
indice = 0
# loop
while True:
    # checking if there is a new link to crawl
    if indice >= len(all_links):
        break
    # getting target url
    target_url = all_links[indice]
    # requesting target url
    if len(sys.argv) > 3 and sys.argv[3] == 'selenium':
        driver.get(target_url)
        page_text = driver.page_source
        driver_count += 1
        # restarting the browser
        if driver_count > 14:
            driver.close()
            driver = webdriver.PhantomJS()
        soup = BeautifulSoup(page_text, 'html.parser')
        try:
            if soup.find("iframe").text.find("equest unsuccessful") > -1:
                print_now('{} request unseccessful'.format(datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')))
                continue
        except:
            pass
    elif len(sys.argv) > 2 and sys.argv[2] == 'proxy':
        page = requests.get(target_url, proxies={"http": "186.211.102.57:80"})
        # parsing page
        soup = BeautifulSoup(page.text, 'html.parser')
        if page.status_code != 200:
            print_now('{} erro no request, cod {}'.format(datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S'),
                                                            str(page.status_code)))
            continue
    else:
        page = requests.get(target_url)
        # parsing page
        soup = BeautifulSoup(page.text, 'html.parser')
        if page.status_code != 200:
            print_now('{} erro no request, cod {}'.format(datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S'),
                                                            str(page.status_code)))
            continue
    # generating empty list
    new_urls = []
    # getting all links from page
    for anchor in soup.find_all('a'):
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
    # appending to list of links
    for url in new_urls:
        if url not in all_links:
            all_links.append(url)
    # raw html content (stripping white space)
    page_raw_html = ' '.join(str(soup).split())
    # creating link's raw content id
    link_id = hashlib.sha1(target_url.encode('utf-8')).hexdigest()
    # storing html content
    res = es.index(index="i_commerceshtml_v1",
                    doc_type='m_commerceshtml_v1',
                    id=link_id,
                    timeout='120s',
                    body={
                        'link': target_url,
                        'domain': domain,
                        'raw_html': page_raw_html})
    if res['created']:
        print_now('{} scrapped link {}'.format(datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S'),
                                                target_url))
    # incrementing the counter
    indice += 1
