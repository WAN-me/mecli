import os
import platform
import pip
from pathlib import Path
plt = platform.system()
pip.main("install prompt_toolkit sbeaver requests playsound==1.2.2 alive_progress".split())
if plt == "Windows":
    pip.main("install colorama win10toast".split())
if plt == "Linux":
    os.system("mkdir -p ~/.config/systemd/user/")
    os.system("mkdir -p ~/.cache/mecli/")
    os.system('mkdir -p ~/.local/lib/meclid')
    os.system("touch ~/.config/systemd/user/meclid.service")
    os.system(f'cp *.py {Path.home()}/.local/lib/meclid/')
    with open(f'{Path.home()}/.config/systemd/user/meclid.service', 'w') as f:
        f.write(f"""[Unit]
Description=meclid - daemon for wanilla cli messenger

[Service]
ExecStart={Path.home()}/.local/lib/meclid/daemon.py
Restart=always
WorkingDirectory={Path.home()}/.local/lib/meclid

[Install]
WantedBy=default.target
        """)
    os.system('systemctl --user daemon-reload')
    os.system('systemctl --user enable --now meclid.service')
    os.system('systemctl --user restart meclid.service')
import requests
import shutil
import zipfile
import os
from alive_progress import alive_bar
print('downloading..')
def download_file(url,filename = None):
    local_filename = filename or url.split('/')[-1]
    with requests.get(url, stream=True) as r:
        lenght = int(r.headers.get('Content-Length',1024))
        if lenght == 1024:
            lenght = len(r.content)
        print(f'need to get {lenght} bytes of data')
        with alive_bar(lenght,spinner_length=5,title="download main.zip") as bar:
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024):
                    f.write(chunk)
                    bar(len(chunk))
    return local_filename
download_file('https://github.com/WAN-me/mecli/archive/refs/heads/main.zip','main.zip')

with zipfile.ZipFile('main.zip', 'r') as zip_ref:
    zip_ref.extractall('tmp')
print('unzip succesful')

rootdir = 'tmp'+os.sep+'mecli-main'+os.sep
for root, dirs, files in os.walk(rootdir):
  for file in files:
    shutil.copy2(rootdir+file,file)
print('copy succesful')

shutil.rmtree('tmp')
os.remove('main.zip')

if __name__ == '__main__':
    import install
