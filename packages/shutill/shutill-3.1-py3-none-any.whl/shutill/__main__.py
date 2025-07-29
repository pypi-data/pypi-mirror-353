# shutill/__main__.py
import subprocess
import platform

def open_calc():
    if platform.system() == "Windows":
        subprocess.Popen("calc.exe")
    else:
        raise OSError("This package only works on Windows.")

if __name__ == "__main__":
    open_calc()