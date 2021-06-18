import json
import pickle
import os
import sys
import time
from tqdm import tqdm
from indexing.index_helper import parseWikiJsons, getTerms
import multiprocessing as mp

class InvertedIndex(object):
    def __init__(self, wikis,full=False):
        self.index_folder = '../dataset/indexing_dataset/inverted_index'
        self.wikis = wikis
        #Use full index or just use mappings
        self.full = full

    def create_inverted_index_helper(self, article, n):
        '''Create inverted index for individual wiki partition
        params:
        article: wiki partition
        n: identifier for wiki partition output
        '''
        index_file_dir = os.path.join(self.index_folder, "inverted_index_tmp." + str(n) + ".pickle")
        wiki_data = parseWikiJsons(article)
        inverted_index = dict()
        #Iterate through articles in partition and generate inverted index
        for article in tqdm(wiki_data):
            doc_id = article["uid"]
            text = getTerms(article["text"])
            title = getTerms(article["title"])
            for word in text:
                if not word in inverted_index:
                    inverted_index[word] = {doc_id: 1}
                else:
                    if not doc_id in inverted_index[word]:
                        inverted_index[word][doc_id] = 1
                    else:
                        inverted_index[word][doc_id] += 1
        with open(index_file_dir,'wb') as file:
            pickle.dump(inverted_index,file)
        file.close()

    def create_inverted_index(self):
        '''Create inverted index for dataset'''
        assert(self.wikis is not None)
        #Generate inverted indices for each wiki partition
        cpu_num = mp.cpu_count()
        mp_pool = mp.Pool(cpu_num)
        mp_pool.starmap(self.create_inverted_index_helper,[(self.wikis[i],i)for i in range(len(self.wikis))])
        inverted_index = {}
        #Combine inverted indices into one massive index
        for i in tqdm(range(len(self.wikis))):
            if os.path.exists(os.path.join(self.index_folder,'inverted_index_tmp.'+str(i)+'.pickle')):
                continue

            with open(os.path.join(self.index_folder,'inverted_index_tmp.'+str(i)+'.pickle'), 'rb') as file:
                tmp_inverted = pickle.load(file)
                for word in tmp_inverted:
                    if not word in inverted_index:
                        inverted_index[word] = tmp_inverted[word]
                    else:
                        inverted_index[word].update(tmp_inverted[word])
            file.close()
        #Output large-scale index
        with open(os.path.join(self.index_folder,'inverted_index.pickle'),'wb') as file:
            pickle.dump(inverted_index,file)
        file.close()
        #Partition larger index into smaller files and map each word to one file
        mappings = {}
        iters = len(inverted_index.items())//5000
        for i in tqdm(range(iters)):
            d = dict(list(inverted_index.items())[i:iters*5000:iters])
            for k in d:
                mappings[k] = i
            with open(os.path.join(self.index_folder,'inverted_index_part_{}.pickle'.format(i)),'wb') as file:
                pickle.dump(d,file)
            file.close()
        if len(inverted_index.items())%5000 > 0:
            d = dict(list(inverted_index.items())[-(len(inverted_index.items())%5000):])
            for k in d:
                mappings[k] = iters
            with open(os.path.join(self.index_folder,'inverted_index_part_{}.pickle'.format(iters)),'wb') as file:
                pickle.dump(d,file)
            file.close()
        #Output mappings
        with open(os.path.join(self.index_folder,'inverted_index_mappings.pickle'),'wb') as file:
            pickle.dump(mappings,file)
        file.close()
        if self.full:
            self.inverted_index=inverted_index
        else:
            self.mappings = mappings
    
    def find(self, term):
        '''Use inverted index to lookup term
        params:
        term: term for lookup
        return:
        dict: with docs as keys and frequencies w/in docs as values
        '''
        #If using big index
        if self.full:
            return self.inverted_index[term]
        #Otherwise use mappings
        with open(os.path.join(self.index_folder,'inverted_index_part_{}.pickle'.format(self.mappings[term])),'rb') as file:
            inverted_part = pickle.load(file)
        file.close()
        return inverted_part[term]

    def find_doc_set(self,term):
        '''Return set of docs related to a given term
        params:
        term: term for lookup
        return:
        set: set of docs
        '''
        d = self.find(term)
        result = set()
        for k in d:
            result.add(k)
        return result

    def exists(self):
        '''Check if needed assets exist for inverted index lookup
        returns:
        boolean
        '''
        return os.path.exists(os.path.join(self.index_folder,'inverted_index.pickle')) and \
                os.path.exists(os.path.join(self.index_folder,'inverted_index_mappings.pickle'))

    def load_inverted_index(self):
        '''Load inverted index from assets'''
        assert(self.exists())
        #If using big index
        if self.full:
            with open(os.path.join(self.index_folder,'inverted_index.pickle'),'rb') as file:
                self.inverted_index = pickle.load(file)
            file.close()
        #Otherwise use mappings
        else:
            with open(os.path.join(self.index_folder,'inverted_index_mappings.pickle'),'rb') as file:
                self.mappings = pickle.load(file)

    def delete_inverted_index(self):
        '''Delete all needed assets for inverted index lookup'''
        for f in os.listdir(self.index_folder):
            os.remove(os.path.join(self.index_folder, f))

if __name__ == '__main__':
    pass
    # wikis = get_directory_file_list("../dataset/extracted_dataset/text/")
    # inverted = InvertedIndex(wikis,False)
    # if not inverted.exists():
    #     print("Generating Inverted Index")
    #     start = time.time()
    #     inverted.create_inverted_index()
    #     finish = time.time()
    #     print("Generated Inverted Index in {} seconds".format(str(finish-start)))
    # else:
    #     print("Loading Inverted Index Search")
    #     start = time.time()
    #     inverted.load_inverted_index()
    #     finish = time.time()
    #     print("Loaded Inverted Index in {} seconds".format(str(finish-start)))
    #
    # print(inverted.find('alexander'))
