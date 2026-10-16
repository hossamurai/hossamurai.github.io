"""Data from the admin bot, baked into the pages (runs in GitHub Actions every 6 hours); the website also reads it live
from n8n (site-data) on every visit:
  - channels: match channel per league
  - prices:   plan prices parsed from the bot's price entries — the ONE place prices are set (the admin bot);
              the plan cards, the order form and the bot all use them. The numbers in content.py are only the fallback.
Nothing about customers is kept. If n8n can't be reached, the last good file is kept.

Also writes assets/data/fx.json: USD exchange rates for the "≈ 48 CAD" amounts, from the first source that answers
(open.er-api.com → fawazahmed0 currency-api on jsDelivr → its Cloudflare mirror). The website tries the same live
sources first and uses this file when they are all blocked or down.

Output: assets/data/bot.json (read by _source/pages.py at build time) and assets/data/fx.json.
"""
import json, os, sys, urllib.request
from datetime import datetime, timezone

URL = 'https://n8n.hossamservices.com/webhook/site-data'
OUT = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'data', 'bot.json')
FX_OUT = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'data', 'fx.json')
FX_SOURCES = [
    ('https://open.er-api.com/v6/latest/USD', lambda d: d.get('rates')),
    ('https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/usd.json', lambda d: {k.upper(): v for k, v in (d.get('usd') or {}).items()}),
    ('https://latest.currency-api.pages.dev/v1/currencies/usd.json', lambda d: {k.upper(): v for k, v in (d.get('usd') or {}).items()}),
]


def get_json(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (hossamservices.com build)', 'Accept': 'application/json'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def fx():
    """USD rates from the first source that gives sane numbers; the old file stays if none does."""
    for url, pick in FX_SOURCES:
        try:
            rates = pick(get_json(url)) or {}
            if 1 < float(rates.get('CAD', 0)) < 2 and 20 < float(rates.get('EGP', 0)) < 200:
                keep = {k: round(float(v), 6) for k, v in rates.items() if isinstance(v, (int, float)) and len(k) == 3 and v > 0}
                with open(FX_OUT, 'w', encoding='utf-8') as f:
                    json.dump({'src': url.split('/')[2], 't': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'), 'r': keep}, f, separators=(',', ':'))
                print('fx from', url.split('/')[2], len(keep), 'currencies')
                return
        except Exception as e:
            print('fx source failed', url, e, file=sys.stderr)
    print('fx: all sources failed, keeping the old file', file=sys.stderr)


def clean_prices(p):
    """Only plain numbers in a sane range, per plan and period (y1 / y2)."""
    out = {}
    for plan in ('basic', 'premium', 'xtv', 'marvel'):
        v = (p or {}).get(plan) or {}
        o = {k: v[k] for k in ('y1', 'y2') if isinstance(v.get(k), (int, float)) and 0 < v[k] < 100000}
        if o:
            out[plan] = o
    return out


def main():
    fx()
    old = {}
    try:
        with open(OUT, encoding='utf-8') as f:
            old = json.load(f)
    except Exception:
        pass
    try:
        d = get_json(URL)
    except Exception as e:
        print('site-data failed, keeping the old file:', e, file=sys.stderr)
        return
    out = {'channels': d['channels'] if isinstance(d.get('channels'), dict) else old.get('channels', {}),
           'prices': clean_prices(d.get('prices')) or old.get('prices', {})}
    if out == {k: old.get(k) for k in out}:
        print('no change')
        return
    out['updated'] = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print('wrote', len(out['channels']), 'channels,', len(out['prices']), 'plan prices')


if __name__ == '__main__':
    main()
