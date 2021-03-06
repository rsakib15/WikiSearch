import codecs
import json
import os
import time
from collections import defaultdict
import random
from tqdm import tqdm

from indexing.data_loader import LoadIDFData, InvertedIndexData, DocumentVectorIndexData
from indexing.index_main import load_meta
from ranking.cosine_similarity import CosineSearch
from ranking.high_tf_idf import HIGH_TF_IDF
from ranking.tf_idf import TF_IDF
from ranking.proximity import Proximity
from ranking.bag_of_words import BOW
from ranking.jaccard import Jaccard


def create_sample_files():
    parsed_doc_path = '../dataset/extracted_dataset/json'
    title_file = codecs.open("benchmark/sample_title.txt", "w", "utf8")
    content_file = codecs.open("benchmark/sample_text.txt", "w", "utf8")
    count = 0
    while count<10:
        filename = random.choice(os.listdir(parsed_doc_path))

        with codecs.open(os.path.join('../dataset/extracted_dataset/json',filename), 'r', 'utf8') as f:
            data = json.loads(f.read())
            if data['text'] == "":
                continue
            else:
                count += 1
            title_file.write(data['title'] + "\n")
            content = data['text']
            content = content.replace("\n"," ").replace('\r', '')
            content_list = str(content).split(" ")
            content_list_len = len(content_list)
            rn = random.randint(0, content_list_len-10)
            s = content_list[rn-1] + " "

            for i in range(10):
                s += content_list[i] + " "

            s = s.strip()
            print(s)
            content_file.write(s + "\n")
    title_file.close()
    content_file.close()


def get_avg_time(path):
    results = read_file(path)
    avg_time_file = codecs.open("benchmark/avg_time.txt", "w", "utf8")
    score = ["BOW","Jaccard", "CosineSearch","TF_IDF","HIGH_TF_IDF"]
    time_count = defaultdict(lambda: 0)
    num = len(results)
    for result in results:
        result = json.loads(result)
        result = list(result.values())
        for s in score:
            time_count[s] += float(result[0][s]['time'])

    for s in score:
        time_count[s] /= num
        print(s, time_count[s])

    # avg_time_file.write(time_count)
    return time_count


def run_and_write(path, queries):
    print("Meta data loading")
    meta_data = load_meta(os.path.join('../dataset/indexing_dataset/meta.json'))
    print("Meta data loaded")
    from search_engine.search_utils import get_idf

    print("DocumentVectorIndexData data loading")
    document_vector_index_data = DocumentVectorIndexData()
    print("DocumentVectorIndexData data done")
    print("InvertedIndexData data loading")
    inverted_index_meta_data = InvertedIndexData()
    print("InvertedIndexData data done")
    # print("IDF Data generating")
    # get_idf(inverted_index_meta_data)
    # print("IDF Data generated")
    print("IDF Data Loading")
    idf_data = LoadIDFData()
    print("IDF Data Loaded")

    scores = ["BOW", "Jaccard", "TF_IDF", "HIGH_TF_IDF"]
    query_result_file = codecs.open(path, "w", "utf8")

    for query in tqdm(queries):
        res = {}
        res[str(query)] = {}

        for score in scores:

            if score == "BOW":
                searcher = BOW(doc_vec_data = document_vector_index_data, inv_data = inverted_index_meta_data, idf_data = idf_data)
            elif score == "Jaccard":
                searcher = Jaccard(doc_vec_data = document_vector_index_data, inv_data = inverted_index_meta_data, idf_data = idf_data)
            elif score == "CosineSearch":
                searcher = CosineSearch(doc_vec_data = document_vector_index_data, inv_data = inverted_index_meta_data,meta_file= meta_data)
            elif score == "TF_IDF":
                searcher = TF_IDF()
            elif score == "HIGH_TF_IDF":
                searcher = HIGH_TF_IDF()
            else:
                searcher = CosineSearch(doc_vec_data = document_vector_index_data, inv_data = inverted_index_meta_data,meta_file= meta_data)

            begin = time.time()
            result = searcher.search(query)
            end = time.time() - begin

            res[query][score] = {
                'result': result,
                'time': end
            }
        query_result_file.write(json.dumps(res, ensure_ascii=False) + "\n")


def read_file(path):
    with codecs.open(path, "r", "utf8") as f:
        return f.readlines()

def score_main():
    #create_sample_files()
    sample_title = read_file("benchmark/sample_title.txt")
    sample_text = read_file("benchmark/sample_text.txt")
    sample_title = map(lambda s: s.strip(), sample_title)
    sample_text = map(lambda s: s.strip(), sample_text)
    run_and_write("benchmark/result.json", sample_title)
    avg_time = get_avg_time("benchmark/result.json")
    print(avg_time)