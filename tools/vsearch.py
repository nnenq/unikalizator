import sys, json, time, urllib.request, urllib.parse, re
UA = {'User-Agent': 'DocResearch/1.0 (documentary licensing check)'}
def api(**p):
    p['format'] = 'json'
    for a in range(6):
        try: return json.loads(urllib.request.urlopen(urllib.request.Request('https://commons.wikimedia.org/w/api.php?' + urllib.parse.urlencode(p), headers=UA), timeout=40).read())
        except Exception: time.sleep(40 * (a + 1))
out = {}
for q in json.load(open(sys.argv[1])):
    r = api(action='query', generator='search', gsrsearch=q + ' filetype:video', gsrnamespace=6, gsrlimit=15, prop='imageinfo', iiprop='extmetadata|size|mediatype')
    time.sleep(20)
    c = []
    for pg in (r or {}).get('query', {}).get('pages', {}).values():
        ii = pg.get('imageinfo', [{}])[0]; m = ii.get('extmetadata', {})
        lic = re.sub('<[^>]+>', '', m.get('LicenseShortName', {}).get('value', ''))
        if not re.search(r'public domain|cc0|cc by|pd', lic, re.I): continue
        c.append(dict(title=pg['title'], lic=lic, w=ii.get('width'), dur=ii.get('duration'), desc=re.sub('<[^>]+>', '', m.get('ImageDescription', {}).get('value', ''))[:120]))
    out[q] = c; json.dump(out, open(sys.argv[2], 'w'), indent=1, ensure_ascii=False); print(q, len(c), flush=True)
