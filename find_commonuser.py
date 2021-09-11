##########################################################################
# Name: find_commonuser.py
#
# Compare followers lists and find same user.
#
# Usage: python3 find_commonuser.py -f <csv>
#
# Author: Ryosuke Tomita
# Date: 2021/08/27
##########################################################################
import argparse
import pandas as pd


def parse_args():
    """set follower list created by fetch_follower_list.py multiply."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", help="set follower_data.csv",
                        action='append', type=str)
    p = parser.parse_args()
    args = p.file
    return args


def read_csv(csvfile):
    """read follower list created by fetch_follower_list.py"""
    df = pd.read_csv(csvfile, header=None, encoding="utf-8",
                     usecols=(0, 1, 2, 3), names=('name', 'id', 'username', 'link'))
    return df


def find_min_file(df_list):
    """compare followers list to find smallest file."""
    min_file_size = 0
    for df in df_list:
        if len(df) > min_file_size:
            min_df = df
    return min_df


def find_common_user(df_list, min_df):
    """compare follower list created by fetch_follower_list.py, find common user."""
    min_userid_set = set(min_df['id'])
    common_user_list = []

    for df in df_list:
        # avoid compare same followers list.
        if len(min_df['id']) == len(df['id']):
            continue

        # Judge common user, to use set() size(set cannot have same component.
        for i in range(len(df['id'])):
            min_userid_size_before = len(min_userid_set)
            min_userid_set.add(df['id'][i])
            if len(min_userid_set) == min_userid_size_before:
                common_user_list.append(
                    [df['name'][i], df['id'][i], df['username'][i]])
            # After judge, destory added componet.
            min_userid_set.remove(df['id'][i])

    common_user = pd.DataFrame(data=common_user_list,
                               index=None,
                               columns=['name', 'id', 'username'])
    return common_user


def save_file(common_user):
    """save common user data to csvfile."""
    common_user["link"] = ["https://twitter.com/intent/user?user_id={}"
                           .format(i) for i in common_user['id']]
    common_user.to_csv('common_user.csv',
                       columns=['name', 'id', 'username', 'link'],
                       index=False)


def main():
    files = parse_args()

    df_list = [read_csv(f) for f in files]
    min_df = find_min_file(df_list)

    common_user = find_common_user(df_list, min_df)

    save_file(common_user)


if __name__ == '__main__':
    main()
