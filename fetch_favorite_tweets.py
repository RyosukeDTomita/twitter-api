# coding: utf-8
##########################################################################
# Name: fetch_favorite_tweets.py
#
# Fetch selected user favorite tweets.
#
# Usage: python3 fetch_favorite_tweets.py -i <user_id>
#
# Author: Ryosuke Tomita
# Date: 2021/08/26
#########################################################################
import argparse
import os
from os.path import abspath, dirname, join
import sys
import random
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
    url = "https://api.twitter.com/2/users/{}/liked_tweets".format(user_id)
    return url


def create_params():
    """max_results max =100"""
    return {"tweet.fields": "lang,author_id",
            "max_results": "100"}


def random_user_agent():
    """pick user_agent from useragents.txt randomly."""
    user_agent_file = join(abspath(dirname(__file__)) + "/useragents.txt")

    with open(user_agent_file, mode="r") as f:
        user_agent_list = [i.rstrip() for i in f.readlines()]
        user_agent = random.choice(user_agent_list)
    return user_agent


def create_headers(bearer_token):
    headers = {"Authorization": "Bearer {}".format(bearer_token),
               "User-Agent": random_user_agent()}
    return headers


def display_requests_error(response):
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )


def fetch_favourites_count(headers, user_id):
    """display progress bar,fetch the number of favorited tweet"""
    params = {"user_id": user_id}
    url = 'https://api.twitter.com/1.1/users/show.json'
    response = requests.get(url, params=params, headers=headers,
                            timeout=3)
    display_requests_error(response)

    try:
        favourites_count = response.json()['favourites_count']
        screen_name = response.json()['screen_name']
    except KeyError:
        print(response.status_code)
        sys.exit()

    print("{} has {} favourites tweets.".format(screen_name, favourites_count))
    return favourites_count


def show_progress(max_data_size, fetched_data_size):
    """show left time and progress bar."""
    terminal_size = shutil.get_terminal_size().columns
    max_bar_length = terminal_size - 12

    bar, dot = "#", "."
    progressed_percent = fetched_data_size/max_data_size
    bar_cnt = int(max_bar_length * progressed_percent)
    dot_cnt = max_bar_length - bar_cnt
    wait_time = int((1-progressed_percent)*max_data_size/1500)*15

    print("LEFT TIME IS {:.0f} min.    {}/{}"
          .format(wait_time, fetched_data_size, max_data_size))
    print('\033[32m', bar*bar_cnt + dot * dot_cnt,
          '\033[0m', end="")
    print('\033[31m', '[{:>5.1f}%]'.format(progressed_percent*100),
          '\033[0m')


def save_file(favourites_tweets_json, user_id):
    """save favorited tweet data to csv."""
    csv_file = (user_id + '_' + 'favourites_tweets.csv')
    with open(csv_file, mode="a") as f:
        [f.write("{0},{1},{2},https://twitter.com/{2}/status/{1}".format(j['text'], j['id'],j['author_id'])) for i in favourites_tweets_json for j in i]


def fetch_liked_tweets(url, payload, headers, favourites_count,
                       user_id, fetched_favourites_count):
    """fetch user's all favorited tweets. Tweets can be fetched 1500 par 15 min."""
    while True:
        favourites_tweets_json = []
        response = requests.get(url,
                                params=payload, headers=headers)

        # When api rate limits, sleep 15min and see progress bar.
        if response.status_code == 429:
            fetched_favourites_count += 1500
            show_progress(favourites_count, fetched_favourites_count)
            time.sleep(60*15)
            return fetch_liked_tweets(url, payload, headers,
                                      favourites_count, user_id, fetched_favourites_count)

        display_requests_error(response)
        json_res = response.json()

        try:
            favourites_tweets_json.append(json_res['data'])
            save_file(favourites_tweets_json, user_id)
        except KeyError:
            print("=====DONE=====")
            break

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

    favourites_count = fetch_favourites_count(headers, user_id)

    fetch_liked_tweets(url, payload, headers,
                       favourites_count, user_id, fetched_favourites_count=0)


if __name__ == "__main__":
    main()
