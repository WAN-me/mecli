from threading import Thread
import getch
from jsondb import Db
import sys,os
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.history import FileHistory
from classes import ctrl, Session
from classes import stdin, method


os.system("")  # костыль чтоб работали цвета

cache = Db("cache.json")

def Handler():
    key = handler()
    if key in [ctrl.d]: 
        os._exit(1)
    elif key == ctrl.x:
        cache.data['chat'] = session.choseChat()
        session.printdialog(cache.data['chat']['id'])
    elif key == ctrl.s:
        s = stdin("> ",auto_suggest=AutoSuggestFromHistory(),history=FileHistory('.history.txt'))
        sys.stdout.write(f"\033[F{' '*(len(s)+2)}\n\033[F")
        session.sendmsg(s,cache.data['chat']['id'])
    elif key == ctrl.n:
        id = stdin("id пользователя > ")
        user = session.userget(id)
        if "error" in user:
            print(user['error']['text'])
        else:
            cache.data['chat'] = user
            session.printdialog(cache.data['chat']['id'])

def auth(ligin = "", passwd = ""):
    params = {
    "login": stdin("Введите почту> ", default=ligin),
    "password": stdin("Введите пароль> ",is_password=True, default=passwd)
    }
    return method("users.auth",params)


def reg():
    params={
        "name": stdin("Введите имя пользователя> "),
        "email": stdin("Введите почту> "),
        "password": stdin("Введите пароль> ",is_password=True)
    }
    return (method("users.reg",params),params)

session = Session('temp',cache)
handler = getch.Getch()

def main():
    if "me" in cache.data:
        global session
        session = Session(cache.data['me']['token'],cache)
        print(f"Привет, {cache.data['me']['name']}")
        session.startpool()
        print('ctrl+x для выбора чата\nctrl+s для набора сообщения\nctrl+n для открытия диалога\nctrl+d для выхода\n')
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
            main()
        elif key in yes:
            print("Да")
            ss = reg()
            cache.data['me'] = ss[0]
            res = auth(ss[1]['email'],ss[1]['password'])
            if 'token' in res:
                session = Session(res['token'],cache)
                cache.data['me'] = {}
                cache.data['me'] = session('users.get')
                cache.data['me']['token'] = session.token
                cache.save()
        else:
            print("Выход")
            exit()

main()