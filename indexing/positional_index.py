import json
import os
import sys

from tqdm import tqdm

from indexing.index_helper import parseWikiJsons, getTerms
import multiprocessing as mp

class PositionalIndex(object):
    def __init__(self, wikis):
        self.index_folder = '../dataset/indexing_dataset/positional_index'
        self.wikis = wikis

    def save_positional_index(self, meta_info, meta_file_dir):
        with open(meta_file_dir,'w') as index_meta:
            for doc_id, (filename, line) in meta_info.items():
                index_meta.write(json.dumps({doc_id: (filename, line)}) + "\n")

    def genrate_positional_index(self, article, n):
        index_file_dir = os.path.join(self.index_folder, "positional_index." + str(n) + ".json")
        meta_file_dir = os.path.join(self.index_folder, "positional_index_meta." + str(n) + ".json")

        wiki_data = parseWikiJsons(article)
        positional_index = dict()

        for article in tqdm(wiki_data):
            doc_id = article["uid"]
            text = getTerms(article["text"])
            title = getTerms(article["title"])
            for pos, word in enumerate(text):
                if not word in positional_index:
                    positional_index[word] = {}
                if not doc_id in positional_index[word]:
                    positional_index[word][doc_id] = [pos]
                else:
                    positional_index[word][doc_id].append(pos)

        meta_info = {}

        with open(index_file_dir, "w") as index_file:
            count = 1
            for term, doc_list in positional_index.items():
                meta_info[term] = (n, count)
                index_file.write(json.dumps({term: doc_list}) + "\n")
                count += 1
        index_file.close()
        self.save_positional_index(meta_info, meta_file_dir)

    def get_meta_data(self):
        terms = []
        term_meta = {}
        for i in range(len(self.wikis)):
            print("Scraping " + str(i) + " data.")
            with open(os.path.join(self.index_folder, "positional_index_meta." + str(i) + ".json")) as index_meta:
                line = index_meta.readline()
                while line:
                    meta = eval(line)
                    terms += list(meta.keys())
                    line = index_meta.readline()
            index_meta.close()
        terms = list(set(terms))

        for i in range(len(terms)):
            term_meta[terms[i]] = []

        for i in range(len(self.wikis)):
            print("Scraping meta " + str(i) + " data.")
            with open(os.path.join(self.index_folder, "positional_index_meta." + str(i) + ".json")) as index_meta:
                line = index_meta.readline()
                while line:
                    meta = eval(line)
                    for k, v in meta.items():
                        term_meta[k].append(v)
                    line = index_meta.readline()
            index_meta.close()
        return terms, term_meta

    def merge_positional_index(self):
        terms, term_meta = self.get_meta_data()
        meta_file_dir = os.path.join(self.index_folder, "meta.json")

        with open(meta_file_dir,"w") as meta_data_writer:
            for term in tqdm(terms):
                meta_data_writer.write(json.dumps({term: term_meta[term]}) + "\n")

    def create_index(self):
        cpu_num = mp.cpu_count()
        mp_pool = mp.Pool(cpu_num)
        mp_pool.starmap(self.genrate_positional_index, [(self.wikis[i], i) for i in range(len(self.wikis))])
        self.merge_positional_index()

        for i in range(len(self.wikis)):
            os.remove(os.path.join(self.index_folder, "positional_index_meta." + str(i) + ".json"))

