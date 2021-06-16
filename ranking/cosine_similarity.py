import json
import time

from indexing.data_loader import InvertedIndexData, LoadDocVecIndex, LoadInvertedIndex
from indexing.index_main import load_meta
from ranking.rank_utils import heap
from search_engine.search_utils import cosine_similarity

class CosineSearch(object):
    def __init__(self):
        start = time.time()
        self.inverted_index_data = LoadInvertedIndex()
        self.document_vector_index_data = LoadDocVecIndex()
        self.meta_data_dir = '../dataset/indexing_dataset/meta.json'
        self.article_mata = load_meta(self.meta_data_dir)
        elapsed = time.time() - start
        return

    def search(self, query):
        N = len(self.article_mata)
        result = []
        query = query.split(" ")

        for q_term in query:
            if q_term in self.inverted_index_data:
                for key, _ in self.inverted_index_data[q_term].items():
                    result += [key]
        result = list(set(result))

        for q_term in query:
            if q_term in self.inverted_index_data:
                temp = []
                for key, _ in self.inverted_index_data[q_term].items():
                    temp += [key]
                result = list(set(result).intersection(set(temp)))

        score = {}
        for doc_id in result:
            score[doc_id] = cosine_similarity(query, self.document_vector_index_data[doc_id],self.inverted_index_data, N)
        scores = {k: v for k, v in sorted(score.items(), key=lambda item: item[1], reverse=True)}

        return (heap(scores, 10), query)