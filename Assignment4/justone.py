#!/usr/bin/python

import subprocess, os

def main():
    d = subprocess.Popen('git diff HEAD^..HEAD', cwd = os.getcwd(), shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    (out, error) = d.communicate()
    print(str(out))

if __name__ == "__main__":
    main()
