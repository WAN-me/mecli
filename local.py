import sbeaver
import threading
import main
import contextlib
from classes import print
import sys
server = sbeaver.Server(address='localhost', port=7239, sync=False, silence=True)
global session
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
th = threading.Thread(target=server.start, daemon=True)
with open('help.txt', 'w') as f:
    with contextlib.redirect_stdout(f):
        th.start()

main.main()