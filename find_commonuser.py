##########################################################################
# Name: find_commonuser.py
#
#
#
# Usage:
#
# Author: Ryosuke Tomita
# Date: 2021/08/27
##########################################################################
import pandas as pd
import numpy as np
import argparse

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f","--file",help="set follower_data.csv",
                        action='append',type=str)
    p = parser.parse_args()
    args = p.file
    return args


def read_csv(csvfile):
    df = pd.read_csv(csvfile,header=None,encoding="utf-8",
                     usecols=(0,1,2),names=('name','id','username'))
    return df


def find_min_file(df_list):
    min_file_size = 0
    for df in df_list:
        if len(df) > min_file_size:
            min_df = df
    return min_df

def find_common_user(df_list,min_df):
    min_userid_set = set(min_df['id'])
    common_user_list = []

    for df in df_list:
        if len(min_df['id']) == len(df['id']): continue
        for i in range(len(df['id'])):
            min_userid_size_before = len(min_userid_set)
            min_userid_set.add(df['id'][i])
            if len(min_userid_set) == min_userid_size_before:
                common_user_list.append([df['name'][i],df['id'][i],df['username'][i]])
                min_userid_set.remove(df['id'][i])
    common_user = pd.DataFrame(data=common_user_list,
                               index=None,
                               columns=['name','id','username'])
    return common_user


def save_file(common_user):
    common_user.to_csv('test.csv',columns=['name','id','username'],
                       index=False)
    return None


def main():
    files = parse_args()

    df_list = [read_csv(f) for f in files]
    min_df = find_min_file(df_list)

    common_user = find_common_user(df_list,min_df)

    save_file(common_user)
    return None


if __name__ == '__main__':
    main()