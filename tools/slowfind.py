"""Slow Commons finder: for each query, search, check licenses, keep free-licensed jpg/png candidates. Writes cand.json."""
import sys, json, time, urllib.request, urllib.parse, re
UA = {'User-Agent': 'DocResearch/1.0 (documentary image licensing check)'}
def api(**p):
    p['format'] = 'json'
    for a in range(8):
        try:
            r = urllib.request.urlopen(urllib.request.Request('https://commons.wikimedia.org/w/api.php?' + urllib.parse.urlencode(p), headers=UA), timeout=40).read()
            return json.loads(r)
        except Exception:
            time.sleep(45 * (a + 1))
    return None
qs = json.load(open(sys.argv[1])); out = {}
for q in qs:
    r = api(action='query', generator='search', gsrsearch=q, gsrnamespace=6, gsrlimit=12, prop='imageinfo', iiprop='extmetadata|size')
    time.sleep(25)
    if not r or 'query' not in r: out[q] = []; continue
    c = []
    for pg in r['query']['pages'].values():
        t = pg['title']
        if not re.search(r'\.(jpe?g|png)$', t, re.I): continue
        ii = pg.get('imageinfo', [{}])[0]; m = ii.get('extmetadata', {})
        lic = re.sub('<[^>]+>', '', m.get('LicenseShortName', {}).get('value', ''))
        art = re.sub('<[^>]+>', '', m.get('Artist', {}).get('value', ''))[:60]
        if not re.search(r'public domain|cc0|cc by|pd', lic, re.I): continue
        if ii.get('width', 0) < 700: continue
        c.append(dict(title=t, lic=lic, artist=art, w=ii.get('width'), h=ii.get('height')))
    out[q] = c
    json.dump(out, open(sys.argv[2], 'w'), ensure_ascii=False, indent=1)
    print(q, len(c), flush=True)
