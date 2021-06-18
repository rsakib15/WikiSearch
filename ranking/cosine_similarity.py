import json
import time

from indexing.data_loader import InvertedIndexData, LoadDocVecIndex, LoadInvertedIndex
from indexing.index_main import load_meta
from ranking.rank_utils import heap
from search_engine.search_utils import cosine_similarity

class CosineSearch(object):
    def __init__(self, doc_vec_data, inv_data,meta_file):
        start = time.time()
        self.inverted_index_data = inv_data
        self.document_vector_index_data = doc_vec_data
        self.meta_data_dir = '../dataset/indexing_dataset/meta.json'
        self.article_mata = load_meta(self.meta_data_dir)
        return

    def search(self, query ):
        N = len(self.article_mata)
        result = []
        q = query.split(" ")

        for q_term in q:
            if q_term in self.inverted_index_data:
                for key, _ in self.inverted_index_data[q_term].items():
                    result += [key]
        result = list(set(result))

        for q_term in q:
            if q_term in self.inverted_index_data:
                temp = []
                for key, _ in self.inverted_index_data[q_term].items():
                    temp += [key]
                result = list(set(result).intersection(set(temp)))

        score = {}
        for doc_id in result:
            score[doc_id] = cosine_similarity(query, self.document_vector_index_data[doc_id],self.inverted_index_data, N)
        scores = {k: v for k, v in sorted(score.items(), key=lambda item: item[1], reverse=True)}
        print(scores)
        return heap(scores, 10), query