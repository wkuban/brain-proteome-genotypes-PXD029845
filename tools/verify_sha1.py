"""Verify SHA-1 of every complete file in data_raw against the PRIDE manifest. Resumable; results in results/sha1_verified.json."""
import os, csv, hashlib, time, json, sys
budget = float(sys.argv[1]) if len(sys.argv) > 1 else 1e9
man = {r['file_name']: r for r in csv.DictReader(open('config/PXD029845_manifest.tsv'), delimiter='\t')}
where = {f: os.path.join(d, f) for d, _, fs in os.walk('data_raw') for f in fs}
logp = 'results/sha1_verified.json'
ok = json.load(open(logp)) if os.path.exists(logp) else {}
t0 = time.time(); todo = 0
for n, r in man.items():
    p = where.get(n, 'data_raw/' + n)
    if n in ok or not os.path.exists(p) or os.path.getsize(p) != int(r['size_bytes']):
        continue
    if time.time() - t0 > budget:
        todo += 1; continue
    h = hashlib.sha1()
    with open(p, 'rb') as fh:
        while True:
            b = fh.read(1 << 24)
            if not b: break
            h.update(b)
    ok[n] = (h.hexdigest() == r['sha1'])
    json.dump(ok, open(logp, 'w'), indent=1)
print(len(ok), 'checked;', sum(ok.values()), 'match; mismatch:', [n for n, v in ok.items() if not v], '; still to check:', todo)
