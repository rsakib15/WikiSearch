import json
import pickle
import heapq as hq
import logging
import pickle
import os
from indexing.data_loader import InvertedIndexData


class node:
    def __init__(self):
        self.child = {}
        self.top_k = []


class Trie:
    def __init__(self, top_k):
        self.top_k = top_k
        self.root = node()
        return

    def add(self, sentence, weight):
        # char = sentence[0]
        cur = self.root
        for char in sentence:
            char = str(char)
            if char in cur.child:
                if len(cur.child[char].top_k) < self.top_k:
                    hq.heappush(cur.child[char].top_k, (weight, sentence))
                else:
                    smallest = hq.nsmallest(1, cur.child[char].top_k)
                    if weight > smallest[0][0]:
                        hq.heapreplace(cur.child[char].top_k,
                                       (weight, sentence))
            else:
                cur.child[char] = node()
                cur.child[char].top_k = [(weight, sentence)]
                hq.heapify(cur.child[char].top_k)
            cur = cur.child[char]
        return

    def match(self, partial_sentence, dump=False):
        cur = self.root
        anchor = 0
        if dump:
            logging.info(partial_sentence)
        for char in partial_sentence:
            anchor += 1
            char = str(char)
            if char in cur.child:
                cur = cur.child[char]
            else:
                return anchor, []
        _re = cur.top_k
        _re.sort(key=lambda x: x[0])
        re = [_re[len(_re) - r - 1][1] for r in range(len(_re))]
        return anchor, re

    def load(self, dump_file):
        dump_f = open(dump_file, 'rb')
        obj = pickle.load(dump_f)
        ind = [0]
        self.traversal(obj, self.root, True, ind)
        dump_f.close()

    def dump(self, dump_file):
        obj = []
        self.traversal(obj, self.root)
        dump_f = open(dump_file, 'wb')
        pickle.dump(obj, dump_f)
        dump_f.close()

    def traversal(self, obj, cur, is_load=False, ind=[0]):
        if is_load:
            if ind[0] >= len(obj):
                raise IndexError
            childs = obj[ind[0]]
            cur.top_k = obj[ind[0] + 1]
            for ch in childs:
                cur.child[ch] = node()
            ind[0] += 2
            for ch in childs:
                self.traversal(obj, cur.child[ch], True, ind)
            return
        childs = list(cur.child.keys())
        obj.append(childs)
        obj.append(cur.top_k)
        for ch in childs:
            self.traversal(obj, cur.child[ch])

def rotate(str, n):
    return str[n:] + str[:n]

class QuerySuggestion:
    def __init__(self, top_k):
        self.top_k = top_k
        self.trie = Trie(top_k)
        self.index_folder = 'dataset'
        return

    def get_permuterm_index(self):
        term2F = {}
        with open(os.path.join(self.index_folder, "fuzzy_dataset.json")) as ind_meta:
            line = ind_meta.readline()
            while line:
                meta = json.loads(line)
                for term, filename_lineno in meta.items():
                    term2F[term] = filename_lineno
                line = ind_meta.readline()
        return term2F

    def generay_fuzzy_permuterm_index(self):
        inv = InvertedIndexData()
        keys =inv.keys()

        with open('../dataset/fuzzy_dataset.json','w') as index_meta:
            for key in sorted(keys):
                dkey = key + "$"
                perm = []
                for i in range(len(dkey), 0, -1):
                    out = rotate(dkey, i)
                    perm.append(out)
                index_meta.write(json.dumps({key: perm}) + "\n")

    def prefix_match(self, term, prefix):
        term_list = []
        print(term.keys())

        for tk in term.keys():
            if tk.startswith(prefix):
                term_list.append(term[tk])
        return term_list

    def suggest(self,partial_query):
        print("suggest")
        print(partial_query)
        assert len(partial_query) > 0, "empty query string"

        permuterm = self.get_permuterm_index()
        term_list = self.prefix_match(permuterm, partial_query)

        print(term_list)

        docID = []
        # for term in term_list:
        #     print(term)
