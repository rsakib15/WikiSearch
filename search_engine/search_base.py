import codecs
import json
import os
import time

from tqdm import tqdm
from heapq import heappop, heappush, heapify

from wikisearch.searcher.score import similarity

from indexing.data_loader import InvertedIndexData
from indexing.data_loader import DocumentVectorIndexData, LoadInvertedIndex
from indexing.index_main import load_meta
from ranking.bag_of_words import BOW
from search_engine.search_utils import get_idf, get_tf_idf_score, get_tf_idf, get_all_docs, jaccard, get_high_idf_docs, get_bow


class SearchEngineBase(object):
    def __init__(self):
        pass

    def search(self, query, dump):
        raise NotImplementedError

    def rank(self, results):
        raise NotImplementedError


def heap(scores, top_k):
    heap = []
    heapify(heap)
    for doc in scores:
        print(doc)
        heappush(heap, (-scores[doc], doc))

    top_k_docs = []
    num = min(len(heap), top_k)
    for i in range(num):
        top_k_docs.append(heappop(heap)[1])
    return top_k_docs


class Searcher(SearchEngineBase):
    def __init__(self, proc_num=1, idf_threshold=0.5, terms=3, seed=-1, cluster_load=-1, tf_idf=-1):
        super().__init__()
        self.meta_data_dir = '../dataset/indexing_dataset/meta.json'
        tf_idf_file = '../dataset/indexing_dataset/tf_idf'
        self.meta_data = load_meta(self.meta_data_dir)
        self.inverted_index_meta_data = InvertedIndexData()
        self.invertedIndex = LoadInvertedIndex()
        self.document_vector_index_data = DocumentVectorIndexData()
        self.total_documents = len(self.document_vector_index_data)
        self.terms = terms
        self.seed = seed
        self.idf_threshold = int(idf_threshold * self.total_documents)
        self.idf = get_idf(self.inverted_index_meta_data)

        if tf_idf == 0:
            self.tf_idf_DocVecIndex = {}

            for doc in tqdm(self.document_vector_index_data.keys()):
                self.tf_idf_DocVecIndex[doc] = {}
                for term in self.document_vector_index_data[doc]:
                    tf = self.document_vector_index_data[doc][term]/len(self.document_vector_index_data[doc])
                    idf = self.idf[term]
                    self.tf_idf_DocVecIndex[doc][term] = get_tf_idf_score(tf, idf, self.total_documents)

            if not os.path.exists(tf_idf_file):
                os.makedirs(tf_idf_file)

            with open(os.path.join(tf_idf_file, "tf_idf.json"), "w") as f:
                json.dump(self.tf_idf_DocVecIndex, f)
            print(self.tf_idf_DocVecIndex)

        if tf_idf == 1:
            with open(os.path.join(tf_idf_file, "tf_idf.json"), "r") as f:
                self.tf_idf_DocVecIndex = json.load(f)

    def process_query(self, query):
        new_query = []
        for index, term in enumerate(query):
            new_term = term.replace(" ", "")
            if new_term:
                new_query.append(new_term)
        query = new_query

        # Remove non-chinese character
        for index, term in enumerate(query):
            valid_chrs = ""
            for ch in term:
                valid_chrs += ch
            query[index] = valid_chrs

        # Remove stop words
        clean_query = []
        for term in query:
            clean_query.append(term)

        return clean_query

    def naive_jaccard(self, query, title):
        query = set(query)
        return len(query & title) / len(query | title)

    def search(self, query, top_k=10, score="tf-idf", filter_type="heap"):
        query_vec = get_tf_idf(query, self.idf, self.total_documents)
        val_docs = get_high_idf_docs(query, self.idf, self.invertedIndex,self.idf_threshold)

        # title_scores = {}
        # for doc in val_docs:
        #     title = (self.meta_data[str(doc)]["title"])
        #     title = list(title)
        #     title = self.process_query(title)
        #
        #     title_scores[doc] = self.naive_jaccard(set(query), set(title))

        scores = {}
        for docID in val_docs:
            scores[docID] = similarity(query_vec, self.tf_idf_DocVecIndex[str(docID)])


        # scores = {}
        # if score == "bow":
        #     scores = bag_of_words(query)
        #     print("on bow")
        #     query_vec = get_bow(query)
        #     print(query_vec)
        #     val_docs = get_high_idf_docs(query,self.idf,self.inverted_index_meta_data,self.idf_threshold)
        #     print(val_docs)
        #     title_scores = {}
        #     for doc in val_docs:
        #         title = list(self.meta_data[doc]["title"])
        #         title = self.process_query(title)
        #         title_scores[doc] = self.naive_jaccard(set(query), set(title))
        #
        #     for docID in val_docs:
        #         scores[docID] = similarity(query_vec, self.tf_idf_DocVecIndex[docID])

        # if score == "tf-idf":
        #     print("on tf-idf")
        # if score == "high-tf-idf":
        #     print("on high-tf-idf")
        # if score == "jaccard":
        #     print("on jaccard")
        # if score == "cosine":
        #     print("on high-tf-idf")

        print(scores)

        return (heap(scores, top_k), query)


