import codecs
import json
import logging
import sys
import math
import os
import time

from tqdm import tqdm

from document_vector_index import DocumentVectorIndex
from inverted_index import InvertedIndex
from positional_index import PositionalIndex


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

        write_file(os.path.join(output_dir, "meta.json"), json.dumps(meta_data, ensure_ascii=False))


def main():
    #get all directory of extracted dataset
    wikis = get_directory_flie_list("../dataset/extracted_dataset/text/")

    #for getting all file separetly
    generate_separte_file(wikis, "../dataset/extracted_dataset/json/")

    #document vector indexing
    index_start = time.time()
    dvi = DocumentVectorIndex(wikis=wikis)
    dvi.create_index()
    indexing_time = time.time() - index_start
    logging.info("Document vector indexing time: " + str(indexing_time))
    print("Document vector indexing time: " + str(indexing_time))

    # document vector indexing
    index_start = time.time()
    inv_index = InvertedIndex(wikis)
    inv_index.create_index()
    indexing_time = time.time() - index_start
    logging.info("Inverted vector indexing time: " + str(indexing_time))
    print("Inverted vector indexing time: " + str(indexing_time))

    #positional indexing
    index_start = time.time()
    pos_index = PositionalIndex(wikis)
    pos_index.create_index()
    indexing_time = time.time() - index_start
    logging.info("Positional indexing time: " + str(indexing_time))
    print("Positional indexing time: " + str(indexing_time))


if __name__ == "__main__":
    main()