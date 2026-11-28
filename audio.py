"""Build final.wav: narration placed on timeline + quiet ambient bed, loudnorm -14 LUFS."""
import os, json, subprocess, sys
ENG = os.path.dirname(os.path.abspath(__file__))
info = json.loads(subprocess.run([sys.executable, os.path.join(ENG, 'dk.py'), 'vo'], capture_output=True, text=True, check=True).stdout)
st, total = info['starts'], info['total']
n = len(st)
inp = []; fl = []
for i, s in enumerate(st):
    inp += ['-i', f'vo/{i:03d}.wav']; ms = int(s * 1000)
    fl.append(f'[{i}:a]aresample=48000,aformat=channel_layouts=mono,adelay={ms}|{ms},apad[v{i}]')
mix = ''.join(f'[v{i}]' for i in range(n))
MUS = info.get('music') or []
if MUS:
    keys = info['keys']; cues = [(st[keys.index(k)], tr, vol) for k, tr, vol in MUS]
    cues.sort()
    parts = []
    for j, (c0, tr, vol) in enumerate(cues):
        c1 = cues[j + 1][0] if j + 1 < len(cues) else total
        ln = c1 - c0 + 2.0; ms = max(0, int((c0 - 1.0) * 1000))
        parts.append((tr, ln, vol, ms))
    ins = []; fl2 = []
    for j, (tr, ln, vol, ms) in enumerate(parts):
        ins += ['-stream_loop', '-1', '-i', '/root/music/' + tr + '.mp3']
        fl2.append(f'[{j}:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:{ln:.2f},asetpts=PTS-STARTPTS,afade=t=in:d=1.5,afade=t=out:st={max(0.1, ln - 2.5):.2f}:d=2.5,volume={vol},adelay={ms}|{ms},apad[m{j}]')
    mx = ''.join(f'[m{j}]' for j in range(len(parts)))
    fc2 = ';'.join(fl2) + f';{mx}amix=inputs={len(parts)}:normalize=0,atrim=0:{total}[mus]'
    subprocess.run(['ffmpeg', '-v', 'error', '-y'] + ins + ['-filter_complex', fc2, '-map', '[mus]', 'music.wav'], check=True)
bed = (f"anoisesrc=color=brown:amplitude=0.5:r=48000:d={total},lowpass=f=180,volume=0.05[n];"
       f"sine=f=55:r=48000:d={total},volume=0.025[s1];sine=f=82.4:r=48000:d={total},volume=0.015[s2];"
       f"[n][s1][s2]amix=inputs=3:normalize=0,afade=t=in:d=3,afade=t=out:st={total - 4}:d=4[bed]")
if MUS:
    inp += ['-i', 'music.wav']; mi = n
    fc = ';'.join(fl) + f';{mix}amix=inputs={n}:normalize=0,atrim=0:{total},asplit=2[vo][sc];[{mi}:a]aformat=channel_layouts=mono[mm];[mm][sc]sidechaincompress=threshold=0.02:ratio=6:attack=40:release=600[duck];[vo][duck]amix=inputs=2:normalize=0,alimiter=limit=0.9[pre]'
else:
    fc = ';'.join(fl) + f';{mix}amix=inputs={n}:normalize=0,atrim=0:{total}[vo];' + bed + ';[vo][bed]amix=inputs=2:normalize=0,alimiter=limit=0.9[pre]'
subprocess.run(['ffmpeg', '-v', 'error', '-y'] + inp + ['-filter_complex', fc, '-map', '[pre]', '-ac', '2', 'pre.wav'], check=True)
m = subprocess.run(['ffmpeg', '-hide_banner', '-i', 'pre.wav', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-'], capture_output=True, text=True).stderr
j = json.loads(m[m.rindex('{'):m.rindex('}') + 1])
af = f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true"
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', 'pre.wav', '-af', af, '-ar', '48000', 'final.wav'], check=True)
print('audio ok', round(total, 1))
