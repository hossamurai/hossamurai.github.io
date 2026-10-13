"""Match channels set from the admin bot, baked into the match and league pages for search engines
(runs in GitHub Actions every 6 hours). The website also reads them live from n8n (site-data) on every visit.

Only `channels` (match channel per league) is kept — nothing about customers. If n8n can't be reached, the last good file is kept.

Output: assets/data/bot.json  →  read by _source/pages.py at build time.
"""
import json, os, sys, urllib.request
from datetime import datetime, timezone

URL = 'https://n8n.hossamservices.com/webhook/site-data'
OUT = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'data', 'bot.json')


def main():
    old = {}
    try:
        with open(OUT, encoding='utf-8') as f:
            old = json.load(f)
    except Exception:
        pass
    try:
        req = urllib.request.Request(URL, headers={'User-Agent': 'Mozilla/5.0 (hossamservices.com build)', 'Accept': 'application/json'})
        with urllib.request.urlopen(req, timeout=30) as r:
            d = json.load(r)
    except Exception as e:
        print('site-data failed, keeping the old file:', e, file=sys.stderr)
        return
    out = {'channels': d['channels'] if isinstance(d.get('channels'), dict) else old.get('channels', {})}
    if out == {k: old.get(k) for k in out}:
        print('no change')
        return
    out['updated'] = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print('wrote', len(out['channels']), 'channels')


if __name__ == '__main__':
    main()
