##########################################################################
# Name: fetch_liked_tweets.py
#
# Fetch selected user liked tweets.
#
# Usage: python3 fetch_liked_tweets.py -i <user_id>
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

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i","--userid",help="userid",type=str)
    p = parser.parse_args()
    args = {"userid":p.userid}
    return args


def load_bearer_token():
    return os.getenv("BEARER_TOKEN")


def create_url(user_id):
    url = "https://api.twitter.com/2/users/{}/liked_tweets".format(user_id)
    return url


def create_params():
    return {"tweet.fields":"lang,author_id",
            "max_results": "100"}


def create_headers(bearer_token):
    headers = {"Authorization": "Bearer {}".format(bearer_token),
               "User-Agent": select_user_agent()}
    return headers


def select_user_agent():
    user_agents = []
    user_agents.append("Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0) Opera 12.14")
    user_agents.append("Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:26.0) Gecko/20100101 Firefox/26.0")
    user_agents.append("Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.1.3) Gecko/20090913 Firefox/3.5.3")
    user_agents.append("Mozilla/5.0 (Windows; U; Windows NT 6.1; en; rv:1.9.1.3) Gecko/20090824 Firefox/3.5.3 (.NET CLR 3.5.30729)")
    user_agents.append("Mozilla/5.0 (Windows NT 6.2) AppleWebKit/535.7 (KHTML, like Gecko) Comodo_Dragon/16.1.1.0 Chrome/16.0.912.63 Safari/535.7")
    user_agents.append("Mozilla/5.0 (Windows; U; Windows NT 5.2; en-US; rv:1.9.1.3) Gecko/20090824 Firefox/3.5.3 (.NET CLR 3.5.30729)")
    user_agents.append("Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.1) Gecko/20090718 Firefox/3.5.1")
    random_user_agent = random.choice(user_agents)
    return(random_user_agent)


def save_file(liked_tweets_json,user_id):
    save_file = (user_id + '_' + 'liked_tweets.csv')
    with open(save_file,mode="a") as f:
        [f.write("{0},{1},{2},https://twitter.com/{2}/status/{1}".format(j['text'],j['id'],j['author_id'])) for i in liked_tweets_json for j in i]


def fetch_liked_tweets(url,payload,headers):
    cnt = 0
    while True:
        liked_tweets_json = []
        response = requests.get(url,
                                params=payload,headers=headers)
        if response.status_code == 429:
            time.sleep(60*15)
            fetch_liked_tweets(url,payload,headers)
        json_res = response.json()

        if response.status_code != 200:
            raise Exception(
                "Request returned an error: {} {}".format(
                    response.status_code, response.text
                )
            )

        try:
            liked_tweets_json.append(json_res['data'])
            save_file(liked_tweets_json,user_id)
        except KeyError:
            print("=====DONE=====")
            break

        if 'next_token' in json_res['meta']:
            payload.update(pagination_token=json_res['meta']['next_token'])

        else: break

    return None


def main():
    args = parse_args()
    global user_id
    user_id = args['userid']

    bearer_token = load_bearer_token()
    url = create_url(user_id)
    payload = create_params()
    headers = create_headers(bearer_token)

    fetch_liked_tweets(url,payload,headers)
    return None


if __name__ == "__main__":
    main()
