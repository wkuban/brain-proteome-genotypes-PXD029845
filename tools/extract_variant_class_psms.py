"""Collect, from the PeptideProphet/Percolator pep.xml files written by FragPipe, every rank-1 PSM whose
protein list contains a variant entry (target or decoy), before any FDR filtering.
Needed for a class-specific FDR of variant peptides. Resumable: one TSV per TMT set.
Usage: python tools/extract_variant_class_psms.py <search_dir> <out_dir> [time_budget_s]"""
import sys, re, glob, os, time, csv
search, out = sys.argv[1], sys.argv[2]
budget = float(sys.argv[3]) if len(sys.argv) > 3 else 1e9
os.makedirs(out, exist_ok=True)
VAR = re.compile(r'(?:rev_)?sp\|[A-Z0-9]+_[A-Z]\d+[A-Z]\|')
re_sq = re.compile(r'<spectrum_query .*?spectrum="([^"]+)"')
re_hit = re.compile(r'<search_hit .*?peptide="([A-Z]+)".*?hit_rank="(\d+)".*?protein="([^"]+)"|<search_hit .*?hit_rank="(\d+)".*?peptide="([A-Z]+)".*?protein="([^"]+)"')
re_pep = re.compile(r'peptide="([A-Z]+)"'); re_rank = re.compile(r'hit_rank="(\d+)"'); re_prot = re.compile(r' protein="([^"]+)"')
re_alt = re.compile(r'<alternative_protein .*?protein="([^"]+)"')
re_prob = re.compile(r'<peptideprophet_result probability="([0-9.eE+-]+)"')
t0 = time.time()
for s in range(1, 5):
    files = sorted(glob.glob(os.path.join(search, f'SET_{s}', 'interact-*.pep.xml')))
    done_p = os.path.join(out, f'variant_class_psms_SET_{s}.done')
    if os.path.exists(done_p): continue
    part = os.path.join(out, f'variant_class_psms_SET_{s}.tsv')
    seen = set()
    if os.path.exists(part):
        seen = {r[0] for r in csv.reader(open(part), delimiter='\t')}
    with open(part, 'a', newline='') as fh:
        w = csv.writer(fh, delimiter='\t')
        for f in files:
            name = os.path.basename(f)
            if name in seen: continue
            if time.time() - t0 > budget: print('budget reached at', name); sys.exit(0)
            rows = []; spec = pep = None; prots = []; rank1 = False; n_all = 0
            for line in open(f, encoding='utf-8', errors='replace'):
                if line.startswith('<spectrum_query'):
                    spec = re_sq.search(line).group(1); pep = None; prots = []; rank1 = False
                elif line.startswith('<search_hit'):
                    rank1 = re_rank.search(line).group(1) == '1'
                    if rank1:
                        pep = re_pep.search(line).group(1); prots = [re_prot.search(line).group(1)]
                elif rank1 and line.startswith('<alternative_protein'):
                    prots.append(re_alt.search(line).group(1))
                elif rank1 and line.startswith('<peptideprophet_result'):
                    n_all += 1
                    if any(VAR.match(p) for p in prots):
                        rows.append((name, spec, pep, re_prob.search(line).group(1), ';'.join(prots)))
                    rank1 = False
            w.writerow((name, '#psms_total', n_all, '', ''))
            w.writerows(rows); fh.flush()
    open(done_p, 'w').write('ok')
    print('SET', s, 'done', round(time.time() - t0), 's')
print('all done')
