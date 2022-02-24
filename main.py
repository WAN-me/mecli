from threading import Thread
import getch
from jsondb import Db
import sys,os

from classes import ctrl, Session
from classes import stdin, method


os.system("")  # enables ansi escape characters in terminal




cache = Db("cache.json")

def Handler():
    
    key = handler()
    if key in [ctrl.c,ctrl.d]: 
        exit()
    elif key == ctrl.x:
        cache.data['chat'] = session.choseChat()
        session.printdialog(cache.data['chat']['id'])
    elif key == ctrl.s:
        s = stdin("> ")
        sys.stdout.write(f"\033[F{' '*(len(s)+2)}\n\033[F")
        session.sendmsg(s,cache.data['chat']['id'])




def auth():
    params = {
    "login": stdin("Введите почту> "),
    "password": stdin("Введите пароль> ",is_password=True)
    }
    return method("users.auth",params)


def reg():
    params={
        "name": stdin("Введите имя пользователя> "),
        "email": stdin("Введите почту> "),
        "password": stdin("Введите пароль> ",is_password=True)
    }
    return method("users.reg",params)








session = Session('temp')
handler = getch.Getch()

def main():
    if "me" in cache.data:
        global session
        session = Session(cache.data['me']['token'])
        print(f"Привет, {cache.data['me']['name']}")
        Thread(target=session.poll).start()
        print('ctrl+x для выбора чата\nctrl+s для набора сообщения\n')
        while True:
            Handler()
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
                session = Session(res['token'])
                cache.data['me'] = {}
                cache.data['me'] = session('users.get')
                cache.data['me']['token'] = session.token
                cache.save()

            print("Авторизованно!")
            main()
        elif key in yes:
            print("Да")
            print(reg())
        else:
            print("Выход")
            exit()

main()