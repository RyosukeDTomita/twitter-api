##########################################################################
# Name: monitor_timeline.py
#
# Using Twitter API fetch follower list.
#
# Usage: python3 test.py -i 920511017683247104
#
# Author: Ryosuke Tomita
# Date: 2021/08/26
##########################################################################
import requests
import os
import json
import time
import random
import argparse

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i","--userid",help="userid",type=str)
    p = parser.parse_args()
    args = {"userid":p.userid}
    return args


def load_bearer_token():
    return os.getenv("BEARER_TOKEN")


def create_url(user_id):
    url_tweets = "https://api.twitter.com/2/users/{}/tweets".format(user_id)
    url_mensions = "https://api.twitter.com/2/users/{}/mentions".format(user_id)
    return url_tweets,url_mensions


def create_params():
    return {"tweet.fields": "created_at",'max_results': '100'} #max_results=5~100


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


def fetch_user_timeline(url,payload,headers):
    timeline_json = []
    response = requests.get(url,params=payload,headers=headers)
    json_res = response.json()

    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    timeline_json.append(json_res['data'])
    return timeline_json


def save_file(followers_json,user_id):
    save_file = (user_id + '_' + 'timeline_data.csv')
    with open(save_file,mode="a") as f:
        [f.write("{0},{1},https://twitter.com/{2}/status/{0}\n".format(j['id'],j['text'],user_id)) for i in followers_json for j in i]


def main():
    args = parse_args()
    user_id = args['userid']

    bearer_token = load_bearer_token()
    url_tweets,url_mensions = create_url(user_id)
    payload = create_params()
    headers = create_headers(bearer_token)

    timeline_json = fetch_user_timeline(url_tweets,payload,headers)
    save_file(timeline_json,user_id)

    mentions_json = fetch_user_timeline(url_mensions,payload,headers)
    save_file(mentions_json,user_id)


if __name__ == "__main__":
    main()
