import json
import mysql.connector
from word2vec import w2v
class chatBot:
    def __init__(self):
        self.importData()
        self.topicChooser = w2v()
        cusPrint("hi, what can I help you with?")
        cursor = conDB()
    cursor = None
    checks = []
    topic = "none"
    state = "OPEN"
    running = True
    topicChooser=None
    topics = []

    def fileReport(self):
        name = input("what is your name? ")
        number = input("what is your phone number")
        topic = self.topic
        chatID = 1 #------------------ToDo impliment chat logging system-------

    def update(self):
        if self.state == "OPEN":
            self.state_open()
        elif self.state == "CONF":
            self.state_conf()
        elif self.state == "TOPIC":
            self.state_topic()

    def state_conf(self):
        uInp = cusInput("are you having a problem with "+ self.topic+"?")
        temp = self.topics
        temp.append("yes")
        temp.append("no")
        res =  self.topicChooser.topic_select(temp,uInp)
        if  res== "yes":
            self.state = "TOPIC"
        if res=="no":
            self.state="OPEN"
            self.topic="none"


    def state_open(self):
        uin = cusInput('')
        self.topic = self.topicChooser.topic_select(self.topics,uin)
        self.state ="CONF"

    def state_topic(self):
        for i in self.checks:
            if i[3] == self.topic:
                inp = cusInput(i[0])
                if i[2] == True:
                    if inp == "no":
                        txt = i[1]
                    elif inp == "yes":
                        txt = i[4]
                    if txt == "Record":
                        self.fileReport()
                    if txt != "":
                        cusPrint(txt)
                        conf = cusInput("did that fix the problem?")
                        if conf == "yes":
                            break
                    else:
                        cusPrint(txt)
                    i[2] = False
        cusPrint("what else can I help you with?")
        self.state = "OPEN"
        self.topic = "none"

    def importData(self):
         with open('config.json') as file:
             tdata = file.read()
             data = json.loads(tdata)
         for i in data['checks']:
            d = data['checks'][str(i)]
            temp = [d["prompt"], d["StepN"],True, d['topic'], d['StepY']]
            if temp[3] not in self.topics:
                self.topics.append(temp[3])
            self.checks.append(temp)


def cusInput(*args):
    if args != None:
        usrIn = input(args[0])
    else:
        usrIn = input()
    return usrIn

def cusPrint(msg):
    print(msg)

def conDB():
    global conn, cur
    conn = mysql.connector.connect(host="localhost", user="root", passwd="Gmysql8952w")
    cur = conn.cursor()
    return cur

bot = chatBot()
while bot.running:
    bot.update()

