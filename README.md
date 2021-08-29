# INDEX
Using twitter api, get twitter data. 

- [ABOUT](#ABOUT)
- [ENVIRONMENT](#ABOUT)
- [PREPARING](#PREPARING)
- [HOW TO USE](#HOW TO USE)
- [REFERENCE(#REFERENCE)]

# ABOUT
These programs need twitter api BEARER_TOKEN.
If you don't have api token, please register from [here](https://developer.twitter.com/en/apps/)

# ENVIRONMENT
I used the following environment.
- Python3.8
- Ubuntu 20.04 LTS or MacOS Catalina

I think these program can run in windows.But, I didn't test it.

# PREPARING
1. Plase get your token from [your twitter developer page](https://developer.twitter.com/en/apps/)
2. Export your token to environment variables. Add these commands in bashrc.(You need to replace <TOKEN> for your token.)

```
export CONSUMER_KEY=<YOUR_CONSUMER>
export CONSUMER_SECRET=<YOUR_CONSUMER_SECRET>
export BEARER_TOKEN=<YOUR_BEARER_TOKEN>
```

# HOW TO USE
## fetching selected user's followers data and save to text file.

```shell
python3 fetch_followerList.py -i <user_id>
```

## fetching selected user's tweet to save to text file.

```shell
python3 fetch_timeline.py -i <user_id>
```

## monitoring selected user's tweet.
Scanning selected user's tweet per 1 minutes.
If found new tweet then save to text file.

```shell
python3 monitor_timeline_per1min.py -i <user_id>
```

## compare followerslist.csv and find common user.

```shell
python3 find_commonuser.py -f <csv1> -f <csv2>
```

## fetch followerlist.csv's icon image.

```shell
python3 fetch_follower_icon.py -f <csv>
```
******


# REFERENCE
- If you get rate-limit error(429),see [rate-limit](https://developer.twitter.com/en/docs/twitter-api/v1/rate-limits).
- [Developer terms](https://developer.twitter.com/en/developer-terms/more-on-restricted-use-cases)
