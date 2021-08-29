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


def save_file(followers_json,user_id):
    save_file = (user_id + '_' + 'followers_data.csv')
    with open(save_file,mode="a") as f:
        [f.write("{},{},{}\n".format(j['name'],j['id'],j['username'])) for i in followers_json for j in i]


def fetch_followers_data(url,payload,headers):
    response = requests.get(url,params=payload,headers=headers,
                            timeout=3)
    json_res = response.json()
    if response.status_code != 200:
        print("Request returned an error: {} {}".format(
              response.status_code, response.text))

    return json_res


def img_dl(icon_scr,username,userid):
    img = requests.get(icon_scr).content
    imgName = (username + str(userid) + "jpg")
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

    for i,user_id in enumerate(df['id']):
        if not user_id: continue
        print(user_id)
        payload = create_params(user_id)
        user_object_json = fetch_followers_data(url,payload,headers)
        if i+1%300 == 0 and i != 0: time.sleep(60*15)
        try:
            icon_src = user_object_json['profile_image_url']
        except KeyError:
            continue

        img_dl(icon_src,df['username'][i],df['id'][i])


if __name__ == "__main__":
    main()
