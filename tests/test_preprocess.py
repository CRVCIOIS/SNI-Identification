import os
import unittest
from input.preprocess import InputPreprocess
from collections import defaultdict
from smart_open import open
from gensim.corpora import MmCorpus
from gensim.test.utils import datapath
from gensim import corpora
from pprint import pprint

class PreprocessTest(unittest.TestCase):
    def setUp(self):

        #define a sample corpus
        self.corpus = [
            ["This", "is", "a", "sample", "document"],
            ["Another", "sample", "document"],
            ["Yet", "another", "sample", "document"]
        ]
        self.corpus_filename = "test.corpus"

        self.preprocessor = InputPreprocess(self.corpus_filename)



    def test_write_tokenized_corpus_as_vectorized_corpus_to_file(self):

        vectorized_text = [[(0,1), (1,1)]]
        tokenized_text = [["test", "test2"]]

        self.preprocessor.write_tokenized_corpus_as_vectorized_corpus_to_file(tokenized_text, self.corpus_filename)
        self.assertTrue(os.path.exists(f"{self.corpus_filename}.mm"), "File does not exist")


        corpus = MmCorpus(f"{self.corpus_filename}.mm")

        for (vector, corpus_vector) in zip(vectorized_text, corpus):
            self.assertEqual(vector, corpus_vector, "Vectors are not equal")

        #clean up
        os.remove(f"{self.corpus_filename}.mm")
        os.remove(f"{self.corpus_filename}.mm.index")

      

    def test_read_vectorized_corpus_from_file(self):
        vectorized_text = [[(0,1), (1,1)]]
        tokenized_text = [["test", "test2"]]

        self.preprocessor.write_tokenized_corpus_as_vectorized_corpus_to_file(tokenized_text, self.corpus_filename)
        corpus = self.preprocessor.read_vectorized_corpus_from_file(self.corpus_filename)

        for (vector, corpus_vector) in zip(vectorized_text, corpus):
            self.assertEqual(vector, corpus_vector, "Vectors are not equal")

        #clean up
        os.remove(f"{self.corpus_filename}.mm")
        os.remove(f"{self.corpus_filename}.mm.index")
            




    def test_execute(self):
        # Define a sample corpus
        corpus = [
            "Better late than never, but better never late.",
            "<i>Hel 9lo</i> <b>Wo9 rld</b>! Th3     weather_is really g00d today, isn't it?",
            "test test2 test1 test3 test2"
        ]

        # Call the execute method
        result = self.preprocessor.execute(corpus)

        

        # Assert that the result is the preprocessed corpus
        expected_tokenized_corpus = [
            ["better", "late", "better", "late"],
            [],
            ["test", "test", "test", "test", "test"]
        ]
        expected_dictionary_corpus = corpora.Dictionary(expected_tokenized_corpus)

        self.assertEqual(result, (expected_tokenized_corpus, expected_dictionary_corpus))
    
    def test_doc2bow(self):
        # Define a sample corpus
        corpus = [
            ["better", "late", "better", "late"],
            [],
            ["test", "test", "test", "test", "test"]
        ]

        # Call the doc2bow method
        result = self.preprocessor.doc2bow(corpus, corpora.Dictionary(corpus))

        # Assert that the result is the preprocessed corpus
        expected = [
            [(0, 2), (1, 2)], 
            [],
            [(2, 5)]
        ]

        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()


  
