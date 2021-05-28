import json
import multiprocessing as mp
import os
import shutil
import linecache

import pickle
import zlib

from tqdm import tqdm
import jieba

from index_main import parseWikiJsons
from indexer import Indexer

def text_segmentation(text):
    text = jieba.cut(text)
    return text

def saveInvertedIndexMeta(term2F, indexFolder):
    with open(os.path.join(indexFolder, "inverted_index_meta.json"),'w') as ind_meta:
        for term, filename_lineno in term2F.items():
            ind_meta.write(json.dumps({term: filename_lineno}) + "\n")


def loadInvertedIndexMeta(indexFolder):
    term2F = {}
    with open(os.path.join(indexFolder,"inverted_index_meta.json")) as ind_meta:
        line = ind_meta.readline()
        while line:
            meta = json.loads(line)
            for term, filename_lineno in meta.items():
                term2F[term] = filename_lineno
            line = ind_meta.readline()
    return term2F


def BuildInvertedIndex(article_file, indexFolder):
    """build inverted index, see slide Lect-2-p19 (but a bit different, see the following example)
    Args:
        articles (list(json)): in memory articles
        indexFile (str): in disk index file
    Examples:
        each line of the inverted index file is a dumped json objects.
        {term: {DocID_0: freq_0, DocID_1: freq_1, ... DocID_n: freq_n}}
    """
    articles = parseWikiJsons(article_file)
    invertedIndex = dict()
    for article in articles:
        docID = article["uid"]
        text = text_segmentation(article["text"])
        for word in text:
            if not word in invertedIndex:
                invertedIndex[word] = {docID: 1}  # set([docID])
            else:
                if not docID in invertedIndex[word]:
                    invertedIndex[word][docID] = 1  # .add(docID)
                else:
                    invertedIndex[word][docID] += 1
    term2F = {}
    # output to indexFile
    with open(os.path.join(indexFolder, "inverted_index.json"), "w") as indfile:
        lineno = 1
        for term, docList in invertedIndex.items():
            term2F[term] = (os.path.join(indexFolder,"inverted_index.json"), lineno)
            indfile.write(json.dumps({term: docList}) + "\n")
            lineno += 1
    saveInvertedIndexMeta(term2F, indexFolder)
    return


def _build_inv_ind(indFol):
    return InvertedIndexer(indFol, thread_num=-1)


def parallelBuildInvertedIndex(article_file_list, indexFolder):
    cpu_num = mp.cpu_count()
    pool = mp.Pool(cpu_num)
    # article_list = pool.map(parseWikiJsons, article_file_list)

    for i in range(len(article_file_list)):
        indFolder = os.path.join(indexFolder, str(i))
        if not os.path.exists(indFolder):
            os.mkdir(indFolder)

    pool.starmap(BuildInvertedIndex,
                 [(article_file_list[i], os.path.join(indexFolder, str(i)))
                  for i in range(len(article_file_list))])

    inverted_index_list = pool.map(_build_inv_ind, [
        os.path.join(indexFolder, str(i))
        for i in range(len(article_file_list))
    ])

    merge_inverted_index(inverted_index_list, indexFolder)

    for i in range(len(article_file_list)):
        meta_file = os.path.join(os.path.join(indexFolder, str(i)),
                                 "inverted_index_meta.json")
        if os.path.exists(meta_file):
            os.remove(meta_file)
            # shutil.rmtree(os.path.join(indexFolder, str(i)))
    return


def LoadMultiInvertedIndex(indexFiles, proc_num):
    pool = mp.Pool(proc_num)
    invertedIndices = pool.map(LoadInvertedIndex, indexFiles)
    return invertedIndices


def LoadInvertedIndex(indexFile):
    invertedIndex = {}
    with open(indexFile) as indfile:
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


def merge_inverted_index(inverted_index_list, indexFolder):
    cpu_num = mp.cpu_count()

    terms = []
    for ind in inverted_index_list:
        terms += list(ind.keys())
    terms = list(set(terms))

    term2F = {}
    for i in range(len(terms)):
        term2F[terms[i]] = []
        for ind in inverted_index_list:
            if not ind.has_key(terms[i]):
                continue
            term2F[terms[i]].append(ind.get_meta(terms[i]))
    saveInvertedIndexMeta(term2F, indexFolder)

    return


def _line2json(filename, lineno):
    content = linecache.getline(filename, lineno)
    linecache.clearcache()
    return json.loads(content)


class InvertedIndexer(Indexer):
    def __init__(self, IndexFolder, in_memory=False, thread_num=0):
        super().__init__(IndexFolder, in_memory)
        self.meta = loadInvertedIndexMeta(IndexFolder )
        if self.in_memory:
            term_list = list(self.meta.keys())
            for id in tqdm(range(len(term_list))):
                term = term_list[id]
                self.cache[term] = None
                temp = {}
                for (filename, lineno) in self.meta[term]:
                    content = linecache.getline(filename, lineno)
                    temp.update(json.loads(content)[term])
                self.cache[term] = zlib.compress(pickle.dumps(temp))
            linecache.clearcache()
        if thread_num < 0:
            self.thread_num = thread_num
            return
        if thread_num > 0:
            self.thread_num = thread_num
        else:
            self.thread_num = mp.cpu_count()
        self.pool = mp.Pool(self.thread_num)

    def __getitem__(self, key):
        if self.in_memory:
            return pickle.loads(zlib.decompress(self.cache[key]))
        re = {}
        re[key] = {}
        filename_lineno = self.meta[key]

        if self.thread_num >=0:
            res = self.pool.starmap(_line2json,[(i[0], i[1]) for i in filename_lineno])
        else:
            res = []
            for i in filename_lineno:
                res.append(_line2json(i[0], i[1]))

        for _re in res:
            re[key].update(_re[key])

        return re[key]
        # return self.__dict__[key]

    def get_meta(self, key):
        return self.meta[key]

    def __len__(self):
        return len(self.meta)
        # return len(self.__dict__)

    def has_key(self, k):
        return (k in self.meta)
        # return k in self.__dict__

    def keys(self):
        return self.meta.keys()
        # return self.__dict__.keys()