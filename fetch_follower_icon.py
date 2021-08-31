##########################################################################
# Name: fetch_follower_icon.py
#
# Using Twitter API fetch followers icon. FollowersList is able to set from argument.
#
# Usage:
#
# Author: Ryosuke Tomita
# Date: 2021/08/26
##########################################################################
import requests
import os
from os.path import join,abspath,dirname
import json
import random
import argparse
import time
import pandas as pd
import numpy as np
import shutil

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f","--file",help="set FollowersList.csv",
                        type=str)
    p = parser.parse_args()
    args = {"file":p.file}
    return args


def load_bearer_token():
    return os.getenv("BEARER_TOKEN")


def read_csv(csvfile):
    df = pd.read_csv(csvfile,header=0,encoding="utf-8",
                     usecols=(0,1,2),
                     names=('name','id','username'))

    with open(csvfile,mode='r') as f:
        user_id_list = []
        for i in range(len(df)):
            user_id_list.append(f.readline().split(',')[1])

    df['id'] = user_id_list
    return df


def create_params(user_id):
    return {"user_id":user_id,
            "include_entities":"false"}


def create_headers(bearer_token):
    headers = {"authorization": "Bearer {}".format(bearer_token)}
    return headers


def show_progress(max_data_size,fetched_data_size):
    terminal_size = shutil.get_terminal_size().columns
    max_bar_length = terminal_size - 12

    bar,dot = "#","."
    progressed_percent = fetched_data_size/max_data_size
    bar_cnt = int(max_bar_length * progressed_percent)
    dot_cnt = max_bar_length - bar_cnt
    wait_time = int((1-progressed_percent)*max_data_size/300)*15

    print("LEFT TIME IS {:.0f} min.    {}/{}"
          .format(wait_time,fetched_data_size,max_data_size))
    print('\033[32m',bar*bar_cnt + dot * dot_cnt,
          '\033[0m',end="")
    print('\033[31m','[{:>5.1f}%]'.format(progressed_percent*100),
          '\033[0m')
    return None


def fetch_followers_data(url,payload,headers,df_length,i):
    response = requests.get(url,params=payload,headers=headers,
                            timeout=3)

    if response.status_code == 429:
        show_progress(df_length,i)
        time.sleep(60*15)
        return fetch_followers_data(url,payload,headers,df_length,i)
    json_res = response.json()

    if response.status_code != 200:
        print("Request returned an error: {} {}".format(
              response.status_code, response.text))

    return json_res


def img_dl(icon_src,userid):
    img = requests.get(icon_src).content
    imgName = str(userid)
    DIRPATH = join(abspath(dirname(__file__)) + "/icon/")
    with open((DIRPATH+imgName),"wb") as f:
        f.write(img)

def main():
    args = parse_args()

    csv_file = args['file']
    df = read_csv(csv_file)

    url = 'https://api.twitter.com/1.1/users/show.json'
    bearer_token = load_bearer_token()
    headers = create_headers(bearer_token)

    df_length = len(df['id'])

    for i,user_id in enumerate(df['id']):
        if not user_id: continue
        print(user_id)
        payload = create_params(user_id)
        user_object_json = fetch_followers_data(url,payload,
                                            headers,df_length,i)
        try:
            icon_src = user_object_json['profile_image_url']
            if not icon_src: continue
        except KeyError:
            continue


        img_dl(icon_src,df['id'][i])


if __name__ == "__main__":
    main()
