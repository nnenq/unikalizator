"""Piper narration: python3 tts.py  (in project dir; uses script.S and PRON from plan)."""
import os, sys, json, subprocess, wave, importlib.util
from concurrent.futures import ThreadPoolExecutor
P = os.getcwd()
def load(n):
    s = importlib.util.spec_from_file_location(n, os.path.join(P, n + '.py')); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
S = load('script').S
PRON = getattr(load('plan'), 'PRON', [])
V = os.environ.get('VOICE', '/root/vk/ryan.onnx')
os.makedirs('vo', exist_ok=True)
def gen(i):
    k, v, t = S[i]
    for a, b in PRON: t = t.replace(a, b)
    out = f'vo/{i:03d}.wav'
    if not os.path.exists(out):
        subprocess.run(['piper', '-m', V, '--length_scale', '1.28', '--sentence_silence', '0.75', '-f', out], input=t.encode(), check=True, capture_output=True)
    w = wave.open(out); return w.getnframes() / w.getframerate()
with ThreadPoolExecutor(4) as ex: d = list(ex.map(gen, range(len(S))))
json.dump({'durs': d, 'lines': [list(x) for x in S]}, open('vo/vo.json', 'w'))
print(len(d), round(sum(d) / 60, 2), 'min')
