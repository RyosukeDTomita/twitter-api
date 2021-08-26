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
import requests
import os
import json
import time
import random
import argparse
import shutil

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i","--userid",help="userid",type=str)
    p = parser.parse_args()
    args = {"userid":p.userid}
    return args


def load_bearer_token():
    return os.getenv("BEARER_TOKEN")


def create_url(user_id):
    return "https://api.twitter.com/2/users/{}/tweets".format(user_id)


def create_params():
    return {"tweet.fields": "created_at",'max_results': '5'} #max_results=5~100


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
    response = requests.get(url,params=payload,headers=headers)
    json_res = response.json()

    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    return json_res['data']


def save_file(tweet_json):
    save_file = (user_id + '_' + 'timeline_data.csv')
    with open(save_file,mode="a") as f: #"a"でテキストの追記
        f.write("{},{}\n".format(tweet_json['id'],tweet_json['text']))


def keep_monitoring(url,payload,headers):
    id_list = []
    while True:
        print("-----Scanning Target Tweet.-----")
        new_tweets_json = fetch_user_timeline(url,payload,headers)
        newTweetExist = False

        for t in new_tweets_json:
            if t['id'] not in id_list:
                id_list.append(t['id'])
                print("{}\n{}".format(t['text'],
                          "="*shutil.get_terminal_size().columns))
                save_file(t)
                newTweetExist = True

        if not newTweetExist: print("-----No new Tweet------")

        print("-----Next Scan is 60s later.------")
        time.sleep(60)

def main():
    args = parse_args()
    global user_id
    user_id = args['userid']

    bearer_token = load_bearer_token()
    url = create_url(user_id)
    payload = create_params()
    headers = create_headers(bearer_token)

    keep_monitoring(url,payload,headers)



if __name__ == "__main__":
    main()
