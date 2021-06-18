import math
from indexing.data_loader import InvertedIndexData, DocumentVectorIndexData, tf_idf_data, LoadInvertedIndex
from indexing.index_main import load_meta
from ranking.rank_utils import heap
from search_engine.search_utils import get_high_idf_docs, get_idf

class Jaccard(object):
    def __init__(self,doc_vec_data, inv_data,idf_data):
        self.document_vector_index_data = doc_vec_data
        self.inverted_index_meta_data = inv_data
        self.invertedIndex = LoadInvertedIndex()
        self.total_documents = len(self.document_vector_index_data)
        self.idf_threshold = int(0.5 * self.total_documents)
        self.idf = idf_data

    def jaccard(self, query, doc):
        query = set(query)
        return len(query & doc) / math.sqrt(len(query | doc))

    def search(self, query):
        val_docs = get_high_idf_docs(query, self.idf, self.invertedIndex, self.idf_threshold)
        scores = {}

        for docID in val_docs:
            scores[docID] = self.jaccard(query, set(self.document_vector_index_data[str(docID)].keys()))

        return (heap(scores, 10), query)

