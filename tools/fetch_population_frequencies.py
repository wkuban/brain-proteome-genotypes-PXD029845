"""Fetch East Asian allele frequencies (gnomAD, 1000 Genomes) for a list of dbSNP ids from the Ensembl REST API.
Resumable cache: results/ensembl_eas_frequencies.json
Usage: python tools/fetch_population_frequencies.py <file with one rsID per line> [time_budget_s]"""
import sys, json, os, time, urllib.request
ids = [l.strip() for l in open(sys.argv[1]) if l.strip().startswith('rs')]
budget = float(sys.argv[2]) if len(sys.argv) > 2 else 1e9
cache_p = 'results/ensembl_eas_frequencies.json'
cache = json.load(open(cache_p)) if os.path.exists(cache_p) else {}
todo = [i for i in dict.fromkeys(ids) if i not in cache]
t0 = time.time(); B = 25
while todo and time.time() - t0 < budget:
    batch, todo = todo[:B], todo[B:]
    req = urllib.request.Request('https://rest.ensembl.org/variation/homo_sapiens?pops=1', data=json.dumps({'ids': batch}).encode(),
                                 headers={'Content-Type': 'application/json', 'Accept': 'application/json'})
    try:
        got = json.load(urllib.request.urlopen(req, timeout=60))
    except Exception as e:
        print('retry later:', type(e).__name__); todo += batch; time.sleep(3); continue
    for i in batch:
        v = got.get(i)
        if v is None:
            cache[i] = None; continue
        m = (v.get('mappings') or [{}])[0]
        pops = [p for p in v.get('populations', []) if p['population'] in ('gnomADg:eas', 'gnomADe:eas', '1000GENOMES:phase_3:EAS')]
        cache[i] = {'allele_string': m.get('allele_string'), 'consequence': v.get('most_severe_consequence'),
                    'freq': [(p['population'], p['allele'], p['frequency']) for p in pops]}
    json.dump(cache, open(cache_p, 'w'))
print('cached', len(cache), '; still to fetch', len(todo))
