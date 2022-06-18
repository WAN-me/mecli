
import queue
import asyncio
from msspeech import MSSpeech
import os
import os.path
import sys
from typing import overload
import requests
import time
from prompt_toolkit import prompt
from threading import Thread
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.history import FileHistory
import prompt_toolkit
import playsound

def print(obj):
    sys.stdout.write(str(obj)+'\n\r')

async def a_mss_synthesize(voice_name, text, filename):
    mss = MSSpeech()
    v = await mss.get_voices_by_substring(voice_name)
    if len(v) == 0:
        raise ValueError("The voice was not found.")
    await mss.set_voice(v[0]['Name'])
    await mss.synthesize(text.strip(), filename)

def mss_synthesize(*args, **kwargs):
    return asyncio.run(a_mss_synthesize(*args, **kwargs))

q = queue.Queue()
def _play_mss_worker():
    while True:
        if q.empty():
            continue
        text, voice = q.get()
        filename = str(time.time())+".mp3"
        mss_synthesize(
            voice, text, filename
        )
        if os.path.isfile(filename):
            playsound.playsound(filename)
            os.remove(filename)

Thread(target=_play_mss_worker).start()

def play_mss(text, voice):
    q.put((text, voice))

def notif():
    Thread(target=playsound.playsound,args=('not.mp3', True)).start()
class COLOR():
    HEADER="\033[95m"
    BLUE="\033[96m"
    GREEN= "\033[92m"
    RED= "\033[91m"
    ENDC= "\033[0m"

class ctrl():
    c = "\x03"
    x = "\x18"
    d = "\x04"
    s = "\x13"
    n = "\x0e"
    k = "\x0b"
    z = "\x1a"
    h = "\x08"
    j = "\n"

class Session():
    def __init__(self,token,cache):
        self.token = token
        self.cache = cache
        self.write_msg = False
        self.ps = prompt_toolkit.PromptSession("> ",auto_suggest=AutoSuggestFromHistory(),history=FileHistory('.history.txt'))

    def start_poll(self):
        try:
            self.stoppoll()
        except:
            ...
        self.pollth = Thread(target=self.poll)
        self.pollth.daemon = True
        self.pollth.start()

    def stop_poll(self):
        self.pollth.join()
    
    def newgroup(self, name, type):
        return self('groups.new', {'name': name, 'type': type})

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
    
    def groupget(self,id):
        if "groups" in self.cache.data and str(id) in self.cache.data['groups']:
            return self.cache.data['groups'][str(id)]
        else:
            group = self.__call__('groups.get',{"id":id})
            if not "groups" in self.cache.data:
                self.cache.data['groups'] = {}
            self.cache.data['groups'][str(id)] = group
            self.cache.save()
            return self.cache.data['groups'][str(id)]

    def __call__(self,methodname:str,params:dict={}):
        params['accesstoken'] = self.token
        return method(methodname,params)


    def poll(self):
        lp = Lp(self)
        for event in lp.start():
            self.printupdate(event)

    def chose_chat(self):
        "Показывает существующие чаты и предлагает выбрать"
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

    def printmsg(self,message, is_new=False):
        username = self.userget(message['from_id'])['name']
        text = str(message['text']).replace('\n','\n\r')
        if self.write_msg:
            sys.stdout.write(f"\r{' '*(len(self.ps.default_buffer.text)+2)}\r") # Переставить коретку на строку выше, очистить строку
            if message['from_id'] == self.cache.data['me']['id']:
                print(f"{COLOR.BLUE}{text}{COLOR.ENDC}")
            else: 
                print(f"{COLOR.GREEN}{username}{COLOR.ENDC}: {text}")
                if is_new and self.cache.data['tts']['enabled']:
                    play_mss(text=f"{username}: {text}", voice=self.cache.data['tts']['voice'])
            sys.stdout.write("\r> "+self.ps.default_buffer.text)
        else:
            if message['from_id'] == self.cache.data['me']['id']:
                print(f"{COLOR.BLUE}{text}{COLOR.ENDC}\n\033[F")
            else: 
                print(f"{COLOR.GREEN}{username}{COLOR.ENDC}: {text}\n\033[F")
                if is_new and self.cache.data['tts']['enabled']:
                    play_mss(text=f"{username}: {text}", voice=self.cache.data['tts']['voice'])


    def join_chat(self):
        id = input('id чата> ')
        group = self('groups.join', {'id': id})
        if 'error' in group:
            print(group['error']['text'])
        else:
            print('ok')
            return id
    def print_dialog(self,chatid):
        "Запускает обработчик новых событий из чата"
        messages = (self.gethistory(chatid))['items']
        messages.reverse()
        for message in messages:
            self.printmsg(message)

    def create_chat(self):
        "Запускает диалог создания группового чата"
        group = self.newgroup(input('Имя нового чата> '), 1)
        print(group)

    def printupdate(self,upd):
        type = upd["type"]
        if type == 1:
            self.printmsg(upd['object'], is_new=True)
            notif()
        elif type == 2:
            self.printmsg(upd['object'])
        else:
            print(upd)

class Lp:
    def __init__(self, session):
        self.sess = session
    def start(self):
        self.id = None
        while True:
            try:
                s = self.sess("poll.get", {'id': self.id})
                if 'id' in s:
                    self.id = s['id']
                else:
                    if s['count']>0:
                        for up in s["items"]:
                            yield up
                            self.id = up['event_id']
            except requests.exceptions.ConnectionError:
                print("net_error")
            time.sleep(2)

def log(text):
    open("a.log", "a").write(f"\n{text}")


def method(method:str,params:dict={}):
    r = requests.post("http://api.wan-group.ru/method/"+method,data=params)
    if 'password' in params:
        params['password'] = "PASSWORD"
    
    if 'accesstoken' in params:
        params['accesstoken'] = "TOKEN"
        
    try:
        if "error" in r.json():
            log(f"----> {method} {params}")
            log(f"<---- {r.text}")
        return r.json()
    except:
        if "error" in r.content:
            log(f"----> {method} {params}")
            log(f"<---- {r.text}")
        print(r.content)

def stdin(message='',**kwargs):
    return prompt(message, **kwargs)
