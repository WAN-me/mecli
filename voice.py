from contextlib import redirect_stderr
import playsound
import asyncio
import queue
from threading import Thread
import os
from msspeech import MSSpeech
from pathlib import Path
import time

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

def say(text):
    fname = f'{int(time.time())}.mp3'
    mss_synthesize('Светлана', text, fname)
    playsound.playsound(fname, True)

if __name__ == "__main__":
    text = 'привет мир'
    say(text)
    
    