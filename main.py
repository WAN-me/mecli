from threading import Thread
import getch
from jsondb import Db
import sys,os
from classes import ctrl, Session
from classes import stdin, method
if os.name != 'posix':
    import colorama
    colorama.init()

os.system("")  # костыль чтоб работали цвета

cache = Db("cache.json")

def Handler():
    key = handler()
    if key in [ctrl.d,ctrl.c]: 
        os._exit(1)
    elif key == ctrl.x:
        cache.data['chat'] = session.choseChat()
        session.printdialog(cache.data['chat']['id'])
    elif key == ctrl.s:
        session.write_msg = True
        s = session.ps.prompt()
        sys.stdout.write(f"\033[F{' '*(len(s)+2)}\n\033[F")
        session.write_msg = False
        Thread(target=session.sendmsg,args=(s,cache.data['chat']['id']))
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
    "email": stdin("Введите почту> ", default=ligin),
    "password": stdin("Введите пароль> ",is_password=True, default=passwd)
    }
    return method("account.auth",params)


def reg():
    params={
        "name": stdin("Введите имя пользователя> "),
        "email": stdin("Введите почту> "),
        "password": stdin("Введите пароль> ",is_password=True)
    }
    return (method("account.reg",params),params)

session = Session('temp',cache)
handler = getch.Getch()

def main():
    if "me" in cache.data:
        global session
        session = Session(cache.data['me']['token'],cache)
        print(f"Привет, {cache.data['me']['name']} (id{cache.data['me']['id']})")
        session.startpool()
        print('ctrl+x для выбора чата\nctrl+s для набора сообщения\nctrl+n для открытия диалога\nctrl+d или ctrl+c для выхода\n')
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
            else: 
                print(res)
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