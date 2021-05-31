import codecs
import json
import logging
import sys
import math
import os
import time

from tqdm import tqdm
import multiprocessing as mp

from indexing.document_vector_index import DocumentVectorIndex
from indexing.index_helper import parseWikiJsons
from indexing.inverted_index import InvertedIndex
from indexing.positional_index import PositionalIndex


def get_directory_flie_list(base_directory):
    directory_list = []
    for directory in os.listdir(base_directory):
        path = os.path.join(base_directory, directory)
        if os.path.isdir(path):
            directory_list += get_directory_flie_list(path)
        else:
            directory_list.append(path)
    return directory_list

def write_file(path, file):
    with codecs.open(path, 'w', 'utf8') as f:
        f.write(file)

def generate_separte_file(wikis, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    meta_data = {}

    for wiki_dir in tqdm(wikis):
        with open(wiki_dir, 'r') as f:
            lines =  f.readlines()
            for j in range(len(lines)):
                line = lines[j]
                line_obj = json.loads(line)
                output_file_name = os.path.join(output_dir, line_obj['id']+".json")
                meta_data[line_obj['id']] = output_file_name
                write_file(output_file_name, json.dumps(line_obj, ensure_ascii=False))

        write_file(os.path.join(output_dir, "meta.json"), json.dumps(meta_data))


def dump_meta(wikiFile, metaFile):
    articles = parseWikiJsons(wikiFile, True)
    with open(metaFile, 'w') as metaF:
        for article in articles:
            metaF.write(json.dumps(article) + '\n')


def load_meta(metaFile):
    articles = dict()
    with open(metaFile) as metaF:
        line = metaF.readline()
        while line:
            _article = json.loads(line)
            articles[str(_article["uid"])] = _article
            if "text" in articles[str(_article["uid"])]:
                del articles[str(_article["uid"])]["text"]
            line = metaF.readline()
    return articles


def dump_meta_data(wikis, filename):
    cpu_num = mp.cpu_count()
    pool = mp.Pool(cpu_num)
    pool.starmap(dump_meta,[(wikis[i], filename + str(i)) for i in range(len(wikis))])
    articles = pool.map(load_meta, [filename + str(i) for i in range(len(wikis))])
    with open(filename, 'w') as metaF:
        for i in range(len(wikis)):
            for uid, article in articles[i].items():
                metaF.write(json.dumps(article) + '\n')
    for i in range(len(wikis)):
        if os.path.exists(filename + str(i)):
            os.remove(filename + str(i))


def index_dataset():
    #get all directory of extracted dataset
    wikis = get_directory_flie_list("dataset/extracted_dataset/text/")

    #for getting all file separetly
    generate_separte_file(wikis, "dataset/extracted_dataset/json/")

    dump_meta_data(wikis, "dataset/indexing_dataset/meta.json")

    #document vector indexing
    print("Document vector indexing starts")
    index_start = time.time()
    dvi = DocumentVectorIndex(wikis=wikis)
    dvi.create_index()
    indexing_time = time.time() - index_start
    print("Document vector indexing time: " + str(indexing_time))

    # # inverted indexing
    # print("Inverted indexing starts")
    # index_start = time.time()
    # inv_index = InvertedIndex(wikis)
    # inv_index.create_index()
    # indexing_time = time.time() - index_start
    # print("Inverted vector indexing time: " + str(indexing_time))
    #
    # #positional indexing
    # print("Positional indexing starts")
    # index_start = time.time()
    # pos_index = PositionalIndex(wikis)
    # pos_index.create_index()
    # indexing_time = time.time() - index_start
    # print("Positional indexing time: " + str(indexing_time))


if __name__ == "__main__":
    index_dataset()