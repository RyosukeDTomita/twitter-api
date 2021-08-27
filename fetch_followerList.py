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
    return "https://api.twitter.com/2/users/{}/followers".format(user_id)


def create_params():
    return {"user.fields": "created_at",
            "max_results": "1000"}


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


def save_file(followers_json,user_id):
    save_file = (user_id + '_' + 'followers_data.csv')
    with open(save_file,mode="a") as f:
        [f.write("{},{},{}\n".format(j['name'],j['id'],j['username'])) for i in followers_json for j in i]


def fetch_followers_data(url,payload,headers):
    cnt = 0
    while True:
        followers_json = []
        response = requests.get(url,params=payload,headers=headers)
        json_res = response.json()

        if response.status_code != 200:
            raise Exception(
                "Request returned an error: {} {}".format(
                    response.status_code, response.text
                )
            )

        followers_json.append((json_res['data']))
        payload.update(pagination_token=json_res['meta']['next_token'])
        print(json_res['meta']['next_token'])
        save_file(followers_json,user_id)
        cnt += 1
        if cnt == 15:
            time.sleep(60*15)
            cnt = 0

    return followers_json



def main():
    args = parse_args()
    global user_id
    user_id = args['userid']

    bearer_token = load_bearer_token()
    url = create_url(user_id)
    payload = create_params()
    headers = create_headers(bearer_token)

    followers_json = fetch_followers_data(url,payload,headers)



if __name__ == "__main__":
    main()
