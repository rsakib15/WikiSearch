from wikisearch.searcher.score import similarity
from indexing.data_loader import InvertedIndexData, DocumentVectorIndexData, tf_idf_data
from ranking.rank_utils import heap
from search_engine.search_utils import get_bow, get_high_idf_docs, get_idf


class BOW(object):
    def __init__(self):
        self.document_vector_index_data = DocumentVectorIndexData()
        self.inverted_index_meta_data = InvertedIndexData()
        self.tf_idf_DocVecIndex = tf_idf_data()
        self.total_documents = len(self.document_vector_index_data)
        self.idf_threshold = int(0.5 * self.total_documents)
        self.idf = get_idf(self.inverted_index_meta_data)

    def naive_jaccard(self, query, title):
        query = set(query)
        return len(query & title) / len(query | title)

    def search(self, query):
        query_vec = get_bow(query)
        val_docs = get_high_idf_docs(query, self.idf, self.inverted_index_meta_data, self.idf_threshold)
        scores = {}
        for docID in val_docs:
            scores[docID] = similarity(query_vec, self.tf_idf_DocVecIndex[docID])

        return (heap(scores, 10), query)

