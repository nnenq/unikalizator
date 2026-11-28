"""Flickr without API key.
 python3 fl.py search "text" [user_nsid|-] [license=7,8,9,10,4,5]  -> prints id | title | lic | w
 python3 fl.py get name id [name id ...] -> img/name.jpg (largest <=2048) + img/name.lic"""
import sys, re, os, time, subprocess, json, urllib.parse
def urllib_q(s): return urllib.parse.quote(s)
UA = 'Mozilla/5.0 (X11; Linux x86_64)'
LIC = {'4': 'CC BY 2.0', '5': 'CC BY-SA 2.0', '7': 'No known copyright restrictions', '8': 'United States Government Work', '9': 'CC0', '10': 'Public Domain Mark'}
def fetch(url):
    for a in range(4):
        r = subprocess.run(['curl', '-s', '-L', '-m', '60', '-A', UA, url], capture_output=True)
        if r.returncode == 0 and len(r.stdout) > 1000: return r.stdout.decode('utf8', 'ignore')
        time.sleep(10 * (a + 1))
    return ''
def page(pid):
    for a in range(5):
        h = fetch(f'https://www.flickr.com/photos/{pid.split("@",1)[1]}/{pid.split("@")[0]}/' if '@' in pid else f'https://www.flickr.com/photo.gne?id={pid}')
        if '"license":' in h: break
        time.sleep(30 * (a + 1))
    t = re.search(r'og:title" content="([^"]*)"', h); lic = re.search(r'"license":(\d+)', h)
    sizes = {}
    for k, u, w in re.findall(r'"(\w+)":\{"displayUrl":"([^"]+)","width":(\d+)', h): sizes[k] = (int(w), 'https:' + u.replace('\\/', '/'))
    owner = re.search(r'"ownerNsid":"([^"]+)"', h) or re.search(r'"owner":\{[^}]*"nsid":"([^"]+)"', h)
    rn = re.search(r'"realname":"([^"]*)"', h); un = re.search(r'"username":"([^"]*)"', h)
    return dict(id=pid, title=t.group(1) if t else '', lic=LIC.get(lic.group(1), 'lic' + lic.group(1)) if lic else '?', sizes=sizes,
                author=(rn.group(1) if rn and rn.group(1) else (un.group(1) if un else '')))
c = sys.argv[1]
if c == 'search':
    text = sys.argv[2]; user = sys.argv[3] if len(sys.argv) > 3 and sys.argv[3] != '-' else ''
    lic = sys.argv[4] if len(sys.argv) > 4 else '4,5,7,8,9,10'
    url = 'https://www.flickr.com/search/?text=' + text.replace(' ', '%20') + '&license=' + lic.replace(',', '%2C') + ('&user_id=' + user.replace('@', '%40') if user else '')
    h = fetch(url)
    ids = []
    for i in re.findall(r'live\.staticflickr\.com\\/\d+\\/(\d+)_', h):
        if i not in ids: ids.append(i)
    n = int(os.environ.get('N', '15'))
    for i in ids[:n]:
        p = page(i); mw = max([w for w, u in p['sizes'].values()] or [0])
        print(i, '|', p['title'][:80], '|', p['lic'], '|', mw, '|', p['author'][:30], flush=True); time.sleep(1.5)
elif c == 'get':
    os.makedirs('img', exist_ok=True)
    a = sys.argv[2:]
    for name, pid in zip(a[::2], a[1::2]):
        p = page(pid)
        if p['lic'] not in LIC.values(): print(name, 'BAD LICENSE', p['lic']); continue
        best = sorted([s for s in p['sizes'].values() if s[0] <= 2100], key=lambda s: -s[0])
        if not best: print(name, 'nosize'); continue
        subprocess.call(['curl', '-s', '-L', '-m', '120', '-A', UA, '-o', f'img/{name}.tmp', best[0][1]])
        os.system(f'ffmpeg -v error -y -i img/{name}.tmp -q:v 3 img/{name}.jpg && rm -f img/{name}.tmp')
        open(f'img/{name}.lic', 'w').write(json.dumps(dict(src=f'https://www.flickr.com/photo.gne?id={pid.split("@")[0]}', title=p['title'], lic=p['lic'], author=p['author'])))
        print(name, best[0][0], p['lic'], p['author'], p['title'][:60], flush=True); time.sleep(2)
if c == 'find':
    # python3 fl.py find out.json "q1" "q2" ... (any user, open licenses); saves thumbs to cand/th/
    out = sys.argv[2]; res = json.load(open(out)) if os.path.exists(out) else {}
    os.makedirs('cand/th', exist_ok=True)
    for q in sys.argv[3:]:
        if q in res: continue
        h = fetch('https://www.flickr.com/search/?text=' + urllib_q(q) + '&license=4%2C5%2C7%2C8%2C9%2C10')
        items = []
        for p in h.split('"_flickrModelRegistry":"photo-lite-models"')[1:]:
            g = lambda r: (re.search(r, p) or [None, ''])[1]
            pid = g(r'"id":"(\d+)"\},"exportMetaType":"model"'); own = g(r'"ownerNsid":"([^"]+)"'); lic = g(r'"license":(\d+)')
            th = g(r'"m":\{"data":\{"displayUrl":"([^"]+)"')
            if not pid or lic not in LIC: continue
            items.append(dict(id=pid, owner=own, title=g(r'"title":"([^"]*)"'), lic=LIC[lic], author=g(r'"realname":"([^"]*)"') or g(r'"username":"([^"]*)"')))
            if th and not os.path.exists(f'cand/th/{pid}.jpg'):
                subprocess.call(['curl', '-s', '-m', '30', '-A', UA, '-o', f'cand/th/{pid}.jpg', 'https:' + th.replace('\\/', '/')])
        res[q] = items[:int(os.environ.get('N', '20'))]
        json.dump(res, open(out, 'w'), indent=1, ensure_ascii=False); print(q, len(items), flush=True); time.sleep(6)
