import codecs
import json
import os
import re
import time

from indexing.data_loader import InvertedIndexData, DocumentVectorIndexData, LoadIDFData
from indexing.index_main import load_meta
from indexing.tf_idf import genreate_tf_idf, genreate_inv_meta
from ranking.bag_of_words import BOW
from ranking.cosine_similarity import CosineSearch
from ranking.proximity import Proximity
from ranking.tf_idf import TF_IDF
from ranking.high_tf_idf import HIGH_TF_IDF
from ranking.jaccard import Jaccard

print("Meta data loading")
meta_data = load_meta(os.path.join('../dataset/indexing_dataset/meta.json'))
print("Meta data loaded")
from search_engine.search_utils import get_idf

print("DocumentVectorIndexData data loading")
document_vector_index_data = DocumentVectorIndexData()
print("DocumentVectorIndexData data done")
print("InvertedIndexData data loading")
inverted_index_meta_data = InvertedIndexData()
print("InvertedIndexData data done")
# print("IDF Data generating")
# get_idf(inverted_index_meta_data)
# print("IDF Data generated")
print("IDF Data Loading")
idf_data = LoadIDFData()
print("IDF Data Loaded")
print("TF_IDF start")
# genreate_tf_idf(document_vector_index_data,idf_data)
# print("Separate meta start")
# genreate_inv_meta()
# print("Separate meta generated")



def get_text(dir):
    f = open('../dataset/extracted_dataset/json/'+ str(dir) + '.json')
    data = json.load(f)
    f.close()
    return data

def get_summary(docId, words):
    words = words.split(" ")
    doc = get_text(docId)
    text = doc['text']
    sentence = re.findall(r'[^.]*(?:' + '|'.join(words) + r')[^.]*\.', text)
    l = {}
    for s in sentence:
        l[s] = 0
        for w in words:
            if w in s:
                l[s] += 1

    all_s = {k: v for k, v in sorted(l.items(), key=lambda item: item[1], reverse=True)}
    if len(all_s)>0:
        abstract = list(all_s.values())[0]
        abstract = [k for k,v in all_s.items() if v == abstract]
        abstract = max(abstract, key=len)
    else:
        abstract = doc['text'][:300] + "..."

    match_word = [word for word in words if word in abstract or word in doc['title']]

    return {
        'title': doc['title'],
        'text': abstract,
        'words': match_word,
        'url': doc['url'],
        'id': doc['id']
    }

def searcher(query, method):
    query = query.lower()
    print(query)
    print(method)

    #searcher = Searcher(proc_num=8, cluster_load=1, tf_idf=1)
    if method == "bow":
        searcher = BOW(doc_vec_data = document_vector_index_data, inv_data = inverted_index_meta_data, idf_data = idf_data)
    elif method == "jaccard":
        searcher = Jaccard()
    elif method == "highidf":
        searcher = HIGH_TF_IDF()
    elif method == "tfidf":
        searcher = TF_IDF()
    elif method == "cosine":
        searcher = CosineSearch()
    else:
        searcher = BOW(doc_vec_data = document_vector_index_data, inv_data = inverted_index_meta_data, idf_data = idf_data)


    #searcher = CosineSearch()
    print("Search loaded")
    #searcher = Proximity()
    #searcher = TF_IDF()

    begin_time = time.time()
    print("Search start")
    result,words = searcher.search(query)
    print("Search done")

    print(result,words)

    elapsed_time = time.time() - begin_time

    res = []
    for doc in result:
        if str(doc) in meta_data:
            res.append(get_summary(doc,words))

    return {
        "result": res,
        "elapsed_time": elapsed_time
    }


