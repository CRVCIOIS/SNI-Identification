import os
import unittest
from input.preprocess import InputPreprocess
from collections import defaultdict

class PreprocessTest(unittest.TestCase):
    def setUp(self):
        self.preprocessor = InputPreprocess()
        self.corpus_filename = "corpus.txt"


    """"
    Test the get_preprocessed_corpus method with an existing file, an empty file and no file.
    """
    def test_get_preprocessed_corpus_with_existing_file(self):
        # Create a preprocessed corpus file with some content
        preprocessed_corpus_filename = f"preprocessed_{self.corpus_filename}"
        with open(preprocessed_corpus_filename, "w") as file:
            file.write("This is a preprocessed corpus")

        # Call the get_preprocessed_corpus method
        preprocessed_corpus = self.preprocessor.get_preprocessed_corpus(self.corpus_filename)

        # Assert that the returned preprocessed_corpus is the same as the content in the file
        self.assertEqual(preprocessed_corpus, ["This is a preprocessed corpus"])

    def test_get_preprocessed_corpus_with_empty_file(self):
        # Create an empty preprocessed corpus file
        preprocessed_corpus_filename = f"preprocessed_{self.corpus_filename}"
        open(preprocessed_corpus_filename, "w").close()

        # Mock the execute method to return a preprocessed corpus
        self.preprocessor.execute = lambda filename: ["This is a preprocessed corpus"]

        # Call the get_preprocessed_corpus method
        preprocessed_corpus = self.preprocessor.get_preprocessed_corpus(self.corpus_filename)

        # Assert that the returned preprocessed_corpus is the same as the mocked result
        self.assertEqual(preprocessed_corpus, ["This is a preprocessed corpus"])

    def test_get_preprocessed_corpus_with_no_file(self):
        # Mock the execute method to return a preprocessed corpus
        self.preprocessor.execute = lambda filename: ["This is a preprocessed corpus"]

        # Call the get_preprocessed_corpus method without specifying a file
        preprocessed_corpus = self.preprocessor.get_preprocessed_corpus()

        # Assert that the returned preprocessed_corpus is the same as the mocked result
        self.assertEqual(preprocessed_corpus, ["This is a preprocessed corpus"])


    """"
    Test the write_corpus_to_file method.
    """
    def test_write_corpus_to_file(self):
        # Define a sample corpus
        corpus = ["This is line 1", "This is line 2", "This is line 3"]

        # Define a sample filename
        corpus_filename = "test_corpus.txt"

        # Call the write_corpus_to_file method
        self.preprocessor.write_corpus_to_file(corpus, corpus_filename)

        # Read the contents of the file
        with open(corpus_filename, "r") as file:
            file_contents = file.readlines()

        # Assert that the file contents match the original corpus
        self.assertEqual(file_contents, ["This is line 1\n", "This is line 2\n", "This is line 3\n"])

        # Clean up the test file
        os.remove(corpus_filename)

    def test_read_corpus_from_file(self):
        # Define a sample corpus file
        corpus_filename = "test_corpus.txt"
        with open(corpus_filename, "w") as file:
            file.write("This is line 1\nThis is line 2\nThis is line 3\n")

        # Set the corpus filename in the preprocessor
        self.preprocessor.corpus_filename = corpus_filename

        # Call the read_corpus_from_file method
        corpus = self.preprocessor.read_corpus_from_file()

        # Assert that the returned corpus is the same as the contents of the file
        self.assertEqual(corpus, ["This is line 1\n", "This is line 2\n", "This is line 3\n"])

        # Clean up the test file
        os.remove(corpus_filename)


    def test_execute(self):
        # Define a sample corpus
        corpus = [
            ["This", "is", "a", "sample", "document"],
            ["Another", "sample", "document"],
            ["Yet", "another", "sample", "document"]
        ]

        # Mock the read_corpus_from_file method to return the sample corpus
        self.preprocessor.read_corpus_from_file = lambda: corpus

        # Mock the remove_stopwords method
        self.preprocessor.remove_stopwords = lambda corpus: [
            ["This", "sample", "document"],
            ["Another", "sample", "document"],
            ["Yet", "another", "sample", "document"]
        ]

        # Mock the preprocess_documents method
        self.preprocessor.preprocess_documents = lambda corpus: [
            ["This", "sample", "document"],
            ["Another", "sample", "document"],
            ["Yet", "another", "sample", "document"]
        ]

         

        # Mock the write_corpus_to_file method
        self.preprocessor.write_corpus_to_file = lambda corpus, filename: None

        # Call the execute method
        result = self.preprocessor.execute(self.corpus_filename)

        # Assert that the result is the preprocessed corpus
        self.assertEqual(result, [
            ["This", "sample", "document"],
            ["Another", "sample", "document"],
            ["Yet", "another", "sample", "document"]
        ])
    


if __name__ == '__main__':
    unittest.main()

