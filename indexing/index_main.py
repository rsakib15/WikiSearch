import json
import sys
import math
import os
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
    # dvi = DocumentVectorIndex(wikis=wikis)
    # dvi.create_index()

    # invi = InvertedIndex(wikis)
    # invi.create_index()


    invi = PositionalIndex(wikis)
    invi.create_index()


if __name__ == "__main__":
    main()