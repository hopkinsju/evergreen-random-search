#!/usr/bin/python

import requests
import time
import math
import pylab as pl
import numpy as np


class BasicSearch(object):
    def __init__(self, catalog_url, debug=False):
        self.catalog_url = catalog_url
        self.debug = debug
        self.search_params = {
        }

    def do_search(self, query):
        """
        Perform the search against the catalog
        :rtype : response object
        :param query: search term
        :return: full response object
        """
        self.search_params['query'] = query
        r = requests.get(self.catalog_url, self.search_params)
        r.raise_for_status()
        if self.debug:
            print r, self.search_params
        return r

    def timed_search(self, query):
        """
        Track time required to perform a search
        :rtype : float
        :param query: search terms
        :return: seconds required for search to complete
        """
        start = time.time()
        self.do_search(query)
        end = time.time()
        return end - start

    def __str__(self):
        return "BasicSearch"

class TitleSearch(BasicSearch):
    def __init__(self, catalog_url):
        BasicSearch.__init__(self, catalog_url)
        self.search_params = {
            'qtype': 'title'
        }

    def __str__(self):
        return "TitleSearch"

class BasicMetabibSearch(BasicSearch):
    def __init__(self, catalog_url):
        BasicSearch.__init__(self, catalog_url)
        self.search_params = {
            'modifier': 'metabib'
        }

    def __str__(self):
        return "BasicMetabibSearch"

class TitleMetabibSearch(BasicSearch):
    def __init__(self, catalog_url):
        BasicSearch.__init__(self, catalog_url)
        self.search_params = {
            'qtype': 'title',
            'modifier': 'metabib'
        }

    def __str__(self):
        return "TitleMetabibSearch"

def gen_random_words(count):
    """
    Get a list of words, hopefully not too obscure using the Wordnik API.
    We get a list so that we can save on API calls and return one at a time
    Returns an array of words or None if API returns non-200 status code
    """
    wordnik_api_key = '***REMOVED***'
    wordnik_url = 'http://api.wordnik.com/v4/words.json/randomWords'

    wordnik_params = {
        "hasDictionaryDef": "true",
        "includePartOfSpeech": "noun",
        "minDictionaryCount": "3",
        "minCorpusCount": "100",
        "minLength": 6,
        "useCannonical": "true",
        "limit": count,
        "api_key": wordnik_api_key
    }
    r = requests.get(wordnik_url, params=wordnik_params)
    r.raise_for_status()
    words = []
    for el in xrange(len(r.json())):
        words.append(r.json()[el]['word'])
    print "fetching", len(words), "words\n", words
    for word in words:
        yield word


def simulate_searches(num_trials):
    """
    Run random catalog searches using random words and various search types
    :rtype : dict
    :param num_trials: number of random words to use per search type
    :return: dictionary of search times by search type
    """
    catalog_url = 'http://missourievergreen.org/eg/opac/results'
    search_types = [
        BasicSearch(catalog_url),
        BasicMetabibSearch(catalog_url),
        TitleSearch(catalog_url),
        TitleMetabibSearch(catalog_url)
    ]
    word_list = gen_random_words(num_trials * len(search_types))
    all_results = {}
    for search in search_types:
        results_for_type = []
        for i in range(num_trials):
            results_for_type.append(search.timed_search(word_list.next()))
        all_results[str(search)] = results_for_type
    return all_results

results = simulate_searches(30)
def plot_simulation(results):
    averages = {}
    for i in results.keys():
        averages[i] = sum(results[i])/len(results[i])

    print averages
    X = np.arange(len(averages))
    pl.bar(X, averages.values(), align='center', width=0.5)
    pl.xticks(X, averages.keys())
    ymax = max(averages.values()) + 1
    pl.ylim(0, ymax)
    pl.show()

plot_simulation(results)
#
# for i in range(3):
#     searchCatalog(word.next())
