import json
import os
import sys

from tqdm import tqdm

from indexing.index_helper import parseWikiJsons, getTerms
import multiprocessing as mp

class InvertedIndex(object):
    def __init__(self, wikis):
        self.index_folder = '../dataset/indexing_dataset/inverted_index'
        self.wikis = wikis

    def save_inverted_index(self, meta_info, meta_file_dir):
        with open(meta_file_dir,'w') as index_meta:
            for doc_id, (filename, line) in meta_info.items():
                filename = filename.split("/")[-1]
                filename = filename.split(".")
                filename = int(filename[1])
                index_meta.write(json.dumps({doc_id:(filename,line)}) + "\n")

    def genrate_inverted_index(self, article, n):
        index_file_dir = os.path.join(self.index_folder, "inverted_index." + str(n) + ".json")
        meta_file_dir = os.path.join(self.index_folder, "inverted_index_meta." + str(n) + ".json")

        if os.path.exists(index_file_dir) and os.path.exists(meta_file_dir):
            return

        wiki_data = parseWikiJsons(article)
        inverted_index = dict()
        for article in tqdm(wiki_data):
            doc_id = article["uid"]
            text = getTerms(article["text"])
            title = getTerms(article["title"])
            for word in text:
                if not word in inverted_index:
                    inverted_index[word] = {doc_id: 1}
                else:
                    if not doc_id in inverted_index[word]:
                        inverted_index[word][doc_id] = 1
                    else:
                        inverted_index[word][doc_id] += 1
        meta_info = {}

        with open(index_file_dir, "w") as index_file:
            count = 1
            for term, doc_list in inverted_index.items():
                meta_info[term] = (os.path.join(self.index_folder, "inverted_index." + str(n) + ".json"), count)
                index_file.write(json.dumps({term:doc_list}) + "\n")
                count += 1
        self.save_inverted_index(meta_info, meta_file_dir)

    def get_meta_data(self):
        terms = []
        term_meta = {}
        for i in range(len(self.wikis)):
            print("Scraping " + str(i) + " data.")
            with open(os.path.join(self.index_folder, "inverted_index_meta." + str(i) + ".json")) as ind_meta:
                line = ind_meta.readline()
                while line:
                    meta = eval(line)
                    terms += list(meta.keys())
                    line = ind_meta.readline()

        terms = list(set(terms))

        for i in range(len(terms)):
            term_meta[terms[i]] = []

        for i in range(len(self.wikis)):
            print("Scraping meta " + str(i) + " data.")
            with open(os.path.join(self.index_folder, "inverted_index_meta." + str(i) + ".json")) as ind_meta:
                line = ind_meta.readline()
                while line:
                    meta = eval(line)
                    for k, v in meta.items():
                        term_meta[k].append(v)
                    line = ind_meta.readline()
        return terms, term_meta

    def merge_inverted_index(self):
        terms, term_meta = self.get_meta_data()
        meta_file_dir = os.path.join(self.index_folder, "meta.json")

        with open(meta_file_dir,"w") as meta_data_writer:
            for term in tqdm(terms):
                # meta_data_writer.write(json.dumps({term: (filename, line)}) + "\n")
                meta_data_writer.write(json.dumps({term:(term_meta[term])}) + "\n")

    def create_index(self):
        for i in range (len(self.wikis)):
            self.genrate_inverted_index(self.wikis[i], i)

        self.merge_inverted_index()

        for i in range(len(self.wikis)):
            os.remove(os.path.join(self.index_folder, "inverted_index_meta." + str(i) + ".json"))