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
import json
import random
import argparse
import time
import pandas as pd

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
                     usecols=(0,1,2),names=('name','id','username'))
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
    response = requests.get(url,params=payload,headers=headers)
    json_res = response.json()

    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    return json_res


def main():
    #args = parse_args()

    bearer_token = load_bearer_token()

    #csv_file = args['file']
    #df = read_csv(csv_file)

    headers = create_headers(bearer_token)

    user_id = 1283398760156893184
    url = 'https://api.twitter.com/1.1/users/show.json'
    payload = create_params(user_id)
    user_object_json = fetch_followers_data(url,payload,headers)
    print(user_object_json['profile_image_url'])



if __name__ == "__main__":
    main()
