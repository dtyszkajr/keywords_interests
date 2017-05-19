# Newspaper's Articles Study

The main objective is know visitors' interests using the newspaper articles read by them.

## Files Description
* es_index_creator.sh - file with initial config for index used to save the data in elasticsearch;
* rss_loop_reader_folha.py - script that reads rss' from folha newspaper and saves article's links in elasticsearch;
* scrapper_news_links_folha.py - scraps folha's website for articles in general and saves into elasticsearch;
* scrapper_news_rawhtml_folha.py - get raw html of links stored and saves into elasticsearch
