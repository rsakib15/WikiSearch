import json
import linecache
import os
import pickle
import sys
import zlib
import pandas as pd
from tqdm import tqdm

from indexing.index_main import get_directory_file_list


def tf_idf_data():
    with open(os.path.join("../dataset/indexing_dataset/tf_idf/tf_idf.json"), "r") as f:
        return json.load(f)

def LoadInvertedIndex():
    wikis = get_directory_file_list("../dataset/extracted_dataset/text/")
    l = len(wikis)
    invertedIndex = {}

    for i in range(l):
        with open(os.path.join("../dataset/indexing_dataset/inverted_index/inverted_index." + str(i) + ".json")) as indfile:
            line = indfile.readline()
            while line:
                ind = json.loads(line)
                for k, v in ind.items():
                    if not k in invertedIndex:
                        invertedIndex[k] = {}
                    for _docid, _freq in v.items():
                        invertedIndex[k][int(_docid)] = _freq
                line = indfile.readline()


    return invertedIndex


def LoadDocVecIndex():
    wikis = get_directory_file_list("../dataset/extracted_dataset/text/")
    l = len(wikis)
    DocVecIndex = {}
    for i in range(l):
        with open(os.path.join("../dataset/indexing_dataset/document_vector_index/document_vector_index." + str(i) + ".json")) as indfile:
            line = indfile.readline()
            while line:
                ind = json.loads(line)
                for docid, term_freq_dict in ind.items():
                    DocVecIndex[int(docid)] = {}
                    for _term, _freq in term_freq_dict.items():
                        DocVecIndex[int(docid)][_term] = int(_freq)
                line = indfile.readline()
    return DocVecIndex

def LoadPositionalIndex():
    wikis = get_directory_file_list("../dataset/extracted_dataset/text/")
    l = len(wikis)

    positionalIndex = {}
    for i in range(l):
        with open(os.path.join("../dataset/indexing_dataset/positional_index/positional_index." + str(i) + ".json")) as indFile:
            line = indFile.readline()
            while line:
                ind = json.loads(line)
                for term, term_pos_in_docs in ind.items():
                    if not term in positionalIndex:
                        positionalIndex[term] = {}
                    for _doc, _pos_list in term_pos_in_docs.items():
                        positionalIndex[term][int(_doc)] = _pos_list
                line = indFile.readline()
    return positionalIndex

def loadInvertedIndexMeta(indexFolder):
    term2F = {}
    with open(os.path.join(indexFolder, "meta.json")) as ind_meta:
        line = ind_meta.readline()
        while line:
            meta = json.loads(line)
            for term, filename_lineno in meta.items():
                term2F[term] = filename_lineno
            line = ind_meta.readline()
    return term2F

def loadDocVecIndexMeta(indexFolder):
    DocVecIndex = {}
    with open(os.path.join(indexFolder, "meta.json")) as indfile:
        line = indfile.readline()
        while line:
            ind = json.loads(line)
            for docid, (filename, lineno) in ind.items():
                DocVecIndex[docid] = (filename, lineno)
            line = indfile.readline()
    return DocVecIndex

def LoadIDFData():
    with open(os.path.join("../dataset/indexing_dataset/tf_idf/idf.json"), "r") as f:
        return json.load(f)

class Indexer(object):
    def __init__(self):
        self.meta = None
        return

    def __sizeof__(self):
        return sys.getsizeof(self.meta)

    def __repr__(self):
        return repr(self.meta)

def _line2json(filename, lineno):
    content = linecache.getline(filename, lineno)
    return json.loads(content)


class InvertedIndexData(Indexer):
    def __init__(self):
        super().__init__()
        self.index_folder = '../dataset/indexing_dataset/inverted_index'
        self.meta = loadInvertedIndexMeta(self.index_folder)

    def __getitem__(self, key):
        re = {}
        re[key] = {}
        filename_lineno = self.meta[key]
        res = []
        for i in filename_lineno:
            # with open(i[0], "r") as fp:
            #     line = fp.readlines()
            # content = line[i[1]-1]
            # res.append(json.loads(content))
            res.append(_line2json("../dataset/indexing_dataset/inverted_index/inverted_index." + str(i[0]) + ".json", i[1]))

        for _re in res:
            re[key].update(_re[key])
        return re[key]

    def get_meta(self, key):
        return self.meta[key]

    def __len__(self):
        return len(self.meta)

    def has_key(self, k):
        return (k in self.meta)

    def keys(self):
        return self.meta.keys()


class DocumentVectorIndexData(Indexer):
    def __init__(self):
        super().__init__()
        self.index_folder = '../dataset/indexing_dataset/document_vector_index'
        self.meta = loadDocVecIndexMeta(self.index_folder)

    def __getitem__(self, key):
        (filename, lineno) = self.meta[key]
        content = linecache.getline("../dataset/indexing_dataset/document_vector_index/document_vector_index."+ str(filename) + ".json", lineno)
        return json.loads(content)[key]

    def __len__(self):
        return len(self.meta)

    def has_key(self, k):
        return k in self.meta

    def keys(self):
        return self.meta.keys()

    def get_meta(self, key):
        return self.meta[key]