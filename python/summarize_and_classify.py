import json
import requests
import time

# Hugging Face APIキー（無料登録で取得）
# https://huggingface.co/settings/tokens で発行
API_URL = "https://api-inference.huggingface.co/models/sonoisa/summarization-ja-bert-003"
API_KEY = "YOUR_HF_API_KEY"  # ←ここに自分のキーを入力
headers = {"Authorization": f"Bearer {API_KEY}"}

# ジャンル候補（必要に応じて調整）
GENRES = [
    "ニュース", "イベント", "お知らせ", "技術", "生活", "エンタメ", "スポーツ", "その他"
]

def summarize(text):
    response = requests.post(API_URL, headers=headers, json={"inputs": text})
    try:
        return response.json()[0]['summary_text']
    except Exception:
        return text[:50] + "..."  # 失敗時は冒頭50文字

def classify(text):
    # 簡易ジャンル分け（キーワード判定）
    text_lower = text.lower()
    if "技術" in text or "python" in text_lower or "api" in text_lower:
        return "技術"
    if "イベント" in text or "開催" in text or "参加" in text:
        return "イベント"
    if "お知らせ" in text or "告知" in text:
        return "お知らせ"
    if "スポーツ" in text or "試合" in text:
        return "スポーツ"
    if "映画" in text or "音楽" in text or "ライブ" in text:
        return "エンタメ"
    if "生活" in text or "日常" in text:
        return "生活"
    if "ニュース" in text or "速報" in text:
        return "ニュース"
    return "その他"

def main():
    with open('python/tweets.json', 'r', encoding='utf-8') as f:
        tweets = json.load(f)

    for tweet in tweets:
        text = tweet.get('text', '')
        if not text:
            continue
        summary = summarize(text)
        genre = classify(text)
        tweet['summary'] = summary
        tweet['genre'] = genre
        time.sleep(1)  # APIレート制限対策

    with open('python/tweets_with_summary.json', 'w', encoding='utf-8') as f:
        json.dump(tweets, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    main()
