from collections import defaultdict
from pprint import pprint
from gensim.parsing.preprocessing import remove_stopwords, preprocess_documents
from gensim import corpora
from gensim.corpora import MmCorpus
from gensim.test.utils import datapath



class InputPreprocess:
    def __init__(self, corpus_filename="corpus") -> None:
        #write corpus to file
        self.corpus_filename = corpus_filename
        #self.write_corpus_to_file(corpus, self.corpus_filename)



   
    def write_tokenized_corpus_as_vectorized_corpus_to_file(self, corpus: list[list[tuple[int, float]]], corpus_filename="") -> None:
        """
        Write the tokenized corpus to a file.

        Args:
            corpus (list[list[str]]): A list of list of strings that represent a tokenized corpus.
        """
        filename = self.corpus_filename
        if corpus_filename != "":
            filename = corpus_filename
        corpus = self.doc2bow(corpus, corpora.Dictionary(corpus))
        MmCorpus.serialize(f'{filename}.mm', corpus)
        
        

    def read_vectorized_corpus_from_file(self, filename=""):
        """
        Read the corpus from a file.

        Returns:
            corpus: Returns a list of vectors, each vector represents a line in the corpus
        """
        if filename == "":
            filename = self.corpus_filename


        corpus = MmCorpus(f'{self.corpus_filename}.mm')

        return corpus
       
    


    def execute(self, corpus: list[str]):
        """
        Preprocesses the given corpus by removing stop words, preprocessing documents,
        removing words that appear only once.

        Args:
            corpus (list): The input corpus to be preprocessed.

        Returns:
            tuple: A tuple containing the preprocessed tokenized corpus and the dictionary corpus.
        """
      

        #preprocess documents
        corpus = preprocess_documents(corpus)


        #remove words that only appear once
        frequency = defaultdict(int)
        for doc in corpus:
            for token in doc:
                frequency[token] += 1

        tokenized_corpus =[
            [token for token in doc if frequency[token] > 1]
            for doc in corpus
        ]


        dictionary_corpus = corpora.Dictionary(tokenized_corpus)
 

        return (tokenized_corpus, dictionary_corpus)
    

    def doc2bow(self, tokenized_corpus: list[list[str]], dictionary_corpus: corpora.Dictionary):
        """
        Returns a list of vectors, each vector represents a line in the corpus
        """
        return [dictionary_corpus.doc2bow(token) for token in tokenized_corpus]

    
    