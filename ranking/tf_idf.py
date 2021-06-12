from heapq import heapify, heappush, heappop

from wikisearch.searcher.score import similarity

from indexing.data_loader import InvertedIndexData, DocumentVectorIndexData, tf_idf_data, LoadInvertedIndex
from indexing.index_main import load_meta
from search_engine.search_utils import get_bow, get_high_idf_docs, get_idf, get_tf_idf, get_all_docs


class TF_IDF(object):
    def __init__(self):
        self.tf_idf_DocVecIndex = tf_idf_data()
        self.document_vector_index_data = DocumentVectorIndexData()
        self.inverted_index_meta_data = InvertedIndexData()
        self.invertedIndex = LoadInvertedIndex()
        self.total_documents = len(self.document_vector_index_data)
        self.idf_threshold = int(0.5 * self.total_documents)
        self.idf = get_idf(self.inverted_index_meta_data)
        self.total_documents = len(self.document_vector_index_data)
        self.meta_data_dir = 'dataset/indexing_dataset/meta.json'
        tf_idf_file = 'dataset/indexing_dataset/tf_idf'
        self.meta_data = load_meta(self.meta_data_dir)

    def heap(self, scores, top_k):
        heap = []
        heapify(heap)
        for doc in scores:
            heappush(heap, (-scores[doc], doc))

        top_k_docs = []
        num = min(len(heap), top_k)
        for i in range(num):
            top_k_docs.append(heappop(heap)[1])
        return top_k_docs

    def naive_jaccard(self, query, title):
        query = set(query)
        return len(query & title) / len(query | title)

    def search(self, query):
        query_vec = get_tf_idf(query, self.idf, self.total_documents)
        val_docs = get_all_docs(self.invertedIndex)
        scores = {}
        for docID in val_docs:
            scores[docID] = similarity(query_vec, self.tf_idf_DocVecIndex[str(docID)])

        return (self.heap(scores, 10), query)

