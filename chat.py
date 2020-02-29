import json
import datetime
import mysql.connector
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from word2vec import w2v
class chatBot:
    def __init__(self):
        self.importData()
        self.topicChooser = w2v()
        self.conDB()
        self.cusPrint("hi, what can I help you with?")

#internal states
    function=None
    topic = [None,None]
    state = "OPEN"
    running = True
    topTopics=[]
    lastMsg=""
    MsgS=[]
#data
    info=[]
    topicChooser=None
    topics = []
    checks = []

    def update(self):
        if self.state == "OPEN":
            self.state_open()
        elif self.state == "CONF":
            self.state_conf()
        elif self.state == "TOPIC":
            self.state_topic()
        elif self.state == "FUNC":
            if self.function=="what":
                self.func_question()
            elif self.function=="maintenance":
                self.func_maintenance()
                self.clr()
            elif self.function=="complain":
                self.func_complaint()
                self.clr()
            elif self.function=="feedback":
                self.func_complaint()
                self.clr()

    def clr(self):
        self.state="OPEN"
        self.topic=[None,None]
        self.function=None
        self.topTopics=[]
        self.cusPrint("What else can I help you with? ")

    def state_conf(self):
        if len(self.topTopics)>=1:

            uInp = self.cusInput("are you having a problem with "+ self.topic[0]+"?")
            temp = self.topics
            temp.append(["yes",["yes"]])
            temp.append(["no",["no"]])
            res =  self.topicChooser.topic_select_V2(temp,uInp, 0.4)
            if  res[0][0]== "yes":
                self.state = "TOPIC"
            elif res[0][0]=="no":
                del self.topTopics[0]
                if len(self.topTopics)>0:
                    self.topic = self.topTopics[0]
                else:
                    self.state="OPEN"
                    self.topic=[None,None]
                    self.cusPrint("sorry i don't think i know what you mean, what else may i help you with?")
            else:
                self.troubleshooter_detection(uInp)
        else:
            self.state = "OPEN"
            self.cusPrint("sorry i don't think i know what you mean, what else may i help you with?")



    def state_open(self):
        uin = self.cusInput('')
        #funcitionality checks (if the user wants to submit maintinance request/complaint/ask question)

        functions = ["maintenance", "complain", "feedback"]
        tInput = word_tokenize(uin)
        tremStopwInput = self.topicChooser.remStopWords(tInput)
        stemStopInp = self.topicChooser.stem_txt(tremStopwInput)
        func = self.topicChooser.func_select(functions, stemStopInp,0.35)
        if func[0] != None:
            self.setFunction(func[0])
            return
        #question detections, detects similar interigative words
        func=self.topicChooser.func_select(["what","where"],tInput,0.6)
        if func[0] =="what" or func[0] =="where":
            self.setFunction("what")
            return
        else:
            self.troubleshooter_detection(uin)
    def state_topic(self):
        fResp = ""
        for i in self.checks:
            if i[3] == self.topic[0]:
                inp = self.cusInput(i[0])
                temp=self.topics
                temp.append(["yes",["yes"]])
                temp.append(["no",["no"]])
                proc = self.topicChooser.topic_select_V2(temp,inp, 0.6)[0][0]
                if i[2] == True:
                    if proc == "no":
                        txt = i[1]
                    elif proc == "yes":
                        txt = i[4]
                    if txt == "Record":
                        self.func_maintenance()
                        break
                    if txt != "":
                        self.cusPrint(txt)
                        conf = self.cusInput("Did that fix the problem?")
                        if conf == "yes":
                            fResp = "Great!"

                            break
                    i[2] = False
        if fResp == "":
            fResp = "I'm sorry. "
            self.func_maintenance()
        else:
            self.state = "OPEN"
            self.topic = ["",None]
        self.cusPrint(fResp)
        self.clr()

    def troubleshooter_detection(self, uin):
        uin = word_tokenize(uin)
        uin = self.topicChooser.remStopWords(uin)
        urgent = self.urgencyCheck()
        self.topTopics = self.topicChooser.topic_select(self.topics,uin,0.2)
        if(self.topTopics!=[]):
            self.topic = self.topTopics[0]
            if self.topic[0] == "None":
                cusPrint("GoodBye!")
                self.running = False
            elif self.topic[1]>0.3:
                self.state = "CONF"
            else:
                self.cusPrint("Sorry, I didn't understand that")
                self.clr()
        else:
            self.cusPrint("Sorry, I didn't understand that")
            self.clr()


    def func_maintenance(self):
        inp = self.cusInput("would you like to submit a maintenance request?")
        temp = self.topics
        temp.append(["yes",["yes"]])
        temp.append(["no",["no"]])
        res = self.topicChooser.topic_select_V2(temp, inp, 0.5)
        urgent = self.urgencyCheck()
        print(urgent)
        if res[0][0] == "yes":
            global conm, cur
            self.cusPrint("ok, I just need to clarify a few things.")
            location = self.cusInput("can you provide a general description of the problem")
            address = self.cusInput("what is the address of the property?")
            name = self.cusInput("and your full name please?")
            number = self.cusInput("and finally what is your phone number so we can contact you?")
            sql = "INSERT INTO maintenance (loc, addr, name, num, topic, CID, emergency, MID, date) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            val = (location, address, name, number, self.topic[0], CID,urgent,None, datetime.datetime.now())
            cur.execute(sql, val)
            conn.commit()
            self.cusPrint(
                "Thank you, I have created a log of your request, we will be in contact with you as soon as possible")
            self.state = "OPEN"
            self.topic = ""

    def func_question(self):
        msg = word_tokenize(self.lastMsg)
        msg = self.topicChooser.remStopWords(msg)
        data = self.topicChooser.topic_select(self.info,msg, 0.4)
        if len(data)>0:
            if data[0][1] >0.4:
                print(data[0][0])
                self.state="OPEN"
            else:
                self.troubleshooter_detection(self.lastMsg)
        else:
            self.troubleshooter_detection(self.lastMsg)

    def func_complaint(self):
        inp = self.cusInput("would you like to me to submit an official complaint/feedback report for you")
        if inp == "yes":
            global conm, cur
            self.cusPrint("ok, I just need to clarify a few things.")
            address = self.cusInput("what is the address of the property?")
            name = self.cusInput("and your full name please?")
            number = self.cusInput("and finally what is your phone number so we can contact you?")
            desc = self.cusInput("Thank you. now finally what would you like to report?")
            sql = "INSERT INTO complaint (descr, addr, name, num, topic, CID) VALUES (%s,%s,%s,%s,%s,%s)"
            val = (desc, address, name, number,self.topic, "1")
            #cur.execute(sql, val)
            #conn.commit()
            self.cusPrint(
                "Thank you, the report has been created!")
            self.state = "OPEN"
            self.topic = ""

    def setFunction(self,func):
        self.function=func
        if func =="maintenance":
            self.function="maintenance"
            self.state="FUNC"
        elif func =="what":
            self.function = "what"
            self.state = "FUNC"
        elif func == "complain":
            self.function = "complain"
            self.state = "FUNC"
        elif func == "complain":
            self.function = "complain"
            self.state = "FUNC"

    def importData(self):
        with open('config.json') as file:
             tdata = file.read()
             data = json.loads(tdata)
        for i in data['checks']:
            d = data['checks'][str(i)]
            temp = [d["prompt"], d["StepN"],True, d['topic'], d['StepY']]
            self.checks.append(temp)
        for i in data['topics']:
            d=data['topics'][str(i)]
            temp = [d['topic'],d['tags']]
            self.topics.append(temp)
        for i in data['info']:
            d=data['info'][i]
            temp = [d['data'],d['tags']]
            self.info.append(temp)
    def urgencyCheck(self):
        str=""
        for m in self.MsgS:
            str+=m
        str = word_tokenize(str)
        str = self.topicChooser.remStopWords(str)
        out = self.topicChooser.func_select(["urgent"],str,0.4)
        if out[0] =="urgent":
            return True
        else:
            return False
    def conDB(self):
        global conn, cur
        conn = mysql.connector.connect(host="localhost", user="root", passwd="Gmysql8952w", database="bot")
        cur = conn.cursor()

    def cusInput(self,msg):
        if msg != "":
            global conn,cur
            sql = "INSERT INTO clog (mID, bot, msg, date, CID) VALUES(%s,%s,%s,%s,%s)"
            val = ("1", "1", msg, datetime.datetime.now(), "1")

            f = open("chatLog.txt", "a")
            f.write(msg + "\n")

            #cur.execute(sql, val)
            #conn.commit()
            usrIn = input(msg)
            self.MsgS.append(usrIn)
            self.lastMsg = usrIn

        else:
            usrIn = input()
            self.MsgS.append(usrIn)
            self.lastMsg = usrIn
        return usrIn

    def cusPrint(self, msg):
        global conn, cur
        sql = "INSERT INTO clog (mID, bot, msg, date, CID) VALUES(%s,%s,%s,%s,%s)"
        val =("1","1",msg,datetime.datetime.now(),"1")
        f=open("chatLog.txt","a")
        f.write(msg+"\n")

        #cur.execute(sql, val)
        #conn.commit()
        print(msg)

bot = chatBot()
while bot.running:
    bot.update()

