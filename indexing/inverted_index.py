import json
import os
import sys

from index_helper import parseWikiJsons, getTerms
import multiprocessing as mp

class InvertedIndex(object):
    def __init__(self, wikis):
        self.IndexFolder = '../dataset/indexing_dataset/inverted_index'
        self.wikis = wikis

    def save_inverted_index(self, metaInfo, meta_file_dir):
        with open(meta_file_dir,'w') as index_meta:
            for docid, (filename, lineno) in metaInfo.items():
                index_meta.write(json.dumps({docid: (filename, lineno)}) + "\n")

    def saveInvertedIndexMeta(self,term2F):
        print("in saveInveter")
        with open(os.path.join(self.IndexFolder, "inverted_index_meta.json"),'w') as ind_meta:
            for term, filename_lineno in term2F.items():
                ind_meta.write(json.dumps({term: filename_lineno}) + "\n")

    def genrate_inverted_index(self, article, n):
        index_file_dir = os.path.join(self.IndexFolder, "inverted_index." + str(n) + ".json")
        meta_file_dir = os.path.join(self.IndexFolder, "inverted_index_meta." + str(n) + ".json")

        articles = parseWikiJsons(article)
        invertedIndex = dict()
        for article in articles:
            doc_id = article["uid"]
            text = getTerms(article["text"])
            for word in text:
                if not word in invertedIndex:
                    invertedIndex[word] = {doc_id: 1}
                else:
                    if not doc_id in invertedIndex[word]:
                        invertedIndex[word][doc_id] = 1
                    else:
                        invertedIndex[word][doc_id] += 1

        metaInfo = {}

        with open(index_file_dir, "w") as indfile:
            lineno = 1
            for term, doc_list in invertedIndex.items():
                metaInfo[term] = (os.path.join(self.IndexFolder, "inverted_index" + str(n) + ".json"), lineno)
                indfile.write(json.dumps({term: doc_list}) + "\n")
                lineno += 1
        indfile.close()
        self.save_inverted_index(metaInfo, meta_file_dir)

    def generate_one_meta(self):
        with open(os.path.join(self.IndexFolder, "meta.json"), 'w') as finalmeta:
            for i in range(len(self.wikis)):
                meta_file_dir = os.path.join(self.IndexFolder, "inverted_index_meta." + str(i) + ".json")
                with open(meta_file_dir, 'r') as indmeta:
                    line = indmeta.readline()
                    while line:
                        tmp = json.loads(line)
                        for docid, (_, lineno) in tmp.items():
                            finalmeta.write(json.dumps({docid: (os.path.join(self.IndexFolder, "inverted_index_meta." + str(i) + ".json"), lineno)}) + "\n")
                        line = indmeta.readline()
                indmeta.close()
                os.remove(meta_file_dir)
        finalmeta.close()


    def getMetaData(self):
        terms = []
        term2F = {}
        for i in range(len(self.wikis)):
            with open(os.path.join(self.IndexFolder, "inverted_index_meta." + str(i) + ".json")) as ind_meta:
                line = ind_meta.readline()
                while line:
                    meta = eval(line)
                    terms += list(meta.keys())
                    line = ind_meta.readline()

        terms = list(set(terms))

        for i in range(len(terms)):
            term2F[terms[i]] = []

        for i in range(len(self.wikis)):
            with open(os.path.join(self.IndexFolder, "inverted_index_meta." + str(i) + ".json")) as ind_meta:
                line = ind_meta.readline()
                while line:
                    meta = eval(line)
                    for k, v in meta.items():
                        term2F[k].append(v)
                    line = ind_meta.readline()
        return terms, term2F

    def merge_inverted_index(self):
        terms, terms2F = self.getMetaData()
        print(len(terms))
        meta_file_dir = os.path.join(self.IndexFolder, "inverted_index_meta.json")

        with open(meta_file_dir,"w") as meta_data_writer:
            for term in terms:
                meta_data_writer.write(json.dumps({term: terms2F[term]}) + "\n")

    def create_index(self):
        cpu_num = mp.cpu_count()
        mp_pool = mp.Pool(cpu_num)
        mp_pool.starmap(self.genrate_inverted_index, [(self.wikis[i], i) for i in range(len(self.wikis))])
        self.merge_inverted_index()