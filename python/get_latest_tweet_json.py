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
    existing_ids = set()
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

        # 新規ツイートのみ追加
        new_tweets = [t for t in tweets if t.id not in existing_ids]
        if not new_tweets:
            break

        all_tweets.extend(new_tweets)
        for t in new_tweets:
            existing_ids.add(t.id)

        # ページングカーソル更新
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
    tweets = await fetch_all_tweets(client, user.id)

    # 新しい順にソート（最新が上）
    sorted_tweets = sorted(tweets, key=parse_created_at, reverse=True)

    all_data = []
    for t in sorted_tweets:
        dt = parse_created_at(t)
        created_str = dt.strftime("%Y/%m/%d")

        data = {
            "username": USERNAME,
            "tweet_id": t.id,
            "text": t.text,
            "created_at": created_str,
            "url": f"https://twitter.com/{USERNAME}/status/{t.id}",
            "likes": getattr(t, "favorite_count", 0),
            "retweets": getattr(t, "retweet_count", 0)
        }
        all_data.append(data)

    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=4)

    print(f"{len(sorted_tweets)} 件のツイートを処理しました。")

asyncio.run(main())