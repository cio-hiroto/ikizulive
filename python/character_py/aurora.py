import asyncio
import json
import os
from datetime import datetime
from twikit import Client

USERNAME = "Rollie_twinkle"
# 出力先ディレクトリ（絶対パスではなくスクリプト相対で指定）
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'character_json')
# ディレクトリがなければ作成
os.makedirs(OUTPUT_DIR, exist_ok=True)
# 出力ファイルパス
JSON_FILE = os.path.join(OUTPUT_DIR, 'aurora_tweets.json')
BATCH_SIZE = 100
SLEEP_SECONDS = 2

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
    # Load cookies.json located next to this script (robust against current working directory)
    cookie_path = os.path.join(os.path.dirname(__file__), 'cookies.json')
    client.load_cookies(cookie_path)
    user = await client.get_user_by_screen_name(USERNAME)

    print("ツイート取得開始...")
    fetched_tweets = await fetch_all_tweets(client, user.id)

    # 既存JSON読み込み
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            all_data = json.load(f)
    else:
        all_data = []

    tweet_dict = {t["tweet_id"]: t for t in all_data}

    added_count = 0
    updated_count = 0

    for t in fetched_tweets:
        dt = parse_created_at(t)
        # create combined date+time string (YYYY/MM/DD HH:MM:SS)
        created_str = dt.strftime("%Y/%m/%d %H:%M:%S")

        if t.id in tweet_dict:
            old_likes = tweet_dict[t.id]["likes"]
            old_retweets = tweet_dict[t.id]["retweets"]

            new_likes = getattr(t, "favorite_count", 0)
            new_retweets = getattr(t, "retweet_count", 0)

            if old_likes != new_likes or old_retweets != new_retweets:
                tweet_dict[t.id]["likes"] = new_likes
                tweet_dict[t.id]["retweets"] = new_retweets
                updated_count += 1
        else:
            tweet_dict[t.id] = {
                "username": USERNAME,
                "tweet_id": t.id,
                "text": t.text,
                "created_at": created_str,
                "url": f"https://twitter.com/{USERNAME}/status/{t.id}",
                "likes": getattr(t, "favorite_count", 0),
                "retweets": getattr(t, "retweet_count", 0)
            }
            added_count += 1

    # sort by created_at which may be either "YYYY/MM/DD HH:MM:SS" or older "YYYY/MM/DD"
    def _parse_created_field(s):
        try:
            return datetime.strptime(s, "%Y/%m/%d %H:%M:%S")
        except Exception:
            try:
                return datetime.strptime(s, "%Y/%m/%d")
            except Exception:
                return datetime.min

    all_data = sorted(tweet_dict.values(), key=lambda x: _parse_created_field(x.get("created_at", "")), reverse=True)

    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=4)

    # 分岐ごとの視覚的な出力
    if added_count > 0 and updated_count > 0:
        print(f"JSON書き出し完了 → 新規追加: {added_count} 件, いいね/リツイート更新: {updated_count} 件")
    elif added_count > 0:
        print(f"JSON書き出し完了 → 新規追加: {added_count} 件")
    elif updated_count > 0:
        print(f"JSON書き出し完了 → いいね/リツイート更新: {updated_count} 件")
    else:
        print("JSON書き出し完了 → 変更なし（既存データのみ）")

asyncio.run(main())