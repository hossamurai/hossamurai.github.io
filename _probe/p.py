import json, subprocess
subprocess.run(['python3', '_source/matches/fetch_matches.py'], check=True)
d = json.load(open('assets/data/matches.json'))
for e in d['events']:
    print(e['utc'][:16], '|', e['league']['en'], '|', e['home']['ar'], '-', e['away']['ar'], '|', (e.get('channel') or {}).get('en'), '| exact' if (e.get('channel') or {}).get('exact') else '')
