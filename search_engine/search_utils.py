import collections
import json
import math


def cosine_similarity(query, doc_term_freq, inverted_index, N):
    epsilon = 1e-8
    product = 0.0
    query_norm = epsilon
    doc_norm = epsilon
    doc_tfidf = {}
    query_tfidf = {}
    for term in query:
        if term in query_tfidf:
            query_tfidf[term] += 1
        else:
            query_tfidf[term] = 1
    for term, _ in query_tfidf.items():
        if not term in inverted_index:
            query_tfidf[term] = 0
            continue
        query_tfidf[term] = (1 + math.log(epsilon + query_tfidf[term]) / math.log(10)) * math.log( N * 1.0 / len(inverted_index[term]))
        query_norm += query_tfidf[term]**2
    for term, _ in doc_term_freq.items():
        if not term in inverted_index:
            continue
        doc_tfidf[term] = (1 + math.log(epsilon + doc_term_freq[term]) / math.log(10)) * math.log( N * 1.0 / len(inverted_index[term]))
        doc_norm += doc_tfidf[term]**2
    for term, _ in doc_tfidf.items():
        if term in doc_tfidf and term in query_tfidf:
            product += doc_tfidf[term] * query_tfidf[term]
    return product / (query_norm * doc_norm)


def get_idf(invertedIndex):
    # output = {term: len(invertedIndex[term]) for term in invertedIndex.keys()}
    # with open('../dataset/indexing_dataset/tf_idf/idf.json', 'w') as idf_file:
    #     idf_file.write((json.dumps(output) + "\n"))

    return {term: len(invertedIndex[term]) for term in invertedIndex.keys()}


def jaccard(query, doc):
    query = query.split(" ")
    query = set(query)
    return len(query & doc) / math.sqrt(len(query | doc))

def get_bow(term_list):
    term_list = term_list.split(" ")
    bow = collections.defaultdict(int)
    for term in term_list:
        bow[term] += 1
    return bow


def get_high_idf_docs(query, idf, invertedIndex, idf_threshold):
    valid_docs = set()
    query = query.split(" ")
    for term in query:
        if term in idf:
            term_idf = idf[term]
            if term_idf < idf_threshold:
                valid_docs = valid_docs | set(invertedIndex[term].keys())
    return valid_docs

def get_tf_idf_score(tf, idf, N):
    idf = math.log(N / idf, 10)
    tf_idf = tf * idf
    return tf_idf

def get_tf_idf(term_list, idf, N):
    tf = get_bow(term_list)
    tf_idf = {}

    for term in set(term_list.split(" ")):
        if term in idf:
            tf_idf[term] = get_tf_idf_score(tf[term], idf[term], N)
    return tf_idf

def get_all_docs(invertedIndex):
    valid_docs = set()
    for term in invertedIndex.keys():
        keys = set(invertedIndex[term].keys())
        valid_docs = valid_docs | keys
    return valid_docs