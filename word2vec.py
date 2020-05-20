import gensim
from gensim.models import KeyedVectors
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
import nltk
#uncomment code for the initial run of the program to download the nessasery NLTK corpus's used within the project
#nltk.download('punkt')
#nltk.download('stopwords')
class w2v:
    model=None
    def __init__(self):
        self.model = KeyedVectors.load("./trimmed.model")

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

    def stem_txt(self,msg):
        stemmer = PorterStemmer()
        t=[]
        for m in msg:
            t.append(stemmer.stem(m))
        return t
    def topic_select_V2(self, topics, uin, thresh):
        tInput = word_tokenize(uin)
        top_av_sim=[]
        vectors = self.model.wv
        for topic in topics:
            total=0
            n=0
            for tag in topic[1]:
                t=0
                for w in tInput:
                    if w in vectors and tag in vectors:
                        sim = self.model.similarity(tag, w)
                        if sim>thresh:
                            t=t+sim

                total+=t
                n+=1
            if total!=0:
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

    def sort(self, topics):
        low = []
        mid = []
        high = []
        if len(topics) > 1:
            p = topics[0]
            for x in topics:
                if x[1] < p[1]:
                    low.append(x)
                if x[1] == p[1]:
                    mid.append(x)
                if x[1] > p[1]:
                    high.append(x)
            return self.sort(low) + mid + self.sort(high)
        else:
            return topics