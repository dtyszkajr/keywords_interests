
import os
import sys
import pandas as pd
import hashlib
import unidecode
import string

# reading actual working directory for dealing with files
sys.path.append(os.getcwd())


def ParseDepartment(text):
    "turn department text into pattern"
    if text is None:
        return None
    # remove accentuation and splitting into sub departments
    text = unidecode.unidecode(text).split('>')
    # table of punctuatuin remover
    trans_table = str.maketrans({key: None for key in string.punctuation})
    # removing punctuatuin and transforming into default pattern
    return [x.lower().translate(trans_table) for x in text if x != '']


# getting saved data
urlsDB = pd.read_csv('data-gathering/partial_data/links-page-types.csv')
visitorsDB = pd.read_csv('data-gathering/partial_data/visitors_db.csv')
visitorsDB['link_id'] = visitorsDB['url'].apply(lambda x: hashlib.sha1(x.encode('utf-8')).hexdigest())  # adding link_id
products_list = []
for linkid in urlsDB.loc[urlsDB['pg-type'] == 'pt-product', 'link_id'].values:
    try:
        with open('data-gathering/websites_data/products/{}'.format(linkid), 'r') as f:
            products_list.append({'link_id': linkid, 'description': f.read()})
    except:
        pass
productsDB = pd.DataFrame(products_list)
# generating complete db
allDB = visitorsDB.merge(urlsDB[['link_id', 'pg-type', 'department']],
                        on='link_id',
                        how='left').merge(productsDB,
                                            on='link_id',
                                            how='left')
# transforming NaN into None values
allDB = allDB.where((pd.notnull(allDB)), None)
# removing bad urls (15% 59% ?)
allDB = allDB.loc[pd.notnull(allDB['pg-type'])]

# cleaning departments
allDB['department'] = allDB['department'].apply(ParseDepartment)

# FLATTENING BY DEPARTMENT
# selecting only department data
vis_deps = allDB.loc[allDB['department'].notnull(), ['visitorId', 'department']]
# aggrouping visitors data
vis_deps = vis_deps.groupby('visitorId', as_index=False).agg({'department': lambda x: list(set([it for subit in x for it in subit]))})
# flattening data
vis_deps_flat = pd.DataFrame([[i, x] for i, y in vis_deps['department'].apply(list).iteritems() for x in y], columns=list(['I','department'])).set_index('I')
vis_deps_flat = vis_deps[['visitorId']].merge(vis_deps_flat, left_index=True, right_index=True)
# saving data
vis_deps_flat.to_csv('data-gathering/partial_data/vis_dep_flat.csv', index=False)

# FLATTENING BY KEYWORDS

###################################################################################################
# FILTROS POR DEPARTAMENTO ##############################################################################

# selecting only data with department information
vis_deps = allDB.loc[allDB['department'].notnull(), ['visitorId', 'department']]
# flattening data by visitors
vis_deps = vis_deps.groupby('visitorId', as_index=False).agg({'department': lambda x: list(set([it for subit in x for it in subit]))})
# flattening ALL data
full_flat = pd.DataFrame([[i, x] for i, y in vis_deps['department'].apply(list).iteritems() for x in y], columns=list(['I','department'])).set_index('I')
full_flat = vis_deps[['visitorId']].merge(full_flat, left_index=True, right_index=True)
# aggregating by department
deps_vis = full_flat.groupby('department', as_index=False).agg({'visitorId': lambda x: list(set(x))})

# initial counts
initial_deps_counts = deps_vis.copy()
initial_deps_counts['vis_qtd'] = initial_deps_counts['visitorId'].apply(lambda x: len(x))
initial_deps_counts = initial_deps_counts[['department', 'vis_qtd']].sort_values(by='vis_qtd', ascending=False)


def FilterVis(flat, dep_target):
    # selecting visitors in target department
    target_vis = flat.loc[flat['department'] == dep_target, 'visitorId'].values
    # getting all data from target visitors
    new_flat = flat.loc[flat['visitorId'].isin(target_vis)]
    # removing target department
    new_flat = new_flat.loc[new_flat['department'] != dep_target]
    # recounting visitors by department inside target dep
    deps_counts = new_flat.groupby('department', as_index=False).agg({'visitorId': lambda x: list(set(x))})
    deps_counts['vis_qtd'] = deps_counts['visitorId'].apply(lambda x: len(x))
    # removing unwanted columns and sorting
    deps_counts = deps_counts[['department', 'vis_qtd']].sort_values(by='vis_qtd', ascending=False)
    return deps_counts, new_flat


next_counts, next_flat = FilterVis(flat=full_flat.copy(), dep_target='eletrodomesticos')

print()
print(next_counts.head(25))

next_counts, next_flat = FilterVis(flat=next_flat.copy(), dep_target='expositor de bebidas e cervejeira')

print()
print(next_counts.head(25))


###################################################################################################
# TESTES DE KEYWORDS ##############################################################################

import itertools
import nltk
import random
import pexpect
import re


def split_sentences(text):
    """
    TOOK FROM RAKE.PY
    https://github.com/aneesha/RAKE
    Utility function to return a list of sentences.
    @param text The text that must be split in to sentences.
    """
    sentence_delimiters = re.compile(u'[.!?,;:\t\\\\"\\(\\)\\\'\u2019\u2013]|\\s\\-\\s')
    sentences = sentence_delimiters.split(text)
    return sentences

