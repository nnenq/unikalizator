"""python3 vget.py name "File:x.webm" [ss dur] ... -> clips/name.mp4 (720p transcode, trimmed, no audio)"""
import sys, json, time, urllib.request, urllib.parse, os, subprocess
UA = {'User-Agent': 'DocResearch/1.0 (documentary licensing check)'}
def api(**p):
    p['format'] = 'json'
    for a in range(6):
        try: return json.loads(urllib.request.urlopen(urllib.request.Request('https://commons.wikimedia.org/w/api.php?' + urllib.parse.urlencode(p), headers=UA), timeout=40).read())
        except Exception: time.sleep(30 * (a + 1))
os.makedirs('clips', exist_ok=True)
a = sys.argv[1:]
i = 0
while i < len(a):
    name, title, ss, dur = a[i], a[i+1], a[i+2], a[i+3]; i += 4
    out = f'clips/{name}.mp4'
    if os.path.exists(out) and os.path.getsize(out) > 50000: print(name, 'have'); continue
    r = None
    for t in range(4):
        r = api(action='query', titles=title, prop='videoinfo', viprop='url|derivatives')
        if r: break
        time.sleep(120)
    if not r: print(name, 'APIFAIL', flush=True); continue
    pg = list(r['query']['pages'].values())[0]
    vi = pg.get('videoinfo', [{}])[0]
    ders = vi.get('derivatives', [])
    pick = None
    for pref in ('720p.vp9.webm', '1080p.vp9.webm', '720p.webm', '480p.vp9.webm', '480p.webm'):
        for d in ders:
            if d['src'].endswith(pref): pick = d['src']; break
        if pick: break
    url = pick or vi.get('url')
    tmp = f'clips/{name}.src'
    ok = False
    for t in range(5):
        rc = subprocess.call(['curl', '-s', '-L', '-f', '-m', '900', '-A', UA['User-Agent'], '-o', tmp, url])
        if rc == 0 and os.path.getsize(tmp) > 50000: ok = True; break
        time.sleep(40 * (t + 1))
    if not ok: print(name, 'FAILED', url); continue
    subprocess.call(['ffmpeg', '-v', 'error', '-y', '-ss', ss, '-i', tmp, '-t', dur, '-an', '-vf', 'scale=1280:-2,fps=30', '-c:v', 'libx264', '-crf', '20', '-preset', 'fast', out])
    os.remove(tmp)
    print(name, os.path.getsize(out) if os.path.exists(out) else 'ffmpeg-fail', flush=True); time.sleep(8)
