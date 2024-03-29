# coding: utf-8
"""
Name: fetch_follower_icon.py

Using Twitter API fetch followers icon. FollowersList is able to set from argument.

Usage:

Author: Ryosuke Tomita
Date: 2021/08/26
"""
import argparse
import os
from os.path import join, abspath, dirname
import shutil
import time
import pandas as pd
import requests


def parse_args():
    """set user_id from stdin."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file",
                        help="set FollowersList.csv", type=str)
    p = parser.parse_args()
    args = {"file": p.file}
    return args


def load_bearer_token():
    """BEARER_TOKEN is exported by .bashrc"""
    return os.getenv("BEARER_TOKEN")


def read_csv(csvfile):
    """read followers_data created by fetch_follower_list.py"""
    df = pd.read_csv(csvfile, header=0, encoding="utf-8",
                     usecols=(0, 1, 2),
                     names=('name', 'id', 'username'))

    # avoid user_id is interpreted in exponantial.
    with open(csvfile, mode='r') as f:
        user_id_list = []
        for i in range(len(df)):
            user_id_list.append(f.readline().split(',')[1])

    df['id'] = user_id_list
    return df


def create_params(user_id):
    """user_id is exported by .bashrc."""
    return {"user_id": user_id,
            "include_entities": "false"}


def create_headers(bearer_token):
    """bearer_token is exported by .bashrc."""
    headers = {"authorization": "Bearer {}".format(bearer_token)}
    return headers


def show_progress(max_data_size, fetched_data_size):
    """display progress bar and left time."""
    terminal_size = shutil.get_terminal_size().columns
    max_bar_length = terminal_size - 12

    bar, dot = "#", "."
    progressed_percent = fetched_data_size/max_data_size
    bar_cnt = int(max_bar_length * progressed_percent)
    dot_cnt = max_bar_length - bar_cnt
    wait_time = int((1-progressed_percent)*max_data_size/300)*15

    print("LEFT TIME IS {:.0f} min.    {}/{}"
          .format(wait_time, fetched_data_size, max_data_size))
    print('\033[32m', bar*bar_cnt + dot * dot_cnt,
          '\033[0m', end="")
    print('\033[31m', '[{:>5.1f}%]'.format(progressed_percent*100),
          '\033[0m')


def fetch_followers_data(url, payload, headers, df_length, i):
    """fetch user data to get user's icon url."""
    response = requests.get(url, params=payload, headers=headers,
                            timeout=3)

    # When api rate limits, sleep 15min and see progress bar.
    if response.status_code == 429:
        show_progress(df_length, i)
        time.sleep(60*15)
        return fetch_followers_data(url, payload, headers, df_length, i)
    json_res = response.json()

    # When response eroor occure, display error message.
    if response.status_code != 200:
        print("Request returned an error: {} {}".format(
              response.status_code, response.text))

    return json_res


def img_dl(icon_src, userid):
    """From user's icon url, download image."""
    img = requests.get(icon_src).content
    img_name = str(userid)
    dir_path = join(abspath(dirname(__file__)) + "/icon/")
    with open((dir_path + img_name), "wb") as f:
        f.write(img)


def main():
    """
    1. Get csvfile path from stdin.
    2. Read csvfile as DataFrame.
    3. Create url, bearer_token, headers.
    4. Check csvfile length to know the number of download icons.
    5. Download user's icons.
    """
    args = parse_args()

    csv_file = args['file']
    df = read_csv(csv_file)

    url = 'https://api.twitter.com/1.1/users/show.json'
    bearer_token = load_bearer_token()
    headers = create_headers(bearer_token)

    df_length = len(df['id'])  # data size.

    # download icon jpg file.
    for i, user_id in enumerate(df['id']):
        if not user_id:
            continue
        print(user_id)
        payload = create_params(user_id)
        user_object_json = fetch_followers_data(url, payload,
                                            headers, df_length, i)
        try:
            icon_src = user_object_json['profile_image_url']
            if not icon_src:
                continue
        except KeyError:
            continue

        img_dl(icon_src, df['id'][i])


if __name__ == "__main__":
    main()
