"""python3 vget2.py name "File:x.webm" ss dur ... ; direct upload.wikimedia.org (no API)"""
import sys, os, hashlib, urllib.parse, subprocess, time
UA = 'DocResearch/1.0 (documentary licensing check)'
os.makedirs('clips', exist_ok=True)
a = sys.argv[1:]
for i in range(0, len(a), 4):
    name, title, ss, dur = a[i:i + 4]
    out = f'clips/{name}.mp4'
    if os.path.exists(out) and os.path.getsize(out) > 50000: print(name, 'have', flush=True); continue
    fn = title.split(':', 1)[1].replace(' ', '_'); h = hashlib.md5(fn.encode()).hexdigest(); q = urllib.parse.quote(fn)
    base = f'https://upload.wikimedia.org/wikipedia/commons'
    urls = [f'{base}/transcoded/{h[0]}/{h[:2]}/{q}/{q}.{r}' for r in ('720p.vp9.webm', '720p.webm', '1080p.vp9.webm', '480p.vp9.webm')] + [f'{base}/{h[0]}/{h[:2]}/{q}']
    tmp = f'clips/{name}.src'; ok = False
    for u in urls:
        for t in range(3):
            rc = subprocess.call(['curl', '-s', '-L', '-f', '-m', '900', '-A', UA, '-o', tmp, u])
            if rc == 0 and os.path.getsize(tmp) > 50000: ok = True; break
            if rc == 22: break
            time.sleep(20 * (t + 1))
        if ok: break
    if not ok: print(name, 'FAILED', flush=True); continue
    subprocess.call(['ffmpeg', '-v', 'error', '-y', '-ss', ss, '-i', tmp, '-t', dur, '-an', '-vf', 'scale=1280:-2,fps=30', '-c:v', 'libx264', '-crf', '20', '-preset', 'fast', out])
    os.remove(tmp); print(name, os.path.getsize(out) if os.path.exists(out) else 'ffmpeg-fail', u.rsplit('.', 2)[-2], flush=True); time.sleep(3)
