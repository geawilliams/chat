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
                for tag in topic[1]:
                    if w in vectors and tag in vectors:
                        sim = self.model.similarity(tag, w)
                        if sim>similarity and sim>0.2:
                            similarity = sim
                            topSim.append([topic[0], similarity])

        chosenTopic = self.findTop(topSim)
        return chosenTopic

    def findTop(self,topSim):
        topic=""
        score=0
        RtopSim=[]
        topSim = self.sort(topSim)
        for i in reversed(topSim):
            RtopSim.append(i)
        final=[]
        for i in range(0,3):
            if len(RtopSim)>=i:
                final.append(RtopSim[i])
        return final

    def sort(self, array):
        less = []
        equal = []
        greater = []
        if len(array) > 1:
            pivot = array[0]
            for x in array:
                if x[1] < pivot[1]:
                    less.append(x)
                if x[1] == pivot[1]:
                    equal.append(x)
                if x[1] > pivot[1]:
                    greater.append(x)
            return self.sort(less) + equal + self.sort(greater)
        else:
            return array