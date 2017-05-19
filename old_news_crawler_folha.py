""" Crawls folha for article old pages """

# starting from the home page, this script crawls every link
# looking for more lings in the target categories and date (2017-04)
# saving all of them in the local elasticsearch database

# executing this script using
# nohup python3 -u old_news_crawler_folha.py > log-old_news_crawler_folha.log &

from bs4 import BeautifulSoup
import datetime
import elasticsearch
import hashlib
import requests
import sys
import urllib


def print_now(text):
    "prints and flushes the output"  # sometimes the pint function has delays, this solves that problem
    sys.stdout.write(str(text))
    sys.stdout.write('\n')
    sys.stdout.flush()


def SaveEntriesToDB(entriesList):
    "saves docs in given list to local elasticsearch and logs the doc indexed"
    for item in entriesList:
        res = es.index(index="i_rsslinks_v1",
                        doc_type='m_rsslinks_v1',
                        id=hashlib.sha1('_'.join([item['category'], item['link']]).encode('utf-8')).hexdigest(),  # same link can be published in different categories
                        body=item)
        if res['created']:
            print_now('{} category {} link {}'.format(datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S'),
                                                    item['category'],
                                                    item['link']))


# initializing url's list to crawl
all_links = ["http://www1.folha.uol.com.br"]

# target categories of articles
target_categories = [
                    'ambiente',
                    'ciencia',
                    'comida',
                    'cotidiano',
                    'educacao',
                    'equilibrio_saude',
                    'esporte',
                    'ilustrada',
                    'mercado',
                    'mundo',
                    'poder',
                    'tech',
                    'turismo'
                    ]

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
    page = requests.get(target_url)
    # parsing page
    soup = BeautifulSoup(page.text, 'html.parser')
    # testing limitations
    try:
        if soup.select('head > meta > link > title')[0].text == 'Você atingiu o limite de 5 reportagens por mês':
            print('limite de reportagens atingido')
            sys.exit(1)
    except:
        pass
    # generating empty list
    new_urls = []
    # getting all links from page
    for anchor in soup.find_all('a'):
        link = anchor.get('href')
        # parsing urls
        url = urllib.parse.urlsplit(link)
        # filtering only ones with domain www1.folha.uol.com.br
        if type(link) == str and url.netloc.find('www1.folha.uol.com.br') >= 0:
            # filtering only links in target categories
            # filtering by date -> 2017-04-XX
            if (len(url.path.split('/')) > 3 and
                    url.path.split('/')[1] in target_categories and
                    url.path.split('/')[2] == '2017' and
                    url.path.split('/')[3] == '04'):
                new_urls.append(urllib.parse.urlunsplit((url.scheme, url.netloc, url.path, None, None)))
    # removing duplicates
    new_urls = list(set(new_urls))
    # appending to list of links
    for url in new_urls:
        if url not in all_links:
            all_links.append(url)
    # incrementing the counter
    indice += 1

# removing home page's link
all_links = all_links[1:]
# turning into objects to save to database
all_itens = [{'category': urllib.parse.urlsplit(it).path.split('/')[1], 'link': it} for it in all_links]
# connecting to elasticsearch
es = elasticsearch.Elasticsearch()
# saving new entries
SaveEntriesToDB(all_itens)
