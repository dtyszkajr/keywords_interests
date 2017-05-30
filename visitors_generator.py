""" Simulates visitors and pages visited by them """

# generates X visitors with random Ids
# each visitor visits Y pages

# examples
# executing this script using
# python3 -u visitors_generator.py 150 3

import os
import random
import string
import sys
import numpy as np
import hashlib

# script variables
VISITOR_NUMBER = sys.argv[1]
PAGES_VISITED_AVG = sys.argv[2]  # options: selenium, get-proxy, get
# VISITOR_NUMBER = 150  # TESTS
# PAGES_VISITED_AVG = 3  # TESTS

# reading actual working directory for dealing with files
sys.path.append(os.getcwd())

# reading possible URLs
urls = []
with open('websites_data/links_list', 'r') as f:
    for line in f:
        urls.append(line.split(',')[1].strip('\n'))

# preparing to generate visitors
visitorsData = []
for vis in range(VISITOR_NUMBER):
    # generating random Id
    vis_id = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(30))
    vis_id = hashlib.sha1(vis_id.encode('utf-8')).hexdigest()
    views = np.random.poisson(PAGES_VISITED_AVG)
    for vi in range(views):
        visitorsData.append({'visitorId': vis_id,
                            'url': random.choice(urls)})

# saving results to file
with open('websites_data/visitors_db.csv', 'w') as f:
    f.write('visitorId,url\n')
    for visData in visitorsData:
        f.write('{},{}\n'.format(visData['visitorId'], visData['url']))
