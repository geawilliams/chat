import gensim
from gensim.models import Word2Vec
from nltk.tokenize import word_tokenize
import nltk
#nltk.download('punkt')
class w2v:
    model=None
    def __init__(self):
        self.model = gensim.models.KeyedVectors.load_word2vec_format('./GoogleNewsModel.bin',limit=100000, binary=True)
        #self.model = Word2Vec.load("./trained_mod.model")
    def topic_select(self,topics, uin):
        tInput = word_tokenize(uin)
        topSim = []
        for topic in topics:
            similarity=0
            for w in tInput:
                vectors = self.model.wv
                if w in vectors and topic in vectors:
                    sim = self.model.similarity(topic, w)
                    if sim>similarity:
                        similarity = sim
            topSim.append([topic,similarity])
        chosenTopic = self.findTop(topSim)
        return chosenTopic

    def findTop(self,topSim):
        topic=""
        score=0
        for i in topSim:
            if i[1]>score:
                score = i[1]
                topic =i[0]
        return topic