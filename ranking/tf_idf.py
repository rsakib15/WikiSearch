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

    def search(self, query):
        query_vec = get_tf_idf(query, self.idf, self.total_documents)
        val_docs = get_all_docs(self.invertedIndex)
        scores = {}
        for docID in val_docs:
            scores[docID] = similarity(query_vec, self.tf_idf_DocVecIndex[str(docID)])

        return scores

