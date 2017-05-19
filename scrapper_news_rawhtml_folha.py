""" Crawls links from DB for html content """

# searches elasticsearch for documents without the html content
# crawls this content and saves into elasticsearch

# executing this script using
# nohup python3 -u scrapper_news_rawhtml_folha.py > log-scrapper_news_rawhtml_folha.log &

from bs4 import BeautifulSoup
import datetime
import elasticsearch
import hashlib
import requests
import sys
import time


def print_now(text):
    "prints and flushes the output"  # sometimes the pint function has delays, this solves that problem
    sys.stdout.write(str(text))
    sys.stdout.write('\n')
    sys.stdout.flush()


# establishing elasticsearch connection
es = elasticsearch.Elasticsearch()

while True:
    # searching
    res = es.search(index="i_rsslinks_v1",
                    doc_type="m_rsslinks_v1",
                    size=15,
                    scroll='1m',
                    body={"filter":{"missing":{"field":"scrapped"}}})
    # counting results
    numRes = len(res['hits']['hits'])
    if numRes > 0:
        # saving results
        pages_to_scrap = list()
        for doc in res['hits']['hits']:
            di = doc['_source']
            di['uniqueId'] = doc['_id']
            pages_to_scrap.append(di)
        # iterating over page links
        for page in pages_to_scrap:
            # sending request
            req = requests.get(page['link'])
            # parsing page
            soup = BeautifulSoup(req.text, 'html.parser')
            # testing limitations
            try:
                if soup.select('head > meta > link > title')[0].text.find('ocê atingiu o limite') > -1:
                    print('limite de reportagens atingido')
                    sys.exit(1)
            except:
                pass
            # raw html content (stripping white space)
            page_raw_html = ' '.join(req.text.split())
            # creating link's raw content id
            link_id = hashlib.sha1(page['link'].encode('utf-8')).hexdigest()
            # storing html content
            res = es.index(index="i_rawhtml_v1",
                            doc_type='m_rawhtml_v1',
                            id=link_id,
                            timeout='60s',
                            body={'link': page['link'],
                                'raw_html': page_raw_html})
            if res['created']:
                print_now('{} scrapped link {}'.format(datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S'),
                                                                page['link']))
            # updating info that page was scrapped
            upd = es.update(index="i_rsslinks_v1",
                            doc_type="m_rsslinks_v1",
                            timeout='120s',
                            id=page['uniqueId'],
                            body={'doc':{'scrapped':1,
                                        'linkId':link_id}})
    time.sleep(35)
