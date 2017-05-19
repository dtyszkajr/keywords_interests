""""Collects news links from chosen rss' feeds from folha de sao paulo and save it to local elasticsearch"""

# executing this script using
# nohup python3 -u rss__loopreader_folha.py > log-rss_loop_reader_folha.log &

import datetime
import elasticsearch
import feedparser
import hashlib
import sys
import time


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

# list of chosen rss' feeds from folha de sao paulo
folha_rss = [
                {
                    'category': 'poder',
                    'link': 'http://feeds.folha.uol.com.br/poder/rss091.xml',
                    'actual_etag': 'zero',
                    'last_loop_entry_links': ['zero']
                },
                {
                    'category': 'mundo',
                    'link': 'http://feeds.folha.uol.com.br/mundo/rss091.xml',
                    'actual_etag': 'zero',
                    'last_loop_entry_links': ['zero']
                },
                {
                    'category': 'mercado',
                    'link': 'http://feeds.folha.uol.com.br/mercado/rss091.xml',
                    'actual_etag': 'zero',
                    'last_loop_entry_links': ['zero']
                },
                {
                    'category': 'cotidiano',
                    'link': 'http://feeds.folha.uol.com.br/cotidiano/rss091.xml',
                    'actual_etag': 'zero',
                    'last_loop_entry_links': ['zero']
                },
                {
                    'category': 'educacao',
                    'link': 'http://feeds.folha.uol.com.br/educacao/rss091.xml',
                    'actual_etag': 'zero',
                    'last_loop_entry_links': ['zero']
                },
                {
                    'category': 'esporte',
                    'link': 'http://feeds.folha.uol.com.br/esporte/rss091.xml',
                    'actual_etag': 'zero',
                    'last_loop_entry_links': ['zero']
                },
                {
                    'category': 'ilustrada',
                    'link': 'http://feeds.folha.uol.com.br/ilustrada/rss091.xml',
                    'actual_etag': 'zero',
                    'last_loop_entry_links': ['zero']
                },
                {
                    'category': 'ciencia',
                    'link': 'http://feeds.folha.uol.com.br/ciencia/rss091.xml',
                    'actual_etag': 'zero',
                    'last_loop_entry_links': ['zero']
                },
                {
                    'category': 'ambiente',
                    'link': 'http://feeds.folha.uol.com.br/ambiente/rss091.xml',
                    'actual_etag': 'zero',
                    'last_loop_entry_links': ['zero']
                },
                {
                    'category': 'tech',
                    'link': 'http://feeds.folha.uol.com.br/tec/rss091.xml',
                    'actual_etag': 'zero',
                    'last_loop_entry_links': ['zero']
                },
                {
                    'category': 'comida',
                    'link': 'http://feeds.folha.uol.com.br/comida/rss091.xml',
                    'actual_etag': 'zero',
                    'last_loop_entry_links': ['zero']
                },
                {
                    'category': 'equilibrio_saude',
                    'link': 'http://feeds.folha.uol.com.br/equilibrioesaude/rss091.xml',
                    'actual_etag': 'zero',
                    'last_loop_entry_links': ['zero']
                },
                {
                    'category': 'turismo',
                    'link': 'http://feeds.folha.uol.com.br/turismo/rss091.xml',
                    'actual_etag': 'zero',
                    'last_loop_entry_links': ['zero']
                }
            ]

# connecting to elasticsearch
es = elasticsearch.Elasticsearch()

while True:
    for target_rss in folha_rss:
        # setting index for target rss
        target_rss_index = next(index for (index, d) in enumerate(folha_rss) if d["category"] == target_rss['category'])
        # getting rss info
        d = feedparser.parse(target_rss['link'], etag=target_rss['actual_etag'])
        # checking if rss was updated,
        # if status = 200 there is new content,
        # otherwise is status 304
        try:
            d.status == 200
        except:
            break
        if d.status == 200:
            # getting entries from rss
            entries = [{
                        'title': entry['title'],
                        'link': entry['link'][entry['link'].find('http', 1):],  # folha uses a url redirect, this code gets the main url only
                        'category': target_rss['category']
                        } for entry in d['entries']]
            # removing entries already processed
            new_entries = [entry for entry in entries if entry['link'] not in folha_rss[target_rss_index]['last_loop_entry_links']]
            # saving new entries
            SaveEntriesToDB(new_entries)
            # updating etag
            folha_rss[target_rss_index]['actual_etag'] = d['etag']
            # updating list of last loop entries info
            folha_rss[target_rss_index]['last_loop_entry_links'] = [entry['link'] for entry in entries]
    time.sleep(15)
