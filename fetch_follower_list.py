# coding: utf-8
##########################################################################
# Name: fetch_followerList.py
#
# Using Twitter API fetch follower list.
#
# Usage: python3 fetch_followerList.py -i 920511017683247104
#
# Author: Ryosuke Tomita
# Date: 2021/08/26
##########################################################################
import argparse
import os
from os.path import abspath, dirname, join
import random
import shutil
import time
import requests


def parse_args():
    """set user_id from stdin."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--userid", help="userid", type=str)
    p = parser.parse_args()
    args = {"userid": p.userid}
    return args


def load_bearer_token():
    """BEARER_TOKEN is exported by .bashrc"""
    return os.getenv("BEARER_TOKEN")


def create_url(user_id):
    """concat user_id to create url."""
    return "https://api.twitter.com/2/users/{}/followers".format(user_id)


def create_params():
    return {"user.fields": "created_at",
            "max_results": "1000"}


def create_headers(bearer_token):
    headers = {"Authorization": "Bearer {}".format(bearer_token),
               "User-Agent": random_user_agent()}
    return headers


def random_user_agent():
    """pick user_agent from useragents.txt randomly."""
    user_agent_file = join(abspath(dirname(__file__)) + "/useragents.txt")

    with open(user_agent_file, mode="r") as f:
        user_agent_list = [i.rstrip() for i in f.readlines()]
        user_agent = random.choice(user_agent_list)
    return user_agent


def display_requests_error(response):
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )


def fetch_followers_count(headers, user_id):
    """To dislpay progress bar, fetch user's the number of followers."""
    params = {"user_id": user_id}
    url = 'https://api.twitter.com/1.1/users/show.json'
    response = requests.get(url, params=params, headers=headers,
                            timeout=3)
    display_requests_error(response)

    followers_count = response.json()['followers_count']
    screen_name = response.json()['screen_name']
    print("{} has {} followers.".format(screen_name, followers_count))
    return followers_count


def show_progress(max_data_size, fetched_data_size):
    """display progress bar and left time."""
    terminal_size = shutil.get_terminal_size().columns
    max_bar_length = terminal_size - 12

    bar, dot = "#", "."
    progressed_percent = fetched_data_size/max_data_size
    bar_cnt = int(max_bar_length * progressed_percent)
    dot_cnt = max_bar_length - bar_cnt
    wait_time = int((1-progressed_percent)*max_data_size/15000)*15

    print("LEFT TIME IS {:.0f} min.    {}/{}"
          .format(wait_time, fetched_data_size, max_data_size))
    print('\033[32m', bar*bar_cnt + dot * dot_cnt,
          '\033[0m', end="")
    print('\033[31m', '[{:>5.1f}%]'.format(progressed_percent*100),
          '\033[0m')


def save_file(followers_json, user_id):
    """save to csvfile. csvfile name contains target user_id"""
    csv_file = (user_id + '_' + 'followers_data.csv')
    with open(csv_file, mode="a") as f:
        [f.write("{0}, {1}, {2}, https://twitter.com/intent/user?user_id={1}\n".format(j['name'].replace(',', ''), j['id'], j['username'])) for i in followers_json for j in i]


def fetch_followers_data(url, payload, headers,
                         followers_count, user_id, fetched_followers):
    """fetch user's all followers data. Data can be fetched 15000 per 15min."""
    while True:
        followers_json = []
        response = requests.get(url,
                                params=payload, headers=headers)

        # When api rate limits, sleep 15min and see progress bar.
        if response.status_code == 429:
            fetched_followers += 15000
            show_progress(followers_count, fetched_followers)
            time.sleep(60*15)
            return fetch_followers_data(url, payload, headers,
                    followers_count, user_id, fetched_followers)
        display_requests_error(response)

        json_res = response.json()
        try:
            followers_json.append((json_res['data']))
            save_file(followers_json, user_id)
        except KeyError: break

        # Remaining data is exist,update payload, request again
        if 'next_token' in json_res['meta']:
            payload.update(pagination_token=json_res['meta']['next_token'])
        else: break


def main():
    args = parse_args()
    user_id = args['userid']

    bearer_token = load_bearer_token()
    url = create_url(user_id)
    payload = create_params()
    headers = create_headers(bearer_token)

    followers_count = fetch_followers_count(headers, user_id)
    fetch_followers_data(url, payload, headers, followers_count, user_id,
                         fetched_followers=0)


if __name__ == "__main__":
    main()