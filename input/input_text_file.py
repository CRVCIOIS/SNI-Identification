import pprint
from input_file_class import InputFileReader


class TextFileReader(InputFileReader):
    """
    A class for reading text files and retrieving the corpus.

    Attributes:
        file_path (str): The path to the input text file.
        lines (list[str]): The lines of the text file.

    Methods:
        get_corpus(): Reads the text file and returns the lines as a corpus
        print_corpus(): Prints the corpus
    """

    def __init__(self, file_path):
        self.file_path = file_path

    def get_corpus(self) -> list[str]:
        """
        Reads the text file and returns each line as a document in a corpus.

        Returns:
            list[str]: Corpus
        """
        try:
            with open(self.file_path, 'r') as file:
                lines = file.readlines()
                return lines
        except FileNotFoundError:
            print(f"File '{self.file_path}' not found.")

    def print_corpus(self):
        """
        Prints the corpus
        """
        corpus = self.get_corpus()
        pprint(corpus)
            
            
    def stringToVector(self):
        """
        Returns a list of vectors, each vector represents a line in the corpus
        """
        vector = []
        for line in self.lines:
            line = line.strip()
            vector.append(line)
        return vector


    def corpus_streaming(self):
        """
        Returns a generator object that yields each line of the corpus.
        """
        for line in self.lines:
            yield line.doc2bow(line.lower().split())


    
