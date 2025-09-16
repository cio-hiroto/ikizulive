import asyncio
import json
import os
from datetime import datetime
from twikit import Client

USERNAME = "MiracleGoldSP"
JSON_FILE = "tweets.json"
BATCH_SIZE = 100
SLEEP_SECONDS = 0.1

async def fetch_all_tweets(client, user_id):
    all_tweets = []
    cursor = None

    while True:
        tweets_response = await client.get_user_tweets(
            user_id,
            tweet_type="tweets",
            count=BATCH_SIZE,
            cursor=cursor
        )

        tweets = tweets_response if isinstance(tweets_response, list) else list(tweets_response)
        if not tweets:
            break

        all_tweets.extend(tweets)

        cursor = getattr(tweets_response, "next_cursor", None)
        if cursor is None:
            break

        await asyncio.sleep(SLEEP_SECONDS)

    return all_tweets

def parse_created_at(t):
    if isinstance(t.created_at, str):
        return datetime.strptime(t.created_at, "%a %b %d %H:%M:%S %z %Y")
    else:
        return t.created_at

async def main():
    client = Client('ja')
    client.load_cookies('cookies.json')
    user = await client.get_user_by_screen_name(USERNAME)

    print("ツイート取得開始...")
    fetched_tweets = await fetch_all_tweets(client, user.id)

    # 既存JSON読み込み
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            all_data = json.load(f)
    else:
        all_data = []

    # IDをキーに辞書化
    tweet_dict = {t["tweet_id"]: t for t in all_data}

    for t in fetched_tweets:
        dt = parse_created_at(t)
        created_str = dt.strftime("%Y/%m/%d")

        if t.id in tweet_dict:
            # 既存ツイートなら likes/retweetsのみ更新
            tweet_dict[t.id]["likes"] = getattr(t, "favorite_count", 0)
            tweet_dict[t.id]["retweets"] = getattr(t, "retweet_count", 0)
        else:
            # 新規ツイートなら追加
            tweet_dict[t.id] = {
                "username": USERNAME,
                "tweet_id": t.id,
                "text": t.text,
                "created_at": created_str,
                "url": f"https://twitter.com/{USERNAME}/status/{t.id}",
                "likes": getattr(t, "favorite_count", 0),
                "retweets": getattr(t, "retweet_count", 0)
            }

    # JSONに書き出し（最新順）
    all_data = sorted(tweet_dict.values(), key=lambda x: datetime.strptime(x["created_at"], "%Y/%m/%d"), reverse=True)
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=4)

    print(f"{len(all_data)} 件のツイートを処理しました。")

asyncio.run(main())
