"""python3 commons.py search "query" | info "File:.." ... | get name "File:.." [...]"""
import sys, json, time, urllib.request, urllib.parse, re, os
UA = {'User-Agent': 'DocResearch/1.0 (documentary image licensing check)'}
def api(**p):
    p['format'] = 'json'
    for a in range(6):
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request('https://commons.wikimedia.org/w/api.php?' + urllib.parse.urlencode(p), headers=UA), timeout=40))
        except Exception as e:
            time.sleep(15 * (a + 1))
    raise SystemExit('api failed')
c = sys.argv[1]
if c == 'search':
    r = api(action='query', list='search', srsearch=sys.argv[2], srnamespace=6, srlimit=15)
    for x in r['query']['search']: print(x['title'])
elif c == 'info':
    r = api(action='query', titles='|'.join(sys.argv[2:]), prop='imageinfo', iiprop='extmetadata|size')
    for p in r['query']['pages'].values():
        ii = p.get('imageinfo', [{}])[0]; m = ii.get('extmetadata', {})
        g = lambda k: re.sub('<[^>]+>', '', m.get(k, {}).get('value', '') or '')[:70]
        print(p['title'], '|', ii.get('width'), 'x', ii.get('height'), '|', g('LicenseShortName'), '|', g('Artist'), '|', g('DateTimeOriginal'))
elif c == 'get':
    pairs = sys.argv[2:]; os.makedirs('img', exist_ok=True)
    for name, title in zip(pairs[::2], pairs[1::2]):
        out = f'img/{name}.jpg'
        if os.path.exists(out) and os.path.getsize(out) > 10000: continue
        r = api(action='query', titles=title, prop='imageinfo', iiprop='url', iiurlwidth=2200)
        ii = list(r['query']['pages'].values())[0]['imageinfo'][0]
        url = ii.get('thumburl') or ii['url']
        data = None
        for a in range(6):
            try:
                data = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read(); break
            except Exception as e:
                time.sleep(20 * (a + 1))
        if not data:
            print(name, 'FAILED'); continue
        open(out + '.tmp', 'wb').write(data)
        os.system(f'ffmpeg -v error -y -i "{out}.tmp" -q:v 3 "{out}" && rm -f "{out}.tmp"')
        print(name, os.path.getsize(out)); time.sleep(4)
