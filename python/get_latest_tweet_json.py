import asyncio
import json
import os
from datetime import datetime
from twikit import Client

USERNAME = "MiracleGoldSP"
JSON_FILE = "tweets.json"
BATCH_SIZE = 100
SLEEP_SECONDS = 0.1

async def fetch_all_tweets(client, user_id, existing_ids):
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

        # 未取得ツイートのみ
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

async def main():
    client = Client('ja')
    client.load_cookies('cookies.json')
    user = await client.get_user_by_screen_name(USERNAME)

    # JSON読み込み
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            all_data = json.load(f)
        existing_ids = set(t["tweet_id"] for t in all_data)
    else:
        all_data = []
        existing_ids = set()

    print("ツイート取得開始...")
    new_tweets = await fetch_all_tweets(client, user.id, existing_ids)

    # 新しい順にソート（最新が先頭）
    def parse_created_at(t):
        if isinstance(t.created_at, str):
            return datetime.strptime(t.created_at, "%a %b %d %H:%M:%S %z %Y")
        else:
            return t.created_at

    sorted_tweets = sorted(new_tweets, key=parse_created_at, reverse=True)

    # JSONに追加（最新順）
    for t in sorted_tweets:
        dt = parse_created_at(t)
        created_str = dt.strftime("%Y/%m/%d")  # YYYY/MM/DD形式
        data = {
            "username": USERNAME,
            "tweet_id": t.id,
            "text": t.text,
            "created_at": created_str,
            "url": f"https://twitter.com/{USERNAME}/status/{t.id}"
        }
        all_data.append(data)  # 末尾追加で最新ツイートが上に来る

    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=4)

    print(f"{len(new_tweets)} 件のツイートを処理しました。")

asyncio.run(main())
