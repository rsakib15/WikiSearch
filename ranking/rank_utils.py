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