import os
import tempfile
from smart_open import open
from gensim.corpora.textcorpus import TextCorpus
from gensim import utils
from gensim.parsing.preprocessing import strip_tags, strip_punctuation, strip_multiple_whitespaces, strip_numeric, remove_stopwords, strip_short, stem_text, preprocess_string
from gensim.utils import simple_tokenize
class FileInputCorpus(TextCorpus):
    stopwords = set('for a of the and to in on'.split())
    
    def get_texts(self):
        for doc in self.getstream():
            doc = utils.to_unicode(doc).lower().strip()
            yield self.preprocess_text(doc)
            
                
    def __len__(self):
        """
        Returns the number of documents in the corpus.
        Returns:
            int: Number of documents.
        """
        self.length = sum(1 for line in open(self.input))
        return self.length
    
    def preprocess_text(self, text):
        """
        Preprocess a single document.
        Args:
            text (str): Text to preprocess.
        Returns:
            list[str]: Preprocessed text and tokenzied.
        """
        #TODO: add more preprocessing steps to the pipeline. Should take a string and return a string.
        
        return super().preprocess_text(text)
    
    
        

            
 

                
  
        