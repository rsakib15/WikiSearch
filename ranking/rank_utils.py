import math
from heapq import heapify, heappush, heappop


def heap(scores, top_k):
    heap = []
    heapify(heap)
    for doc in scores:
        heappush(heap, (-scores[doc], doc))

    top_k_docs = []
    num = min(len(heap), top_k)
    for i in range(num):
        top_k_docs.append(heappop(heap)[1])
    return top_k_docs

def cosine(v1, v2):
    intersection = set(v1.keys()) & set(v2.keys())

    similarity = 0
    for term in intersection:
        similarity += v1[term] * v2[term]
    return similarity

def normalize(vec):
    eucd_len = math.sqrt(sum(map(lambda x: x**2, vec.values())))
    for term in vec:
        vec[term] /= eucd_len
    return vec

def similarity(query, doc):
    query = normalize(query)
    doc = normalize(doc)

    return cosine(query, doc)