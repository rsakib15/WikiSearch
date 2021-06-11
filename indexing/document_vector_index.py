import json
import os
from indexing.index_helper import parseWikiJsons, getTerms
import multiprocessing as mp
from tqdm import tqdm

class DocumentVectorIndex(object):
    def __init__(self, wikis):
        self.index_folder = 'dataset/indexing_dataset/document_vector_index'
        self.wikis = wikis

    def save_document_vector_index(self, meta_info, meta_file_dir):
        with open(meta_file_dir,'w') as index_meta:
            for doc_id, (filename, line) in meta_info.items():
                filename = filename.split(".")
                filename = int(filename[1])
                index_meta.write(json.dumps({doc_id: (filename, line)}) + "\n")

    def genrate_document_vector_index(self, article, n):
        index_file_dir = os.path.join(self.index_folder, "document_vector_index." + str(n) + ".json")
        meta_file_dir = os.path.join(self.index_folder, "document_vector_index_meta." + str(n) + ".json")

        if os.path.exists(index_file_dir) and os.path.exists(meta_file_dir):
            return

        wiki_data = parseWikiJsons(article)

        document_vector_index = {}

        for article in tqdm(wiki_data):
            doc_id = article["uid"]
            document_vector_index[doc_id] = {}
            text = getTerms(article["text"])
            title_term = getTerms(article['title'])

            for word in title_term:
                if not word in document_vector_index[doc_id]:
                    document_vector_index[doc_id][word] = 1
                else:
                    document_vector_index[doc_id][word] += 1

        metaInfo = {}

        with open(index_file_dir, "w") as indfile:
            count = 1
            for docID, term_freq_dict in document_vector_index.items():
                indfile.write(json.dumps({docID: term_freq_dict}) + "\n")
                metaInfo[docID] = (index_file_dir, count)
                count += 1
        indfile.close()
        self.save_document_vector_index(metaInfo, meta_file_dir)

    def generate_one_meta(self):
        with open(os.path.join(self.index_folder, "meta.json"), 'w') as meta_file:
            for i in range(len(self.wikis)):
                meta_file_dir = os.path.join(self.index_folder, "document_vector_index_meta." + str(i) + ".json")
                with open(meta_file_dir, 'r') as div_meta:
                    line = div_meta.readline()
                    while line:
                        data = json.loads(line)
                        for doc_id, (_, lineno) in data.items():
                            meta_file.write(json.dumps({doc_id: (os.path.join(self.index_folder, "document_vector_index." + str(i) + ".json"), lineno)}) + "\n")
                        line = div_meta.readline()
                div_meta.close()
                os.remove(meta_file_dir)
        meta_file.close()

    def create_index(self):
        # cpu_num = mp.cpu_count()
        # mp_pool = mp.Pool(cpu_num)
        # mp_pool.starmap(self.genrate_document_vector_index, [(self.wikis[i], i) for i in range(len(self.wikis))])
        #
        for i in range (len(self.wikis)):
            self.genrate_document_vector_index(self.wikis[i], i)

        self.generate_one_meta()
