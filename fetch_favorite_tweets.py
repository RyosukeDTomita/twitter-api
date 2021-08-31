##########################################################################
# Name: fetch_favorite_tweets.py
#
# Fetch selected user favorite tweets.
#
# Usage: python3 fetch_favorite_tweets.py -i <user_id>
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


def display_requests_error(response):
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    return None


def fetch_favourites_count(headers):
    params = {"user_id":user_id}
    url = 'https://api.twitter.com/1.1/users/show.json'
    response = requests.get(url,params=params,headers=headers,
                            timeout=3)
    display_requests_error(response)

    try:
        favourites_count = response.json()['favourites_count']
        screen_name = response.json()['screen_name']
    except KeyError:
        print(response.status_code)
        exit()

    print("{} has {} favourites tweets.".format(screen_name,favourites_count))
    return favourites_count


def show_progress(max_data_size,fetched_data_size):
    terminal_size = shutil.get_terminal_size().columns
    max_bar_length = terminal_size - 12

    bar,dot = "#","."
    progressed_percent = fetched_data_size/max_data_size
    bar_cnt = int(max_bar_length * progressed_percent)
    dot_cnt = max_bar_length - bar_cnt
    wait_time = int((1-progressed_percent)*max_data_size/1500)*15

    print("LEFT TIME IS {:.0f} min.    {}/{}"
          .format(wait_time,fetched_data_size,max_data_size))
    print('\033[32m',bar*bar_cnt + dot * dot_cnt,
          '\033[0m',end="")
    print('\033[31m','[{:>5.1f}%]'.format(progressed_percent*100),
          '\033[0m')
    return None


def save_file(favourites_tweets_json,user_id):
    save_file = (user_id + '_' + 'favourites_tweets.csv')
    with open(save_file,mode="a") as f:
        [f.write("{0},{1},{2},https://twitter.com/{2}/status/{1}".format(j['text'],j['id'],j['author_id'])) for i in favourites_tweets_json for j in i]
    return None


def fetch_liked_tweets(url,payload,headers,favourites_count,fetched_favourites_count):
    while True:
        favourites_tweets_json = []
        response = requests.get(url,
                                params=payload,headers=headers)

        if response.status_code == 429:
            fetched_favourites_count += 1500
            show_progress(favourites_count,fetched_favourites_count)
            time.sleep(60*15)
            return fetch_favourites_tweets(url,payload,headers,favourites_count,fetched_favourites_count)

        display_requests_error(response)
        json_res = response.json()


        try:
            favourites_tweets_json.append(json_res['data'])
            save_file(favourites_tweets_json,user_id)
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

    favourites_count = fetch_favourites_count(headers)

    fetch_liked_tweets(url,payload,headers,favourites_count,fetched_favourites_count=0)
    return None


if __name__ == "__main__":
    main()
