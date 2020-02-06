import json
import mysql.connector
from word2vec import w2v
class chatBot:
    def __init__(self):
        self.importData()
        self.topicChooser = w2v()
        cusPrint("hi, what can I help you with?")
    checks = []
    topic = "none"
    state = "OPEN"
    running = True
    topicChooser=None
    topics = []


    def update(self):
        if self.state == "OPEN":
            self.state_open()
        elif self.state == "CONF":
            self.state_conf()
        elif self.state == "TOPIC":
            self.state_topic()
        elif self.state =="REPORT":
            self.state_report()
    def state_report(self):
        inp = cusInput("would you like to submit a maintenance request?")
        if inp == "yes":
            cusPrint("ok, I just need to clarify a few things.")
            location = cusInput("where is the problem located in the property?")
            address = cusInput("what is the address of the property?")
            name = cusInput("and your full name please?")
            number = cusInput("and finally what is your phone number so we can contact you?")
            sql = "INSERT INTO maintenance (location, addr, name, num) VALUES (%s,%s,%s,%s)"
            val = (location,address,name,number)
            conn = mysql.connector.connect(host="localhost", user="root", passwd="Gmysql8952w", database="bot")
            cur = conn.cursor()
            cur.execute(sql, val)
            conn.commit()
            cusPrint("Thank you, I have created a log of your request, we will be in contact with you as soon as possible")
            status = "OPEN"
            self.topic = ""

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
        if self.topic == "None":
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
                temp.append("yes")
                temp.append("no")
                proc = self.topicChooser.topic_select(temp,inp)
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
            self.state = "REPORT"
            fResp = "I'm sorry I couldn't help you with your problem"
        else:
            self.state = "OPEN"
            self.topic = ""
        cusPrint(fResp)


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
    def conDB(self):
        global conn, cur



def cusInput(*args):
    if args != None:
        usrIn = input(args[0])
    else:
        usrIn = input()
    return usrIn

def cusPrint(msg):
    print(msg)


bot = chatBot()
while bot.running:
    bot.update()

