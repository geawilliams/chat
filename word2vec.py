import gensim
from gensim.models import KeyedVectors
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
import nltk
#nltk.download('punkt')
#nltk.download('stopwords')
class w2v:
    model=None
    def __init__(self):
        self.model = KeyedVectors.load("./trimmed.model")
        #self.model = gensim.models.KeyedVectors.load_word2vec_format('./GoogleNewsModel.bin',limit=100000, binary=True)
        #self.model = Word2Vec.load("./trained_mod_V2.model")

    def topic_select(self, topics, uin,thresh):
        tInput = uin
        topSim = []
        for topic in topics:
            similarity = 0
            for w in tInput:
                vectors = self.model.wv
                for tag in topic[1]:
                    if w in vectors and tag in vectors:
                        sim = self.model.similarity(tag, w)
                        if sim > similarity and sim > thresh:
                            similarity = sim
                            topSim.append([topic[0], similarity])

        chosenTopic = self.findTop(topSim)
        return chosenTopic
    def topic_select_V3(self,topics, uin,thresh):
        tInput = word_tokenize(uin)
        topSim=[]
        vectors = self.model.wv
        for topic in topics:
            topicSim=0
            topicN=0
            for w in tInput:
                for tag in topic[1]:
                    if w in vectors and tag in vectors:
                        sim = self.model.similarity(tag, w)
                        if sim>thresh:
                            topicSim+=sim
                            topicN+=1
            if topicSim!=0:
                topSim.append([topic[0],topicSim/topicN])

        chosenTopic = self.findTop(topSim)
        return chosenTopic

    def stem_txt(self,msg):
        stemmer = PorterStemmer()
        t=[]
        for m in msg:
            t.append(stemmer.stem(m))
        return t
    def topic_select_V2(self, topics, uin, thresh):
        tInput = word_tokenize(uin)
        tInput = self.stem_txt(tInput)
        top_av_sim=[]
        vectors = self.model.wv
        for topic in topics:
            total=0
            n=0
            for tag in topic[1]:
                tag = PorterStemmer().stem(tag)
                t=0
                for w in tInput:
                    if w in vectors and tag in vectors:
                        sim = self.model.similarity(tag, w)
                        if sim>thresh:
                            t=t+sim
                total+=t
                n+=1
            if total==0:
                top_av_sim.append([topic[0], 0])
            else:
                top_av_sim.append([topic[0], total/n])
        chosenTopic = self.findTop(top_av_sim)
        return chosenTopic

    def remStopWords(self,txt):
        stopW = set(stopwords.words('english'))
        filtered = []
        for w in txt:
            if w not in stopW:
                filtered.append(w)
        return filtered

    def func_select(self,functions,uin,thresh):
        finfun =None
        similarity=0
        tInput=uin
        #tInput = word_tokenize(uin)
        #tInput = self.stem_txt(tInput)
        #tInput = self.remStopWords(tInput)
        vectors = self.model.wv
        for f in functions:
            for w in tInput:
                if w in vectors:
                    nsim = self.model.similarity(f,w)
                    if nsim>similarity and nsim>thresh:
                        similarity = nsim
                        finfun = f
        return [finfun,similarity]

    def findTop(self,topSim):
        topic=""
        score=0
        RtopSim=[]
        topSim = self.sort(topSim)
        for i in reversed(topSim):
            RtopSim.append(i)
        final=[]
        if len(RtopSim)>3:
            l=3
        else:
            l = len(RtopSim)
        for i in range(l):
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