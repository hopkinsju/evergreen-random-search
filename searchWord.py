#!/usr/bin/python

import requests
import time
import random
import pylab as plt
import numpy as np


class BasicSearch(object):
    def __init__(self, debug=False):
        self.catalog_url = 'http://missourievergreen.org/eg/opac/results' // TODO parameterize this
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
    def __init__(self):
        BasicSearch.__init__(self)
        self.search_params = {
            'qtype': 'title'
        }

    def __str__(self):
        return "TitleSearch"

class BasicMetabibSearch(BasicSearch):
    def __init__(self):
        BasicSearch.__init__(self)
        self.search_params = {
            'modifier': 'metabib'
        }

    def __str__(self):
        return "BasicMetabibSearch"

class TitleMetabibSearch(BasicSearch):
    def __init__(self):
        BasicSearch.__init__(self)
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
    wordnik_api_key = '' // NOTE Gonna need to put this into a config file or parameter
    wordnik_url = 'http://api.wordnik.com/v4/words.json/randomWords'

    wordnik_params = {
        "hasDictionaryDef": "true",
        "includePartOfSpeech": "noun",
        "minDictionaryCount": "3",
        "minCorpusCount": "10000",
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
    random.shuffle(words)
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
    search_types = [
        BasicSearch(),
        BasicMetabibSearch(),
        TitleSearch(),
        TitleMetabibSearch()
    ]
    word_list = gen_random_words(num_trials * len(search_types))
    results = []
    for search in search_types:
        for i in range(num_trials):
            word = word_list.next()
            search_time = search.timed_search(word)
            results.append((str(search), word, search_time))
    return results

def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            plt.text(rect.get_x()+rect.get_width()/2., 1.05*height, '%.2f'%height,
                    ha='center', va='bottom')

def plot_average_times(results):
    # Sort results so the bars go in order
    results.sort(None,key=lambda x: x[0]+str(x[2]))

    results_by_type = {}
    for i in results:
        try:
            results_by_type[i[0]].append(i[2])
        except KeyError:
            results_by_type[i[0]] = [i[2]]

    averages = []
    for x in results_by_type.keys():
        averages.append([x,sum(results_by_type[x])/len(results_by_type[x])])

    averages.sort(None, key=lambda x: x[1])
    print averages

    # Format the bars and their spacing
    X = np.arange(len(averages))
    plt.title("Comparison of search times by type")
    rects1 =plt.bar(X, [x[1] for x in averages], align='center', width=0.5)
    plt.xticks(X, [x[0] for x in averages])
    ymax = max([x[1] for x in averages]) + 1
    plt.ylim(0, ymax)
    plt.ylabel('Average search time in seconds')
    plt.xlabel('Search type')

    autolabel(rects1)

    plt.show()


results = simulate_searches(20)

plot_average_times(results)

