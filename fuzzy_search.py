import json
import pickle
import os
import enchant
import re

from tqdm import tqdm
import time
from indexing.index_helper import parseWikiJsons, getTerms
from indexing.index_main import get_directory_file_list
import multiprocessing as mp

def bigram_word(word, bias=None):
    #Add special characters depending on bias
    if bias is None:
        word = '$'+word+'$'
    elif bias == 'left':
        word = '$'+word
    elif bias == 'right':
        word = word+'$'
    #Return bigrams for edited word
    return set([word[i:i+2] for i in range(len(word)-1)])

def biword_phrase(text):
    return set([(text[i]+' '+text[i+1]) for i in range(len(text)-1)])

class FuzzySearch(object):

    def __init__(self, wikis=None):
        self.dictionary_folder = 'dataset/dictionary_dataset/'
        if not wikis is None:
            self.wikis = wikis

    def generate_frequencies_helper(self, article, m):
        frequencies_path = os.path.join(self.dictionary_folder, 'frequencies.'+str(m)+'.pickle')
        biword_frequencies_path = os.path.join(self.dictionary_folder, 'biword_frequencies.'+str(m)+'.pickle')
        wiki_data = parseWikiJsons(article)
        frequencies = {}
        biword_frequencies = {}
        for article in tqdm(wiki_data):
            terms = getTerms(article['text'],remove_stopwords=False) + getTerms(article['title'],remove_stopwords=False)
            biwords = biword_phrase(terms)
            for word in terms:
                if not word in frequencies:
                    frequencies[word] = 1
                else:
                    frequencies[word] += 1
            for biword in biwords:
                if not biword in biword_frequencies:
                    biword_frequencies[biword] = 1
                else:
                    biword_frequencies[biword] += 1
        with open(frequencies_path, 'wb') as file:
            pickle.dump(frequencies,file)
        file.close()
        with open(biword_frequencies_path,'wb') as file:
            pickle.dump(biword_frequencies,file)
        file.close()

    def __generate_frequencies(self):
        assert(self.wikis is not None)
        cpu_num = mp.cpu_count()
        mp_pool = mp.Pool(cpu_num)
        mp_pool.starmap(self.generate_frequencies_helper, [(self.wikis[i],i)for i in range(len(self.wikis))])
        frequencies = {}
        biword_frequencies = {}
        for i in tqdm(range(len(self.wikis))):
            with open(os.path.join(self.dictionary_folder,'frequencies.'+str(i)+'.pickle'),'rb') as file:
                tmp_freq = pickle.load(file)
                for word in tmp_freq:
                    if not word in frequencies:
                        frequencies[word] = tmp_freq[word]
                    else:
                        frequencies[word] += tmp_freq[word]
            file.close()
            with open(os.path.join(self.dictionary_folder,'biword_frequencies.'+str(i)+'.pickle'),'rb') as file:
                tmp_freq = pickle.load(file)
                for biword in tmp_freq:
                    if not biword in biword_frequencies:
                        biword_frequencies[biword] = tmp_freq[biword]
                    else:
                        biword_frequencies[biword] += biword_frequencies[biword]
            file.close()
        with open(os.path.join(self.dictionary_folder,'frequencies.pickle'), 'wb') as file:
            pickle.dump(frequencies,file)
        file.close()
        with open(os.path.join(self.dictionary_folder,'biword_frequencies.pickle'),'wb') as file:
            pickle.dump(frequencies,file)
        file.close()
        self.frequencies = frequencies
        self.biword_frequencies = frequencies
    
    def __generate_dictionary(self):
        assert(self.frequencies is not None)
        dictionary = {}
        counter = 0
        for word in self.frequencies:
            dictionary[counter] = word
            counter += 1
        with open(os.path.join(self.dictionary_folder,'dictionary.pickle'),'wb') as file:
            pickle.dump(dictionary,file)
        file.close()
        self.dictionary = dictionary

    def __generate_bigrams(self):
        assert(self.dictionary is not None)
        bigram_index = {}
        bigram_inverted = {}
        for index in self.dictionary:
            bigrams = bigram_word(self.dictionary[index])
            bigram_index[index] = bigrams
            for bigram in bigrams:
                if not bigram in bigram_inverted:
                    bigram_inverted[bigram] = set([index])
                else:
                    bigram_inverted[bigram].add(index)
        with open(os.path.join(self.dictionary_folder,'bigram_inverted.pickle'),'wb') as file:
            pickle.dump(bigram_inverted,file)
        file.close()
        with open(os.path.join(self.dictionary_folder,'bigram_index.pickle'),'wb') as file:
            pickle.dump(bigram_index,file)
        file.close()
        self.bigram_index = bigram_index
        self.bigram_inverted = bigram_inverted

    def create(self):
        assert(self.wikis is not None)
        print("Generating Frequency List")
        start = time.time()
        self.__generate_frequencies()
        finish = time.time()
        print("Generated Frequency List in {} seconds".format(str(finish-start)))
        print("Generating Dictionary")
        start = time.time()
        self.__generate_dictionary()
        finish = time.time()
        print("Generated Dictionary in {} seconds".format(str(finish-start)))
        print("Generating Bigram Indices")
        start = time.time()
        self.__generate_bigrams()
        finish = time.time()
        print("Generated Bigram Indices in {} seconds".format(str(finish-start)))

    def exists(self):
        return os.path.exists(os.path.join(self.dictionary_folder,'bigram_index.pickle')) and \
                os.path.exists(os.path.join(self.dictionary_folder,'dictionary.pickle')) and \
                os.path.exists(os.path.join(self.dictionary_folder,'frequencies.pickle')) and \
                os.path.exists(os.path.join(self.dictionary_folder,'bigram_inverted.pickle')) and \
                os.path.exists(os.path.join(self.dictionary_folder,'biword_frequencies.pickle'))

    def load(self):
        assert(os.path.exists(os.path.join(self.dictionary_folder,'frequencies.pickle')))
        assert(os.path.exists(os.path.join(self.dictionary_folder,'dictionary.pickle')))
        assert(os.path.exists(os.path.join(self.dictionary_folder,'bigram_index.pickle')))
        assert(os.path.exists(os.path.join(self.dictionary_folder,'bigram_inverted.pickle')))
        assert(os.path.exists(os.path.join(self.dictionary_folder,'biword_frequencies.pickle')))
        print("Loading Frequency List")
        start = time.time()
        with open(os.path.join(self.dictionary_folder,'frequencies.pickle'),'rb') as file:
            self.frequencies = pickle.load(file)
        file.close()
        with open(os.path.join(self.dictionary_folder,'biword_frequencies.pickle'),'rb') as file:
            self.biword_frequencies = pickle.load(file)
        file.close()
        finish = time.time()
        print("Loaded Frequency List in {} seconds".format(finish-start))
        print("Loading Dictionary")
        start = time.time()
        with open(os.path.join(self.dictionary_folder,'dictionary.pickle'),'rb') as file:
            self.dictionary = pickle.load(file)
        file.close()
        finish = time.time()
        print("Loaded Dictionary in {} seconds".format(finish-start))
        print("Loading Bigram Indices")
        start = time.time()
        with open(os.path.join(self.dictionary_folder,'bigram_index.pickle'),'rb') as file:
            self.bigram_index = pickle.load(file)
        file.close()
        with open(os.path.join(self.dictionary_folder,'bigram_inverted.pickle'),'rb') as file:
            self.bigram_inverted = pickle.load(file)
        file.close()
        finish = time.time()
        print("Loaded Bigram Indices in {} seconds".format(str(finish-start)))
    
    def delete(self):
        for f in os.listdir(self.dictionary_folder):
            os.remove(os.path.join(self.dictionary_folder, f))

    def wildcard_lookup(self, term, n=0):
        term = term.lower()
        split = term.split('*')
        #Generate bigram list
        bigrams = bigram_word(split[0],'left') | bigram_word(split[-1],'right')
        middle = split[1:-1]
        for part in middle:
            bigrams = bigrams | bigram_word(part,'middle')
        #Generate potentials list
        potentials = set(self.dictionary.keys())
        for bigram in bigrams:
            if bigram in self.bigram_inverted:
                potentials = potentials & self.bigram_inverted[bigram]
            else:
                potentials = set()
                break
        #Filter potentials
        results = []
        for potential in potentials:
            word = self.dictionary[potential]
            if not word[:len(split[0])] == split[0]:
                continue
            if not len(split[-1]) == 0 and not word[-len(split[-1]):] == split[-1]:
                continue
            if len(split[-1]) == 0:
                word = word[len(split[0]):]
            else:
                word = word[len(split[0]):-len(split[-1])]
            index = -1
            for part in middle:
                if not part == '':
                    index = word.find(part)
                    if index == -1:
                        break
                    word = word[index+len(part):]
            if len(middle)==0 or index > -1:
                results.append((self.dictionary[potential],self.frequencies[self.dictionary[potential]]))
        results.sort(key=lambda x:x[1], reverse = True)
        if n > 0:
            results = results[:n]
        return results
        
    def spell_check(self, term, jaccard_cutoff, edit_cutoff, n):
        term = term.lower()
        #If word in dictionary
        if term in self.dictionary.values():
            return [(term,0)]
        #Generate bigrams
        bigrams = bigram_word(term)
        potentials = {}
        # Generate potentials
        for bigram in bigrams:
            words = self.bigram_inverted[bigram]
            for word in words:
                if not word in potentials:
                    potentials[word] = 1
                else:
                    potentials[word] += 1
        weighted_distances = []
        #Filter potentials
        for potential in potentials:
            #Calculate Jaccard
            jaccard = potentials[potential]/len(list(bigrams|self.bigram_index[potential]))
            if jaccard < jaccard_cutoff:
                continue
            #Calculate edit distance
            distance = enchant.utils.levenshtein(term,self.dictionary[potential])
            if distance >= edit_cutoff:
                continue
            #Weight distances
            weighted_distances.append((self.dictionary[potential],distance/self.frequencies[self.dictionary[potential]]))
        if len(weighted_distances)==0:
            return [(term,0)]
        #Sort weighted distances
        weighted_distances.sort(key=lambda x:x[1])
        return weighted_distances[:n]

    def process_fuzzy(self, query, query_n = 5, wildcard_n = 10, spellcheck_n = 10):
        query = query.lower()
        query = re.sub(r'[^a-z0-9 *]', ' ', query)
        terms = query.split(' ')
        fuzzy_lists = []
        for term in terms:
            if '*' in term:
                fuzzy_lists.append(self.wildcard_lookup(term,wildcard_n))
            else:
                fuzzy_lists.append(self.spell_check(term,.25,2,spellcheck_n))
        queries = ['']
        for fuzzy_list in fuzzy_lists:
            partial_queries = queries
            queries = []
            if len(fuzzy_list)>0:
                for fuzzy_term in fuzzy_list:
                    for partial_query in partial_queries:
                        if partial_query == '':
                            queries.append(fuzzy_term[0])
                        else:
                            queries.append(partial_query+ ' ' + fuzzy_term[0])
            else:
                queries = partial_queries
        ranked = []
        for q in queries:
            counter = 0
            biwords = biword_phrase(q)
            for biword in biwords:
                if biword in self.biword_frequencies:
                    counter += self.biword_frequencies[biword]
            ranked.append((q,counter))
        ranked.sort(key=lambda x:x[1])
        result = []
        for i in range(query_n):
            result.append(ranked[i][0])
        return result

        

if __name__ == '__main__':
    wikis = get_directory_file_list("dataset/extracted_dataset/text/")
    fuzzy = FuzzySearch(wikis)
    if not fuzzy.exists():
        print("Generating Fuzzy Search")
        start = time.time()
        fuzzy.create()
        finish = time.time()
        print("Generated Fuzzy Search in {} seconds".format(str(finish-start)))
    else:
        print("Loading Fuzzy Search")
        start = time.time()
        fuzzy.load()
        finish = time.time()
        print("Loaded Fuzzy Search in {} seconds".format(str(finish-start)))
    print(fuzzy.process_fuzzy('Alex* the graet'))
    