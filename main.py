#!/usr/bin/python3
import sys,os
import sbeaver
from pathlib import Path
from classes import ctrl, Session
from jsondb import Db
from classes import stdin, method
from threading import Thread
import getch
import contextlib

if os.name != 'posix':
    import colorama
    colorama.init()

global session

server = sbeaver.Server(address='localhost', port=7239, sync=False, silence=True)

os.system("")  # костыль чтоб работали цвета

cache = Db(f"{Path.home()}/.cache/mecli/cache.json")

def Handler():
    key = handler()
    if key in [ctrl.d,ctrl.c]: 
        os._exit(1)
    elif key == ctrl.x:
        cache.data['chat'] = session.chose_chat()
        session.print_dialog(cache.data['chat']['id'])
    elif key == ctrl.z:
        session.create_chat()
    elif key == ctrl.h:
        print(help)
    elif key == ctrl.j:
        id = session.join_chat()
        obj = session.groupget(id)
        cache.data['chat'] = obj
        session.print_dialog(-cache.data['chat']['id'])

    elif key == ctrl.s:
        session.write_msg = True
        s = session.ps.prompt()
        sys.stdout.write(f"\033[F{' '*(len(s)+2)}\n\033[F")
        session.write_msg = False
        if 'owner_id' in cache.data['chat']:
            Thread(target=session.sendmsg,args=(s,-cache.data['chat']['id'])).start()
        else:
            Thread(target=session.sendmsg,args=(s,cache.data['chat']['id'])).start()

    elif key == ctrl.n:
        id = stdin("id пользователя > ")
        if id.startswith('-'):
            obj = session.groupget(id[1:])
        else:
            obj = session.userget(id)
        if "error" in obj:
            print(obj['error']['text'])
        else:
            cache.data['chat'] = obj
            if 'owner_id' in obj:
                session.print_dialog(-cache.data['chat']['id'])
            else:
                session.print_dialog(cache.data['chat']['id'])

def auth(ligin = "", passwd = ""):
    params = {
    "email": stdin("Введите почту> ", default=ligin),
    "password": stdin("Введите пароль> ",is_password=True, default=passwd)
    }
    
    return method("account.auth",params)


def reg():
    params={
        "name": stdin("Введите имя пользователя> "),
        "email": stdin("Введите почту> "),
        "password": stdin("Введите пароль> ",is_password=True),
        'invitation': stdin("Введите приглашение> ")
    }
    return (method("account.reg",params),params)

session = Session('temp',cache)
handler = getch.Getch()

help = '''ctrl+x для выбора чата
ctrl+s для набора сообщения
ctrl+n для открытия диалога
ctrl+z для создания чата
ctrl+j для вступления в группу
ctrl+h для вывода справки
ctrl+d или ctrl+c для выхода'''


def main():
    if "me" in cache.data:
        global session
        session = Session(cache.data['me']['token'],cache)
        print(f"Привет, {cache.data['me']['name']} (id{cache.data['me']['id']})")
        print(help)
        #session.start_poll()
        
        while True:
            try:
                Handler()
            except KeyboardInterrupt:
                pass
            except Exception as e:
                print(e)
                
        print('ending handler')

        

    else:
        print("Нет сохранений. Войдите в систему\nЗарегистрироваться?\n(д,н)>", end=" ")
        key = " "
        yes = "дДlL"
        no = "yYнН"
        while not key in no+yes+ctrl.c:
            key = handler()
        if key in no:
            print("Нет")
            res = auth()
            if 'token' in res:
                session = Session(res['token'],cache)
                cache.data['me'] = {}
                cache.data['me'] = session('users.get')
                cache.data['me']['token'] = session.token
                cache.save()
                print("Авторизованно!")
                os.system("systemctl restart --user meclid")
                main()
            else: 
                print(res)
        elif key in yes:
            print("Да")
            ss = reg()
            if 'error' in ss[0]:
                print(ss[0]['error'])
                return
            cache.data['me'] = ss[0]
            res = auth(ss[1]['email'],ss[1]['password'])
            
            if 'token' in res:
                session = Session(res['token'],cache)
                print(ss[0].get('advanced'))
                if ss[0].get('advanced') == 'Please check you mailbox':
                    session('account.verif', {"code": stdin('Введите код из электронного письма> ')})
                cache.data['me'] = {}
                cache.data['me'] = session('users.get')
                cache.data['me']['token'] = session.token
                cache.save()
            
            main()
        else:
            print("Выход")
            exit()


@server.sbind('/addmsg')
def addmsg(req):
    print(req.data['text'])
    if session.write_msg:
        sys.stdout.write(f"\r{' '*(len(session.ps.default_buffer.text)+2)}\r") # Переставить коретку на строку выше, очистить строку
        print(req.data['text'])
        sys.stdout.write("\r> "+session.ps.default_buffer.text)
    else:
        print(req.data['text'])
        
    return 200, ''
th = Thread(target=server.start, daemon=True)
with open('help.txt', 'w') as f:
    with contextlib.redirect_stdout(f):
        th.start()

main.main()