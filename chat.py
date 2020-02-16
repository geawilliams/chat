import json
import datetime
import mysql.connector
from word2vec import w2v
class chatBot:
    def __init__(self):
        self.importData()
        self.topicChooser = w2v()
        self.conDB()
        cusPrint("hi, what can I help you with?")

#internal states
    function=None
    topic = "none"
    state = "OPEN"
    running = True
    topTopics=[]
    lastMsg=None
    info=[]
#data
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
                self.clr()
            elif self.function=="maintenance":
                self.func_maintenance()
                self.clr()
            elif self.function=="complaint":
                self.func_complaint()
                self.clr()
            elif self.function=="feedback":
                self.func_complaint()
                self.clr()

    def clr(self):
        self.state="OPEN"
        self.topic=None
        self.function=None
        cusPrint("Is there anything else I can help you with? ")

    def state_conf(self):
        uInp = cusInput("are you having a problem with "+ self.topic+"?")
        temp = self.topics
        temp.append(["yes",["yes"]])
        temp.append(["no",["no"]])
        res =  self.topicChooser.topic_select(temp,uInp)
        if  res[0][0]== "yes":
            self.state = "TOPIC"
        if res[0][0]=="no":
            del self.topTopics[0]
            if len(self.topTopics)>0:
                self.topic = self.topTopics[0][0]
            else:
                self.state="OPEN"
                self.topic="none"

    def state_open(self):
        uin = cusInput('')
        #funcitionality checks (if the user wants to submit maintinance request/complaint/ask question)
        func=self.topicChooser.func_select(["what"],uin)
        if func[0] =="what":
            self.setFunction(func[0])
            return
        else:
            functions=["maintenance", "complain", "feedback"]
            func = self.topicChooser.func_select(functions, uin)
            if func[0] != None:
                self.setFunction(func)
                return

        #catch all: checks if problem matches troubleshooting backend
        self.topTopics = self.topicChooser.topic_select_V2(self.topics,uin)
        self.topic = self.topTopics[0][0]
        if self.topic == "None":
            print(self.topTopics[0][0])
            cusPrint("GoodBye!")
            self.running = False
        else:
            self.state = "CONF"

    def state_topic(self):
        fResp = ""
        for i in self.checks:
            if i[3] == self.topic:
                inp = cusInput(i[0])
                temp=self.topics
                temp.append(["yes",["yes"]])
                temp.append(["no",["no"]])
                proc = self.topicChooser.topic_select(temp,inp)[0][0]
                if i[2] == True:
                    if proc == "no":
                        txt = i[1]
                    elif proc == "yes":
                        txt = i[4]
                    if txt == "Record":

                        break
                    if txt != "":
                        cusPrint(txt)
                        conf = cusInput("Did that fix the problem?")
                        if conf == "yes":
                            fResp = "Great! is there anything else I can help you with?"
                            break
                    i[2] = False
        if fResp == "":
            fResp = "I'm sorry I couldn't help you with your problem"
            func_maintenance()
        else:
            self.state = "OPEN"
            self.topic = ""
        cusPrint(fResp)

    def func_maintenance(self):
        inp = cusInput("would you like to submit a maintenance request?")
        if inp == "yes":
            global conm, cur
            cusPrint("ok, I just need to clarify a few things.")
            location = cusInput("can you provide a general description of the problem")
            address = cusInput("what is the address of the property?")
            name = cusInput("and your full name please?")
            number = cusInput("and finally what is your phone number so we can contact you?")
            sql = "INSERT INTO maintenance (loc, addr, name, num, topic, CID) VALUES (%s,%s,%s,%s,%s,%s)"
            val = (location, address, name, number, self.topic, "1")
            cur.execute(sql, val)
            conn.commit()
            cusPrint(
                "Thank you, I have created a log of your request, we will be in contact with you as soon as possible")
            self.state = "OPEN"
            self.topic = ""

    def func_question(self):
        global lastMsg
        data = self.topicChooser.topic_select_V2(self.info,lastMsg)
        print(data[0][0])
        self.state=="OPEN"
        self.function==None

    def func_complaint(self):
        inp = cusInput("would you like to submit an official complaint/feedback report")
        if inp == "yes":
            global conm, cur
            cusPrint("ok, I just need to clarify a few things.")
            address = cusInput("what is the address of the property?")
            name = cusInput("and your full name please?")
            number = cusInput("and finally what is your phone number so we can contact you?")
            desc = cusInput("Thank you. now finally what would you like to report?")
            sql = "INSERT INTO complaint (descr, addr, name, num, topic, CID) VALUES (%s,%s,%s,%s,%s,%s)"
            val = (desc, address, name, number, "1")
            cur.execute(sql, val)
            conn.commit()
            cusPrint(
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

    def conDB(self):
        global conn, cur
        conn = mysql.connector.connect(host="localhost", user="root", passwd="Gmysql8952w", database="bot")
        cur = conn.cursor()

def cusInput(*args):
    if args != None:
        global conn,cur, lastMsg
        sql = "INSERT INTO clog (mID, bot, msg, date, CID) VALUES(%s,%s,%s,%s,%s)"
        val = ("1", "1", args[0], datetime.datetime.now(), "1")

        cur.execute(sql, val)
        conn.commit()
        usrIn = input(args[0])
        lastMsg = usrIn
    else:
        usrIn = input()
    return usrIn

def cusPrint(msg):
    global conn, cur
    sql = "INSERT INTO clog (mID, bot, msg, date, CID) VALUES(%s,%s,%s,%s,%s)"
    val =("1","1",msg,datetime.datetime.now(),"1")
    cur.execute(sql, val)
    conn.commit()
    print(msg)

bot = chatBot()
while bot.running:
    bot.update()

