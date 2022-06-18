#!/usr/bin/python3
import requests
from voice import say
from classes import Session, Lp, COLOR
from jsondb import Db
import os
from pathlib import Path
import platform, os
    
def push(title, message):
    plt = platform.system()
    if plt == "Darwin":
        command = '''
        osascript -e 'display notification "{message}" with title "{title}"'
        '''
    elif plt == "Linux":
        command = f'''
        notify-send "{title}" "{message}"
        '''
    elif plt == "Windows":
        win10toast.ToastNotifier().show_toast(title, message)
        return
    else:
        return
    os.system(command)


def send_api(text):
    requests.post('http://localhost:7239/addmsg', {'text':text})

def check():
    try:
        res = requests.get('http://localhost:7239', timeout=1)
        print(res.json())
        return True
    except requests.exceptions.ConnectionError:
        return False

def main():
    cache = Db(f"{Path.home()}/.cache/mecli/cache.json")
    session = Session(cache.data['me']['token'],cache)
    lp = Lp(session)
    for event in lp.start():
        print(event)

        type = event["type"]
        try:
            if type == 1:
                username = session.userget(event['object']['from_id'])['name']
                text = str(event['object']['text']).replace('\n','\n\r')
                if not check:
                    push(f'Новое сообщение[{username}]', text)
                else:
                    if event['object']['from_id'] == session.cache.data['me']['id']:
                        send_api(f'{COLOR.BLUE}{text}{COLOR.ENDC}')
                    else: 
                        send_api(f"{COLOR.GREEN}{username}{COLOR.ENDC}: {text}\n\033[F")
                        say(text)
            elif type == 2:
                if check:
                    text = str(event['object']['text']).replace('\n','\n\r')
                    send_api(f'{COLOR.BLUE}{text}{COLOR.ENDC}')
            else:
                print(event)
        except Exception as e:
            print(e)
            print(e.with_traceback())

print(check())
main()


        