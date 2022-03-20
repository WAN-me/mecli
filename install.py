import os
os.system("pip3 install prompt_toolkit requests playsound alive_progress")
if os.name != "posix":
    os.system("pip3 install colorama")
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