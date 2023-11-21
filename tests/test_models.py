import unittest
from models.models import Models
from gensim import models, corpora

class TestModels(unittest.TestCase):
    def setUp(self):
        self.vectorized_text = [[(0,1),(1,1)]]
        self.dictionary = corpora.Dictionary([["test", "test2"]])
        self.models = Models(self.vectorized_text, self.dictionary)

    def test_train_tfidf(self):
        tfidf_model = self.models.train_tfidf()
        self.assertIsInstance(tfidf_model, models.TfidfModel)
        # Add more assertions to validate the behavior of the method

    def test_train_lsi(self):
        lsi_model = self.models.train_lsi()
        self.assertIsInstance(lsi_model, models.LsiModel)
        # Add more assertions to validate the behavior of the method

    def test_train_lda(self):
        lda_model = self.models.train_lda()
        self.assertIsInstance(lda_model, models.LdaModel)
        # Add more assertions to validate the behavior of the method

    def test_train_okapi(self):
        okapi_model = self.models.train_okapi()
        self.assertIsInstance(okapi_model, models.OkapiBM25Model)
        # Add more assertions to validate the behavior of the method

    def test_train_Rp(self):
        rp_model = self.models.train_Rp()
        self.assertIsInstance(rp_model, models.RpModel)
        # Add more assertions to validate the behavior of the method

    def test_train_Hdp(self):
        hdp_model = self.models.train_Hdp()
        self.assertIsInstance(hdp_model, models.HdpModel)
        # Add more assertions to validate the behavior of the method
    
    def test_save_load(self):
        modelPre = self.models.train_tfidf()
        self.models.save(modelPre, "tfidf")
        modelpost = self.models.load(models.TfidfModel, "tfidf")
        self.assertIsInstance(modelpost, models.TfidfModel)


if __name__ == '__main__':
    unittest.main()