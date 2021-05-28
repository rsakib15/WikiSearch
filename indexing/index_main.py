import json
import logging
import sys
import math
import os
import time
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


def main():

    wikis = get_directory_flie_list("../dataset/extracted_dataset/text/")
    index_start = time.time()
    dvi = DocumentVectorIndex(wikis=wikis)
    dvi.create_index()
    indexing_time = time.time() - index_start
    logging.info("Document vector indexing time: " + str(indexing_time))
    print("Document vector indexing time: " + str(indexing_time))

    index_start = time.time()
    inv_index = InvertedIndex(wikis)
    inv_index.create_index()
    indexing_time = time.time() - index_start
    logging.info("Inverted vector indexing time: " + str(indexing_time))
    print("Inverted vector indexing time: " + str(indexing_time))

    index_start = time.time()
    pos_index = PositionalIndex(wikis)
    pos_index.create_index()
    indexing_time = time.time() - index_start
    logging.info("Positional indexing time: " + str(indexing_time))
    print("Positional indexing time: " + str(indexing_time))


if __name__ == "__main__":
    main()