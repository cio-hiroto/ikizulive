#!/usr/bin/env python3
"""
Merge all JSON files under python/character_py/character_json into one JSON file.

Output path: python/merged_tweets.json
The merged list is sorted by date (newest first) using the `created_at` field if present.
"""
import json
import os
from datetime import datetime
from typing import Any, List


INPUT_DIR = os.path.join(os.path.dirname(__file__), 'character_py', 'character_json')
# place merged output in the repo's top-level `json/` directory
OUTPUT_FILE = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'json', 'merged_tweets.json'))


def parse_date(value: Any) -> datetime:
    """Try to parse different date string formats. If fails, return minimal date."""
    if isinstance(value, datetime):
        return value
    if not value:
        return datetime.min
    s = str(value)
    # common formats used in this project
    fmts = [
        "%Y/%m/%d",
        "%Y-%m-%d",
        "%Y/%m/%d %H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S%z",
    ]
    for f in fmts:
        try:
            return datetime.strptime(s, f)
        except Exception:
            continue
    # try ISO fallback
    try:
        return datetime.fromisoformat(s)
    except Exception:
        pass
    # last resort: return minimal date so it's sorted to the end
    return datetime.min


def collect_json_files(input_dir: str) -> List[str]:
    if not os.path.isdir(input_dir):
        raise FileNotFoundError(f"Input directory not found: {input_dir}")
    files = []
    for name in os.listdir(input_dir):
        if name.lower().endswith('.json'):
            files.append(os.path.join(input_dir, name))
    files.sort()
    return files


def load_items_from_file(path: str) -> List[dict]:
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    # if the file contains a dict with a list under some key, try to find it
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        # common keys that may hold lists
        for key in ('tweets', 'data', 'items', 'list', 'results'):
            if key in data and isinstance(data[key], list):
                return data[key]
        # otherwise, attempt to extract list values
        lists = [v for v in data.values() if isinstance(v, list)]
        if lists:
            return lists[0]
    # fallback: wrap single object
    return [data]


def main():
    files = collect_json_files(INPUT_DIR)
    all_items = []
    for p in files:
        try:
            items = load_items_from_file(p)
            # annotate with source file (optional)
            # do not annotate source file; keep merged items as-is
            all_items.extend(items)
            print(f"Loaded {len(items)} items from {p}")
        except Exception as e:
            print(f"Failed to load {p}: {e}")

    # sort by created_at if present, newest first
    def sort_key(item: Any):
        if isinstance(item, dict):
            return parse_date(item.get('created_at') or item.get('date') or item.get('created'))
        return datetime.min

    all_items.sort(key=sort_key, reverse=True)

    # write output
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_items, f, ensure_ascii=False, indent=2)

    print(f"Merged {len(all_items)} items into {OUTPUT_FILE}")


if __name__ == '__main__':
    main()
