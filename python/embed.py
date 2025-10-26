#!/usr/bin/env python3
"""
Extract today's items from json/merged_tweets.json and write them to
the same `json/` directory as `merged_tweets_YYYY-MM-DD.json`.

Usage:
  python embed.py

This script looks for date fields in each item using the keys
`created_at`, `date`, or `created` and compares the date portion to
today's date (local). If parsing fails for an item it will be skipped.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, date, timedelta
from typing import Any, List, Optional


def parse_date(value: Any) -> Optional[datetime]:
	"""Try to parse various date formats and return a datetime or None."""
	if value is None:
		return None
	if isinstance(value, datetime):
		return value
	s = str(value).strip()
	if not s:
		return None

	fmts = [
		"%Y/%m/%d",
		"%Y-%m-%d",
		"%Y/%m/%d %H:%M:%S",
		"%Y-%m-%d %H:%M:%S",
		"%Y-%m-%dT%H:%M:%S",
		"%Y-%m-%dT%H:%M:%S%z",
		"%Y-%m-%dT%H:%M:%S.%f%z",
		"%Y-%m-%dT%H:%M:%S.%f",
	]
	for f in fmts:
		try:
			return datetime.strptime(s, f)
		except Exception:
			continue

	# try fromisoformat as a last structured attempt
	try:
		return datetime.fromisoformat(s)
	except Exception:
		pass

	# can't parse
	return None


def load_items(path: str) -> List[Any]:
	with open(path, 'r', encoding='utf-8') as f:
		data = json.load(f)
	if isinstance(data, list):
		return data
	if isinstance(data, dict):
		# common container keys
		for key in ('tweets', 'data', 'items', 'list', 'results'):
			if key in data and isinstance(data[key], list):
				return data[key]
		# fallback: first list value
		lists = [v for v in data.values() if isinstance(v, list)]
		if lists:
			return lists[0]
	return [data]


def main() -> int:
	base_dir = os.path.dirname(__file__)
	input_path = os.path.normpath(os.path.join(base_dir, '..', 'json', 'merged_tweets.json'))

	if not os.path.isfile(input_path):
		print(f"Input file not found: {input_path}", file=sys.stderr)
		return 1

	try:
		items = load_items(input_path)
	except Exception as e:
		print(f"Failed to read/parse {input_path}: {e}", file=sys.stderr)
		return 2

	today = date.today()
	selected: List[Any] = []
	skipped = 0
	for it in items:
		dt = None
		if isinstance(it, dict):
			for k in ('created_at', 'date', 'created'):
				if k in it:
					dt = parse_date(it.get(k))
					break
		else:
			# non-dict items can't be matched by fields
			dt = None

		if dt is None:
			skipped += 1
			continue

		try:
			if dt.date() == today:
				selected.append(it)
		except Exception:
			skipped += 1
			continue

	# If no items found for today, select items with the latest date present in the JSON
	if len(selected) == 0:
		parsed: List[tuple[Any, datetime]] = []
		for it in items:
			dt = None
			if isinstance(it, dict):
				for k in ('created_at', 'date', 'created'):
					if k in it:
						dt = parse_date(it.get(k))
						break
			if dt is not None:
				parsed.append((it, dt))

		if parsed:
			# find the most recent datetime among parsed items
			latest_dt = max(dt for (_it, dt) in parsed)
			latest_date = latest_dt.date()
			selected_latest = [it for (it, dt) in parsed if dt.date() == latest_date]
			print(f"No items found for {today.isoformat()}, selecting latest date {latest_date.isoformat()} with {len(selected_latest)} items")
			selected = selected_latest
			# set `today` variable so output filename reflects the chosen date
			today = latest_date
	out_dir = os.path.dirname(input_path)
	# output to a stable filename used by the site
	out_name = "data.json"
	out_path = os.path.join(out_dir, out_name)

	try:
		with open(out_path, 'w', encoding='utf-8') as f:
			# add flag per item: 1 if item's date matches the output date, else 0 (reversed as requested)
			out_list = []
			for it in selected:
				if isinstance(it, dict):
					# remove any _source_file metadata if present
					if '_source_file' in it:
						del it['_source_file']
					# determine item's date
					dt = None
					for k in ('created_at', 'date', 'created'):
						if k in it:
							dt = parse_date(it.get(k))
							break
					# flag: 1 == match, 0 == not match
					flag = 0
					if dt is not None:
						try:
							if dt.date() == today:
								flag = 1
						except Exception:
							flag = 0
					# attach flag
					it['flag'] = flag
				out_list.append(it)
			json.dump(out_list, f, ensure_ascii=False, indent=2)
	except Exception as e:
		print(f"Failed to write output {out_path}: {e}", file=sys.stderr)
		return 3

	print(f"Read {len(items)} items from {input_path}")
	print(f"Selected {len(selected)} items for {today.isoformat()} (skipped {skipped} unparseable)")
	print(f"Wrote {out_path}")
	return 0


if __name__ == '__main__':
	raise SystemExit(main())
