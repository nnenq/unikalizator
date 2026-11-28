"""Flickr without API key.
 python3 fl.py search "text" [user_nsid|-] [license=7,8,9,10,4,5]  -> prints id | title | lic | w
 python3 fl.py get name id [name id ...] -> img/name.jpg (largest <=2048) + img/name.lic"""
import sys, re, os, time, subprocess, json
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
        h = fetch(f'https://www.flickr.com/photo.gne?id={pid}')
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
        open(f'img/{name}.lic', 'w').write(json.dumps(dict(src=f'https://www.flickr.com/photo.gne?id={pid}', title=p['title'], lic=p['lic'], author=p['author'])))
        print(name, best[0][0], p['lic'], p['author'], p['title'][:60], flush=True); time.sleep(2)
