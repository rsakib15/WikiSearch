from indexing.data_loader import InvertedIndexData, DocumentVectorIndexData, tf_idf_data, LoadInvertedIndex
from indexing.index_main import load_meta
from ranking.rank_utils import heap, similarity
from search_engine.search_utils import get_high_idf_docs, get_idf, get_tf_idf, get_all_docs


class HIGH_TF_IDF(object):
    def __init__(self):
        self.tf_idf_DocVecIndex = tf_idf_data()
        self.document_vector_index_data = DocumentVectorIndexData()
        self.inverted_index_meta_data = InvertedIndexData()
        self.invertedIndex = LoadInvertedIndex()
        self.total_documents = len(self.document_vector_index_data)
        self.idf_threshold = int(0.5 * self.total_documents)
        self.idf = get_idf(self.inverted_index_meta_data)

    def search(self, query):
        query_vec = get_tf_idf(query, self.idf, self.total_documents)
        val_docs = get_high_idf_docs(query, self.idf, self.invertedIndex, self.idf_threshold)
        scores = {}
        for docID in val_docs:
            scores[docID] = similarity(query_vec, self.tf_idf_DocVecIndex[str(docID)])

        return (heap(scores, 10), query)