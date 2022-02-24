
import requests
import time
from prompt_toolkit import prompt

class COLOR():
    HEADER="\033[95m"
    BLUE="\033[94m"
    GREEN= "\033[92m"
    RED= "\033[91m"
    ENDC= "\033[0m"

class ctrl():
    c = "\x03"
    x = "\x18"
    d = "\x04"
    s = "\x13"
    n = "\x0e"

class Session():
    def __init__(self,token,cache):
        self.token = token
        self.cache = cache

    def sendmsg(self,text:str,to):
        if not text.strip() == "":
            return self.__call__('messages.send',{"text":text,"to_id":to})

    def gethistory(self,id):
        return self.__call__('messages.gethistory',{"user_id":id})

    def userget(self,id):
        if "users" in self.cache.data and str(id) in self.cache.data['users']:
            return self.cache.data['users'][str(id)]
        else:
            user = self.__call__('users.get',{"id":id})
            if not "users" in self.cache.data:
                self.cache.data['users'] = {}
            self.cache.data['users'][str(id)] = user
            self.cache.save()
            return self.cache.data['users'][str(id)]

    def __call__(self,methodname:str,params:dict={}):
        params['accesstoken'] = self.token
        return method(methodname,params)


    def poll(self):
        lp = Lp(self)
        for event in lp.start():
            self.printupdate(event)

    def choseChat(self):
        chats = self('messages.chats')
        print(f"Чатов - {chats['count']}")
        for rawchat in range(len(chats['items'])):
            chat = chats['items'][rawchat]
            print(f"{rawchat+1}: {chat['name']} (id{chat['id']})")
        norm = False
        chat = {}
        while not norm:
            chatid = stdin("Введите номер чата> ")
            try:
                id = int(chatid)
                chat = chats['items'][id-1]
                norm = True
            except:
                print('Невалидно!')
        return chat

    def printmsg(self,message):
        username = self.userget(message['from_id'])['name']
        text = message['text']
        if message['from_id'] == self.cache.data['me']['id']:
            print(f"{COLOR.BLUE}{text}{COLOR.ENDC}")
        else: 
            print(f"{COLOR.GREEN}{username}{COLOR.ENDC}: {text}")

    def printdialog(self,chatid):
        messages = (self.gethistory(chatid))['items']
        messages.reverse()
        for message in messages:
            self.printmsg(message)

    
    def printupdate(self,upd):
        type = upd["type"]
        if type == 1:
            self.printmsg(upd['object'])
        elif type == 2:
            self.printmsg(upd['object'])
        else:
            print(upd)

class Lp:
    def __init__(self, session):
        self.sess = session
    def start(self):
        while True:
            s = self.sess("Pool.get")
            if s['count']>0:
                for up in s["items"]:
                    yield up
                self.sess("Pool.read")
            time.sleep(2)

def log(text):
    open("a.log", "a").write(f"\n{text}")

def method(method:str,params:dict={}):
    log(f"----> {method} {params}")
    r = requests.post("http://api.wan-group.ru/method/"+method,data=params)
    log(f"<---- {r.text}")
    try:
        return r.json()
    except:
        print(r.content)

def stdin(message='',**kwargs):
    return prompt(message, **kwargs)