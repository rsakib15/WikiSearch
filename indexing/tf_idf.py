import json
import os
import multiprocessing as mp
import threading

from tqdm import tqdm
from search_engine.search_utils import get_tf_idf_score, get_idf


def genreate_inv_meta():
    with open(os.path.join('../dataset/indexing_dataset/inverted_index/', "meta.json")) as ind_meta:
        line = ind_meta.readline()
        while line:
            meta = json.loads(line)
            for term, filename_lineno in meta.items():
                with open(os.path.join("../dataset/indexing_dataset/inverted_index/meta_data/" + str(term) + ".json"),"w") as f:
                    f.write(str(filename_lineno) + "\n")
            line = ind_meta.readline()



def dump_meta(doc,doc_index,idf,total_documents):
    print("generating...")
    tf_idf_DocVecIndex = {}
    if os.path.exists(os.path.join("../dataset/indexing_dataset/tf_idf/single_doc/" + str(doc) + ".json")):
        return
    tf_idf_DocVecIndex[doc] = {}
    res = {}
    for term in doc_index[doc]:
        tf = doc_index[doc][term] / len(doc_index[doc])
        idf_data = idf[term]
        res[term] = get_tf_idf_score(tf, idf_data, total_documents)


    with open(os.path.join("../dataset/indexing_dataset/tf_idf/single_doc/" + str(doc) + ".json"), "w") as f:
            f.write(json.dumps(res) + "\n")


def threadFunc(doc, doc_index,idf, total_documents):
    tf_idf_DocVecIndex = {}
    tf_idf_DocVecIndex[doc] = {}
    res = {}
    l = len(doc_index[doc])
    for term in doc_index[doc]:
        tf = doc_index[doc][term] / l
        idf_data = idf[term]
        res[term] = get_tf_idf_score(tf, idf_data, total_documents)

    with open(os.path.join("../dataset/indexing_dataset/tf_idf/single_doc/" + str(doc) + ".json"), "w") as f:
        f.write(json.dumps(res) + "\n")



def genreate_tf_idf(doc_data, idfd):
    tf_idf_DocVecIndex = {}
    doc_index = doc_data
    total_documents = len(doc_index)
    print(total_documents)
    idf = idfd

    cpu_num = mp.cpu_count()
    mp_pool = mp.Pool(cpu_num)
    mp_pool.starmap(dump_meta, [(doc, doc_index, idf, total_documents) for doc in doc_index.keys()])
    print(doc_index.keys())



    # for doc in tqdm(doc_index.keys()):
    #     t1 = threading.Thread(target=thread_url, args=(count + 1,))
    #     t2 = threading.Thread(target=thread_url, args=(count + 2,))
    #     t3 = threading.Thread(target=thread_url, args=(count + 3,))
    #     t4 = threading.Thread(target=thread_url, args=(count + 4,))
    #
    #
    #
    #
    #     if os.path.exists(os.path.join("../dataset/indexing_dataset/tf_idf/single_doc/" + str(doc) + ".json")):
    #         continue
    #
    #     tf_idf_DocVecIndex[doc] = {}
    #     res = {}
    #     l = len(doc_index[doc])
    #     for term in doc_index[doc]:
    #         tf = doc_index[doc][term] / l
    #         idf_data = idf[term]
    #         res[term] = get_tf_idf_score(tf, idf_data, total_documents)
    #
    #     with open(os.path.join("../dataset/indexing_dataset/tf_idf/single_doc/" + str(doc) + ".json"), "w") as f:
    #          f.write(json.dumps(res) + "\n")