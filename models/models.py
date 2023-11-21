from gensim import models, corpora
import tempfile
import os

class Models:
    def __init__(self, vectorized_text, dictionary):
        self.vectorized_text = vectorized_text
        self.dictionary = dictionary
    
    def train_tfidf(self, no_save=False) -> models.TfidfModel:
        tfidf = models.TfidfModel(self.vectorized_text, normalize=True)
        if no_save == False:
            self.save(tfidf, "tfidf")
        return tfidf
            
    def train_lsi(self, topics=10):
        lsi = models.LsiModel(self.vectorized_text, id2word=self.dictionary, num_topics=topics)
        self.save(lsi, "lsi")
        return lsi

    def train_lda(self, topics=2):
        lda = models.LdaModel(self.vectorized_text, id2word=self.dictionary, num_topics=topics)
        self.save(lda, "lda")
        return lda

    def train_okapi(self):
        okapi = models.OkapiBM25Model(self.vectorized_text)
        self.save(okapi, "okapi")
        return okapi
    
    def train_Rp(self, topics=2):
        # Not sure if this is correct, may need to think more about tfidf?
        tfidf_corpus = self.train_tfidf(no_save=True)[self.vectorized_text]

        rp = models.RpModel(tfidf_corpus, num_topics=topics)

        self.save(rp, "rp")
        return rp
    
    def train_Hdp(self):
        hdp = models.HdpModel(self.vectorized_text, id2word=self.dictionary)

        self.save(hdp, "hdp")
        return hdp
    
    def save(self, model, name):
        if not os.path.exists("models/saved"):
            os.makedirs("models/saved")
        model.save(os.path.join("models/saved", name + ".model"))

    def load(self, model, name):
        return model.load(os.path.join("models/saved", name + ".model"))
        
        