class POS_TAGGER():
    def __init__(self):
        # configuring the call command
        opennlp = os.path.join('/'.join([os.getcwd(),'third-part-projects-used/apache-opennlp-1.8.0/bin/opennlp']))
        tool = 'POSTagger'
        models = os.path.join('/'.join([os.getcwd(),'third-part-projects-used/apache-opennlp-1.8.0/models/pt-pos-perceptron.bin']))
        cmd = "%s %s %s" % (opennlp, tool, models)
        # spawning the server
        self.process = pexpect.spawn(cmd)
        self.process.setecho(False)
        self.process.expect('done')
        self.process.expect('\r\n')

    def parse(self, text):
        # Clear any pending output
        try:
            self.process.read_nonblocking(2048, 0)
        except:
            pass
        self.process.sendline(text)
        # Workaround pexpect bug
        self.process.waitnoecho()
        # Long text also needs increase in socket timeout
        timeout = 5 + len(text) / 20.0
        self.process.expect('\r\n', timeout)
        results = self.process.before
        # preparing data
        results = [tuple(x.split('_')) for x in results.decode('utf-8').split()]
        return results

def GetCandidatesChunks(tagged_sents, grammar):
    # exclude candidates that are stop words or entirely punctuation
    punct = set(string.punctuation)
    # stop_words = set(nltk.corpus.stopwords.words('portuguese'))
    # tokenize, POS-tag, and chunk using regular expressions
    chunker = nltk.chunk.regexp.RegexpParser(grammar)
    # tagged_sents = nltk.pos_tag_sents(nltk.word_tokenize(sent) for sent in nltk.sent_tokenize(text))
    all_chunks = list(itertools.chain.from_iterable(nltk.chunk.tree2conlltags(chunker.parse(tagged_sent)) for tagged_sent in tagged_sents))
    # join constituent chunk words into a single chunked phrase
    candidates = [' '.join(word for word, pos, chunk in group).lower() for key, group in itertools.groupby(all_chunks, lambda x: x[2] != 'O') if key]
    return [cand for cand in candidates if not all(char in punct for char in cand)]

def GetKeywords(parsed_text, grammar_options):
    keywords = []
    for gram in grammar_options:
        k_opts = GetCandidatesChunks(parsed_text, gram)
        [keywords.append(x) for x in k_opts if len(k_opts) > 0]
    if len(keywords) > 0:
        return keywords
    else:
        return None

# loading only texts from descriptions
vis_keywords = allDB.loc[allDB['description'].notnull(), ['visitorId', 'description']]
vis_keywords['description'] = vis_keywords['description'].apply(lambda x: x.lower().replace('aviso:imagens meramente ilustrativas', ''))
vis_keywords['description'] = vis_keywords['description'].apply(lambda x: x.replace('aviso:imagem meramente ilustrativa', ''))
vis_keywords['description'] = vis_keywords['description'].apply(lambda x: x.replace('aviso: imagem meramente ilustrativa', ''))
vis_keywords['description'] = vis_keywords['description'].apply(lambda x: x.replace('imagem meramente ilustrativa', ''))
vis_keywords['description'] = vis_keywords['description'].apply(lambda x: x.replace('imagens meramente ilustrativas', ''))

# print(vis_keywords.shape)
# vis_keywords = vis_keywords.iloc[:150]

#  starting parser
pos_pt = POS_TAGGER()

vis_keywords['description_parsed'] = vis_keywords['description'].apply(lambda x: [pos_pt.parse(sente) for sente in split_sentences(x) if len(sente) > 1])
print(vis_keywords.shape)

g_options = [r'KT: {<n><adj>}', r'KT: {<n><prp><n>}', r'KT: {<prop><prop>}']
vis_keywords['keywords'] = vis_keywords['description_parsed'].apply(lambda x: GetKeywords(x, g_options))

vis_keywords2 = vis_keywords.loc[vis_keywords['keywords'].notnull(), ['visitorId', 'keywords']]
print(vis_keywords2.shape)

# aggrouping visitors data
vis_keywords2 = vis_keywords2.groupby('visitorId', as_index=False).agg({'keywords': lambda x: list(set([it for subit in x for it in subit]))})
# flattening data
vis_keywords2_flat = pd.DataFrame([[i, x] for i, y in vis_keywords2['keywords'].apply(list).iteritems() for x in y], columns=list(['I','keywords'])).set_index('I')
vis_keywords2_flat = vis_keywords2[['visitorId']].merge(vis_keywords2_flat, left_index=True, right_index=True)
# saving data
vis_keywords2_flat.to_csv('data-gathering/partial_data/vis_keywords_flat.csv', index=False)


####################################################################################################
# tests for patterns possibilities

tests = vis_keywords['description_parsed'].values
# loop for testing
print()
amostra = [random.choice(tests) for _ in range(75)]
print(len(amostra))
gram=r'KT: {<prop><prop>}'
for texto in amostra:
    te = GetCandidatesChunks(texto, gram)
    for it in te:
        print(it)

# PATTERNS
# SIM
<n><adj>  # as vezes pega duplas
<n><prp><n>
<prop><prop>  # as vezes pega duplas

# TALVEZ # testar opcoes
<adj><prp><v-inf>
<adv><adv><v-fin>
<n><prp><n><v-pcp>
<prop><prp><n>
<n><adv>

# TALVEZ -> pegar partes
<adj><n>  # as vezes pega duplas
<adv><conj-c><adj>

# NAO
<n><prp><n><adj><n>
<prop><v-fin><n>

###################################################################################################
##############################################################################








