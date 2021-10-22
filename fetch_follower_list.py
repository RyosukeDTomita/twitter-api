# coding: utf-8
"""
Name: fetch_followerList.py

Using Twitter API fetch follower list.

Usage: python3 fetch_followerList.py -i 920511017683247104

Author: Ryosuke Tomita
Date: 2021/08/26
"""
import argparse
import os
from os.path import abspath, dirname, join
import random
import shutil
import time
import requests


def parse_args() -> dict:
    """parse_args.
    set user_id from stdin.

    Args:

    Returns:
        dict:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--userid", help="userid", type=str)
    p = parser.parse_args()
    args = {"userid": p.userid}
    return args


def load_bearer_token() -> str:
    """load_bearer_token.
    BEARER_TOKEN is exported by .bashrc

    Args:

    Returns:
        str:
    """
    return os.getenv("BEARER_TOKEN")


def create_url(user_id: str) -> str:
    """create_url.
    concat user_id to create url.

    Args:
        user_id (str): user_id

    Returns:
        str:
    """
    return "https://api.twitter.com/2/users/{}/followers".format(user_id)


def create_params() -> dict:
    """create_params.
    max_results max == 1000

    Args:

    Returns:
        dict:
    """
    return {"user.fields": "created_at",
            "max_results": "1000"}


def create_headers(bearer_token: str) -> dict:
    """create_headers.
    create header. bearer_token is exported by .bashrc.

    Args:
        bearer_token (str): bearer_token

    Returns:
        dict:
    """
    headers = {"Authorization": "Bearer {}".format(bearer_token),
               "User-Agent": random_user_agent()}
    return headers


def random_user_agent() -> str:
    """random_user_agent.
    pick user_agent from useragents.txt randomly.

    Args:

    Returns:
        str:
    """
    user_agent_file = join(abspath(dirname(__file__)) + "/useragents.txt")

    with open(user_agent_file, mode="r") as f:
        user_agent_list = [i.rstrip() for i in f.readlines()]
        user_agent = random.choice(user_agent_list)
    return user_agent


def display_requests_error(response: requests.models.Response):
    """display_requests_error.

    Args:
        response (requests.models.Response): response
    """
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )


def fetch_followers_count(headers: dict, user_id: str) -> int:
    """fetch_followers_count.
    To dislpay progress bar, fetch user's the number of followers.

    Args:
        headers (dict): headers
        user_id (str): user_id

    Returns:
        int:
    """
    params = {"user_id": user_id}
    url = 'https://api.twitter.com/1.1/users/show.json'
    response = requests.get(url, params=params, headers=headers,
                            timeout=3)
    display_requests_error(response)

    followers_count = response.json()['followers_count']
    screen_name = response.json()['screen_name']
    print("{} has {} followers.".format(screen_name, followers_count))
    return followers_count


def show_progress(max_data_size: int, fetched_data_size: int):
    """show_progress.
    display progress bar and left time.

    Args:
        max_data_size (int): max_data_size
        fetched_data_size (int): fetched_data_size
    """
    terminal_size = shutil.get_terminal_size().columns
    max_bar_length = terminal_size - 12

    bar_, dot = "#", "."
    progressed_percent = fetched_data_size/max_data_size
    bar_cnt = int(max_bar_length * progressed_percent)
    dot_cnt = max_bar_length - bar_cnt
    wait_time = -(-(1-progressed_percent)*max_data_size//15000)*15

    print("LEFT TIME IS {:.0f} min.    {}/{}"
          .format(wait_time, fetched_data_size, max_data_size))
    print('\033[32m', bar_*bar_cnt + dot * dot_cnt,
          '\033[0m', end="")
    print('\033[31m', '[{:>5.1f}%]'.format(progressed_percent*100),
          '\033[0m')


def save_file(followers_json: list, user_id: str):
    """save_file.
    save to csvfile. csvfile name contains target user_id

    Args:
        followers_json (list): followers_json
        user_id (str): user_id
    """
    csv_file = (user_id + '_' + 'followers_data.csv')
    with open(csv_file, mode="a") as f:
        for i in followers_json:
            for j in i:
                f.write(
                    "{0}, {1}, {2}, https://twitter.com/intent/user?user_id={1}\n".format(
                        j['name'].replace(',', ''), j['id'], j['username']
            )
        )


def fetch_followers_data(url, payload, headers,
                         followers_count, user_id, fetched_followers):
    """fetch_followers_data.
    fetch user's all followers data. Data can be fetched 15000 per 15min.

    Args:
        url:
        payload:
        headers:
        followers_count:
        user_id:
        fetched_followers:
    """
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
        except KeyError:
            break

        # Remaining data is exist,update payload, request again
        if 'next_token' in json_res['meta']:
            payload.update(pagination_token=json_res['meta']['next_token'])
        else:
            break


def main():
    """main
    1. Get userid from stdin.
    2. Load token and create payload,url,header.
    3. Check target user's followers number.
    4. Fetch followers data.
    """
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
