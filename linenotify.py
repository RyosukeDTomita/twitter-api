##########################################################################
# Name: linenotify.py
#
#
#
# Usage:
#
# Author: Ryosuke Tomita
# Date: 2021/08/27
##########################################################################
import os
from os.path import *
import requests

def load_token():
    return os.getenv("LINENOTIFY_ACCESSTOKEN")

def get_message(message):
    return message

def main():
    url = "https://notify-api.line.me/api/notify"
    token = load_token()

    headers = {"Authorization" : "Bearer "+ token}
    message =  'これはテストです'
    payload = {"message" :  message}
    png_path = abspath(join(dirname(__file__),"picture/twitter_bird.png"))
    print(png_path)
    files = {"imageFile": open(png_path, "rb")}

    r = requests.post(url ,headers = headers ,params=payload,files=files)


if __name__ == '__main__':
    main()

