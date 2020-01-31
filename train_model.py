from nltk.tokenize import sent_tokenize, word_tokenize
import gensim
sample = open("./custom_model/corpus.txt")
s = sample.read()
f = s.replace("\n"," ")
data=[]
for i in sent_tokenize(f):
    temp = []
    for j in word_tokenize(i):
        temp.append(j.lower())

    data.append(temp)
model1 = gensim.models.Word2Vec(data, min_count=1,
                                size=100, window=5)
model1.save("trained_mod.model")
