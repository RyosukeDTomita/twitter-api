# coding: utf-8
##########################################################################
# Name: monitor_timeline_per1min.py
#
# Using Twitter API fetch follower list.
#
# Usage: python3 monitor_timeline_per1min.py -i <user_id>
#
# Author: Ryosuke Tomita
# Date: 2021/08/26
##########################################################################
import argparse
import os
from os.path import abspath, join, dirname
import time
import random
import shutil
import requests


def parse_args():
    """set target user_id from stdin."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--userid", help="userid", type=str)
    p = parser.parse_args()
    args = {"userid": p.userid}
    return args


def load_bearer_token():
    """BEARER_TOKEN is exported by .bashrc"""
    return os.getenv("BEARER_TOKEN")


def create_url(user_id, tweet_type):
    """create urls to use fetch nomal tweets and mention tweets."""
    if tweet_type == "mention":
        url = "https://api.twitter.com/2/users/{}/mentions".format(user_id)
    else:
        url = "https://api.twitter.com/2/users/{}/tweets".format(user_id)
    return url


def create_params():
    """max_results can be chose between 5~100"""
    return {"tweet.fields": "created_at", 'max_results': '5'}


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


def fetch_user_timeline(url, payload, headers):
    """If find not saved tweets(new tweets) save to file."""
    response = requests.get(url, params=payload, headers=headers)

    # When api rate limits, sleep.
    if response.status_code == 429:
        time.sleep(60)
        return fetch_user_timeline(url, payload, headers)

    json_res = response.json()

    # display requests error message.
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    return json_res['data']


def save_file(tweet_json, user_id):
    """save user tweet to csv."""
    save_file = (user_id + '_' + 'timeline_data.csv')
    with open(save_file, mode="a") as f:
        f.write("{0},{1},https://twitter.com/{2}/status/{0}\n".format(
            tweet_json['id'], tweet_json['text'], user_id))


def keep_monitoring(url, payload, headers, user_id):
    """continue to scanning target user timeline per 1min."""
    id_list = []
    while True:
        print("-----Scanning Target Tweet.-----")
        new_tweets_json = fetch_user_timeline(url, payload, headers)
        newTweetExist = False

        # If new tweets are exist,prind stdin and save to file.
        for tweet in new_tweets_json:
            if tweet['id'] not in id_list:
                id_list.append(tweet['id'])
                print("{}\n{}".format(tweet['text'],
                                      "="*shutil.get_terminal_size().columns))
                save_file(tweet, user_id)
                newTweetExist = True

        if not newTweetExist:
            print("-----No new Tweet------")

        print("-----Next Scan is 60s later.------")
        time.sleep(60)


def main():
    args = parse_args()
    user_id = args['userid']

    bearer_token = load_bearer_token()
    #tweet_type = "mention"
    tweet_type = "normal"
    url = create_url(user_id, tweet_type)
    payload = create_params()
    headers = create_headers(bearer_token)

    keep_monitoring(url, payload, headers, user_id)


if __name__ == "__main__":
    main()
