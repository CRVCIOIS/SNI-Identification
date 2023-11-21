from collections import defaultdict
from gensim.parsing.preprocessing import remove_stopwords, preprocess_documents

class InputPreprocess:
    def __init__(self, corpus: list[str], corpus_filename="corpus.txt") -> None:
        #write corpus to file
        self.corpus_filename = corpus_filename
        self.write_corpus_to_file(corpus, self.corpus_filename)



    def write_corpus_to_file(self, corpus: list[str], corpus_filename="") -> None:
        """
        Write the corpus to a file.

        Args:
            corpus (list[str]): A list of strings that represent the corpus.
        """
        filename= self.corpus_filename
        if(corpus_filename != ""):
            filename = corpus_filename
        file = open(corpus_filename, "w")
        for line in corpus:
            file.write(line + "\n")
        file.close()

    def read_corpus_from_file(self) -> list[str]:
        """
        Read the corpus from a file.

        Returns:
            corpus (list[str]): A list of strings that represent the corpus.
        """
        file = open(self.corpus_filename, "r")
        corpus = file.readlines()
        file.close()
        return corpus


    def execute(self, corpus_filename) -> list[str]:

        corpus = self.read_corpus_from_file()

        #remove stop words
        corpus = remove_stopwords(corpus)

        #preprocess documents
        corpus = preprocess_documents(corpus)

        #remove words that only appear once
        frequency = defaultdict(int)
        for doc in corpus:
            for token in doc:
                frequency[token] += 1

        corpus =[
            [token for token in doc if frequency[token] > 1]
            for doc in corpus
        ]

        self.write_corpus_to_file(corpus, f"preprocessed_{corpus_filename}")

        return corpus
    


    def get_preprocessed_corpus(self, corpus_filename = "") -> list[str]:
        if(corpus_filename == ""):
            corpus_filename = self.corpus_filename
        
        #check if preprocessed corpus file exists and is not empty
        preprocessed_corpus_filename = f"preprocessed_{corpus_filename}"
        file = open(preprocessed_corpus_filename, "r")
        preprocessed_corpus = file.readlines()
        file.close()

        if(len(preprocessed_corpus) == 0): #if preprocessed corpus file is empty
            preprocessed_corpus = self.execute(corpus_filename)
        return preprocessed_corpus



    
    