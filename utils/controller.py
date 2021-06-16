import codecs
import json
import os
import time

docs_path = "../data/parsed/docs"

def read_file(path):
    with codecs.open(path, 'r', 'utf8') as f:
        return json.loads(f.read())

meta_data = read_file(os.path.join(docs_path, "meta.json"))

def getPage(docId):
    if docId not in meta_data:
        return None
    file_path = meta_data[docId]
    doc = read_file(file_path)
    return doc

def generate_abstract(docId, words):
    doc = getPage(docId)
    text = doc['text'][len(doc['title']):]
    begin = 0
    abstract_len = 50
    max_point = 0
    for i in range(len(text)):
        point = 0
        for word in words:
            if word in text[i:i + abstract_len]:
                point += 1

        if max_point < point:
            max_point = point
            begin = i
    abstract = text[begin:begin + abstract_len]
    match_word = [word for word in words if word in abstract or word in doc['title']]
    return {
        'title': doc['title'],
        'abstract': abstract,
        'words': match_word,
        'url': doc['url'],
        'id': doc['id']
    }

def search(searchParams):
    query = searchParams['q']
    print(query)
    print(searchParams['m'])
    begin_time = time.time()

    end_time = time.time()
    res = [generate_abstract(doc, words) for doc in result_list if doc in meta_data]
    return {
        'result': res,
        'time': end_time - begin_time
    }