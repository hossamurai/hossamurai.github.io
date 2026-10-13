import json, subprocess
subprocess.run(['python3', '_source/matches/fetch_matches.py'], check=True)
d = json.load(open('assets/data/matches.json'))
for e in d['events'] + d['results']:
    for k in ('home', 'away'):
        if e['code'].startswith('caf') or not e[k].get('logo'): print(e[k]['en'], '->', e[k].get('logo'))
print(open('assets/data/logos.json').read()[:1500])
