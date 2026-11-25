"""Repair files in which an HTTP error page (403) was written into the download and the
transfer then resumed after it. Each inserted page occupies the place of the real bytes,
so the real bytes are fetched by HTTP range request and written back. SHA-1 decides success."""
import os, csv, hashlib, json, sys, time, urllib.request, re
budget = float(sys.argv[1]) if len(sys.argv) > 1 else 1e9
man = {r['file_name']: r for r in csv.DictReader(open('config/PXD029845_manifest.tsv'), delimiter='\t')}
logp = 'results/sha1_verified.json'; ok = json.load(open(logp))
replog = 'results/repair_log.json'; rep = json.load(open(replog)) if os.path.exists(replog) else {}
START = b'<!DOCTYPE HTML PUBLIC'; END = b'</html>\n'
t0 = time.time()
def sha1(p):
    h = hashlib.sha1()
    with open(p, 'rb') as fh:
        while True:
            b = fh.read(1 << 24)
            if not b: break
            h.update(b)
    return h.hexdigest()
def fetch(url, a, b):
    for k in range(6):
        try:
            req = urllib.request.Request(url, headers={'Range': f'bytes={a}-{b}'})
            with urllib.request.urlopen(req, timeout=90) as r:
                d = r.read()
                if r.status == 206 and len(d) == b - a + 1: return d
        except Exception as e:
            pass
        time.sleep(5)
    return None
for n, good in list(ok.items()):
    if good: continue
    if time.time() - t0 > budget: break
    p = 'data_raw/' + n; r = man[n]; spans = []
    with open(p, 'rb') as fh:
        off = 0; tail = b''
        while True:
            b = fh.read(1 << 24)
            if not b: break
            buf = tail + b; base = off - len(tail)
            for m in re.finditer(re.escape(START), buf):
                s = base + m.start()
                if not spans or s >= spans[-1][0] + 50: spans.append([s, None])
            tail = buf[-64:]; off += len(b)
        for sp in spans:
            fh.seek(sp[0]); chunk = fh.read(4096); e = chunk.find(END)
            sp[1] = sp[0] + e + len(END) - 1 if e >= 0 else None
    if not spans or any(s[1] is None for s in spans):
        rep[n] = {'spans': spans, 'result': 'cannot repair'}; json.dump(rep, open(replog, 'w'), indent=1); continue
    with open(p, 'r+b') as fh:
        fine = True
        for a, b in spans:
            d = fetch(r['url'], a, b)
            if d is None: fine = False; break
            fh.seek(a); fh.write(d)
    good = fine and sha1(p) == r['sha1']
    ok[n] = good; rep[n] = {'spans': spans, 'result': 'repaired' if good else 'still bad'}
    json.dump(ok, open(logp, 'w'), indent=1); json.dump(rep, open(replog, 'w'), indent=1)
    print(n, spans, rep[n]['result'], flush=True)
print('match', sum(ok.values()), 'of', len(ok), '; bad:', [n for n, v in ok.items() if not v])
