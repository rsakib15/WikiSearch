from wikisearch.searcher.score import similarity
from indexing.data_loader import InvertedIndexData, DocumentVectorIndexData, tf_idf_data
from ranking.rank_utils import heap
from search_engine.search_utils import get_bow, get_high_idf_docs, get_idf, get_tf_idf_score


class BOW(object):
    def __init__(self, doc_vec_data, inv_data,idf_data):
        self.document_vector_index_data = doc_vec_data
        self.inverted_index_meta_data = inv_data
        self.tf_idf_DocVecIndex = tf_idf_data()
        self.total_documents = len(self.document_vector_index_data)
        self.idf_threshold = int(0.5 * self.total_documents)
        self.idf = idf_data

    def naive_jaccard(self, query, title):
        query = set(query)
        return len(query & title) / len(query | title)

    def search(self, query):
        query_vec = get_bow(query)
        val_docs = get_high_idf_docs(query, self.idf, self.inverted_index_meta_data, self.idf_threshold)
        scores = {}
        for docID in val_docs:
            res = {}
            for term in self.document_vector_index_data[docID]:
                tf = self.document_vector_index_data[docID][term] / len(self.document_vector_index_data[docID])
                idf_data = self.idf[term]
                res[term] = get_tf_idf_score(tf, idf_data, self.total_documents)
            scores[docID] = similarity(query_vec, res)

        return heap(scores, 10), query

