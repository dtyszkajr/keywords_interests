""" Reads urls codes, categorizes in page types and saves products descriptions """

# examples
# executing this script using
# python3 -u url_classifier.py

import os
import sys
from bs4 import BeautifulSoup
import json

# reading actual working directory for dealing with files
sys.path.append(os.getcwd())

# reading urls list
didread = []
with open('data-gathering/partial_data/links_list', 'r') as f:
    for line in f:
        didread.append({'id': line.split(',')[0], 'url': line.split(',')[1].strip('\n')})

# iterating over links and categorizing each
for page in didread:
    # reading html source code
    with open('data-gathering/websites_data/{}'.format(page['id']), 'r') as f:
        page_content = f.read()
    # parsing page code
    page_soup = BeautifulSoup(page_content, 'html.parser')
    # getting scripts from page
    scripts = page_soup.find_all('script')
    # extracting specific script with page info
    for it in scripts:
        if it.text.find('var dataLayer') > -1:
            dataLayer = json.loads(it.text[17:-2])
    # classifying
    if "displayingHome" in dataLayer:
        page['pg-type'] = 'pt-home'
    elif "productList" in dataLayer:
        page['pg-type'] = 'pt-category'
        page['department'] = '>'.join([dataLayer["pageDepartment"].replace(',', ''), dataLayer["pageCategory"].replace(',', ''), dataLayer["pageSubCategory"].replace(',', '')])
    elif "productSKUList" in dataLayer:
        page['pg-type'] = 'pt-product'
        page['department'] = '>'.join([dataLayer["pageDepartment"].replace(',', ''), dataLayer["pageCategory"].replace(',', ''), dataLayer["pageSubCategory"].replace(',', '')])
        try:
            page['description'] = ' '.join(page_soup.find('div', id='aba-descricao').find('div', 'descricao-produto').text.split()).replace('"', '')
        except:
            pass
    elif "searchQuery" in dataLayer:
        page['pg-type'] = 'pt-search'
        deps = [x['department'] for x in dataLayer['searchProducts']]
        if len(deps) > 0:
            page['department'] = '>'.join([max(deps, key=deps.count).replace(',', ''), '', ''])
    else:
        page['pg-type'] = 'pt-others'


# saving results to file
with open('data-gathering/partial_data/links-page-types.csv', 'w') as f:
    f.write('link_id,pg-type,department,url\n')
    for link in didread:
        if 'department' in link:
            f.write('{},{},{},{}\n'.format(link['id'], link['pg-type'], link['department'], link['url']))
        else:
            f.write('{},{},,{}\n'.format(link['id'], link['pg-type'], link['url']))


# keeping only products with text description
products = [it for it in didread if ('description' in it and it['description'] != '')]

# saving product descriptions
for prod in products:
    with open('data-gathering/websites_data/products/{}'.format(prod['id']), 'w') as f:
        f.write(prod['description'])
