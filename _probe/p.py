import json, subprocess, sys
sys.path.insert(0, '_source/matches')
import fetch_matches as f
for n in ['El Merriekh Bentiu', 'Pyramids FC', 'Sidama Coffee', 'Zamalek', 'Al Hilal Omdurman', 'APR FC']:
    print('wiki', n, '->', f.wiki_logo(n))
subprocess.run(['python3', '_source/matches/fetch_matches.py'], check=True)
import exact_channels
print(open('assets/data/logos.json').read())
