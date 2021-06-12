from wikisearch.searcher.score import similarity
from indexing.data_loader import InvertedIndexData, DocumentVectorIndexData, tf_idf_data, LoadPositionalIndex
from indexing.index_main import load_meta
import bisect
import multiprocessing as mp



class Proximity(object):
    def __init__(self):
        self.positionalIndex = LoadPositionalIndex()
        self.meta_data_dir = 'dataset/indexing_dataset/meta.json'
        self.meta_data = load_meta(self.meta_data_dir)

    def positional_search(self, query, doc_id):
        q_term_pos = []
        for q_term in query:
            q_term_pos.append(self.positionalIndex[q_term][doc_id])
        for first_q_term_pos in q_term_pos[0]:
            last_pos = first_q_term_pos
            for term_id in range(1, len(query)):
                pos = bisect.bisect_left(q_term_pos[term_id], last_pos + 1)
                if pos < len(q_term_pos[term_id]) and pos >= 0:
                    last_pos = q_term_pos[term_id][pos] + 1
                else:
                    last_pos = -1
                    break
            if last_pos >= 0:
                return doc_id
        return -1

    def search(self, query):
        query = query.split(" ")
        result = list(self.positionalIndex[query[0]].keys()) if query[0] in self.positionalIndex else []

        for q_term in query:
            if q_term in self.positionalIndex:
                result = list(set(result).intersection(set(self.positionalIndex[q_term].keys())))
            else:
                result = []
                break

        for res in result:
            self.positional_search(query,res)

        pool = mp.Pool(12)
        matched_doc_id = pool.starmap(self.positional_search,[(query, res) for res in result])

        result = []
        for doc_id in matched_doc_id:
            if doc_id >= 0:
                result.append({
                    "url": self.meta_data[str(doc_id)]["url"],
                    "title": self.meta_data[str(doc_id)]["title"]
                })

        return result


