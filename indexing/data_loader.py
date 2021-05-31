import json
import linecache
import os
import pickle
import sys
import zlib

from tqdm import tqdm


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
        self.index_folder = 'dataset/indexing_dataset/inverted_index'
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
            res.append(_line2json(i[0], i[1]))

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
        self.index_folder = 'dataset/indexing_dataset/document_vector_index'
        self.meta = loadDocVecIndexMeta(self.index_folder)

    def __getitem__(self, key):
        (filename, lineno) = self.meta[key]
        content = linecache.getline(filename, lineno)
        return json.loads(content)[key]

    def __len__(self):
        return len(self.meta)

    def has_key(self, k):
        return k in self.meta

    def keys(self):
        return self.meta.keys()

    def get_meta(self, key):
        return self.meta[key]