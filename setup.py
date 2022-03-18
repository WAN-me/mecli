import os
os.system("pip3 install prompt_toolkit requests")
if os.name != "posix":
    os.system("pip3 install colorama")
