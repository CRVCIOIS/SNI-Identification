import os
import unittest
import tempfile

from input.input_text_file import FileInputCorpus

class TestFileInputCorpus(unittest.TestCase):
    def test_empty_corpus(self):
        with tempfile.TemporaryDirectory() as tempdir:
            with open(os.path.join(tempdir, "test_corpus1.txt"), "w") as f:
                f.write("")
                f.close()
            iterator = FileInputCorpus(os.path.join(tempdir, f.name))
            expected = [
                []
            ]
            
            
            for coprus_streaming_line in iterator:
                self.assertEqual(coprus_streaming_line, [expected.pop(0)])
            self.assertEqual(expected, [[]])


    def test_single_line_corpus(self):
        with tempfile.TemporaryDirectory() as tempdir:
            with open(os.path.join(tempdir, "test_corpus2.txt"), "w") as f:
                f.write("Better late than never, but better never late.")
                f.close()
            iterator = FileInputCorpus(os.path.join(tempdir, f.name))
            expected=[
                [(0, 2), (1, 2)],
            ]
            #check if equal to iterated expected
            for coprus_streaming_line, expected_line in zip(iterator, expected):
                self.assertEqual(coprus_streaming_line, expected.pop(0))
                
            self.assertEqual(expected, []) #check if all expected lines are iterated over
                

    def test_multiple_line_corpus(self):
        with tempfile.TemporaryDirectory() as tempdir:
            with open(os.path.join(tempdir, "test_corpus3.txt"), "w") as f:
                f.write("Better late than never, but better never late.\n")
                f.write("<i>Hel 9lo</i> <b>Wo9 rld</b>! Th3     weather_is really g00d today, isn't it?\n")
                f.write("test test2 test1 test3 test2\n")
                f.close()
            iterator = FileInputCorpus(os.path.join(tempdir, f.name))
            
            
            expected=[
                [(0, 2), (1, 2)],
                [(2, 1), (3, 1), (4, 1), (5, 1), (6, 1)],
                [(7, 5)]
            ]
          
            # check if equal to iterated expected
            for coprus_streaming_line in iterator:
                self.assertEqual(coprus_streaming_line, expected.pop(0)) 
            self.assertEqual(expected, []) #check if all expected lines are iterated over
            

if __name__ == '__main__':
    unittest.main()