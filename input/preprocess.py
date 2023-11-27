from collections import defaultdict
from pprint import pprint
from gensim.parsing.preprocessing import remove_stopwords, preprocess_string
from gensim import corpora
from gensim.corpora import MmCorpus
from gensim.test.utils import datapath



class InputPreprocess:
    """
    This class is deprecated. Please use the new Preprocessor class instead.
    """

    def __init__(self, corpus_filename="corpus") -> None:
        #write corpus to file
        self.corpus_filename = corpus_filename
        #self.write_corpus_to_file(corpus, self.corpus_filename)

    def write_tokenized_corpus_as_vectorized_corpus_to_file(self, corpus: list[list[tuple[int, float]]], corpus_filename="") -> None:
        """
        Write the tokenized corpus to a file.

        Args:
            corpus (list[list[str]]): A list of list of strings that represent a tokenized corpus.
            corpus_filename (str): The filename to save the vectorized corpus. If not provided, the default filename will be used.
        """
        filename = self.corpus_filename
        if corpus_filename != "":
            filename = corpus_filename
        corpus = self.doc2bow(corpus, corpora.Dictionary(corpus))
        MmCorpus.serialize(f'{filename}.mm', corpus)

    def read_vectorized_corpus_from_file(self, filename=""):
        """
        Read the corpus from a file.

        Args:
            filename (str): The filename of the vectorized corpus. If not provided, the default filename will be used.

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
        corpus = preprocess_string(corpus)
        return corpus

    def doc2bow(self, tokenized_corpus: list[list[str]], dictionary_corpus: corpora.Dictionary) -> list[list[tuple[int, float]]]:
        """
        Returns a list of vectors, each vector represents a line in the corpus

        Args:
            tokenized_corpus (list[list[str]]): A list of list of strings that represent a tokenized corpus.
            dictionary_corpus (corpora.Dictionary): The dictionary corpus.

        Returns:
            list[list[tuple[int, float]]]: A list of vectors, each vector represents a line in the corpus.
        """
        return [dictionary_corpus.doc2bow(token) for token in tokenized_corpus]


    
    