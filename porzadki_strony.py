# Netlify: buduje stronę z repozytorium, w którym pliki wgrywane przez przeglądarkę
# dostają dopiski " (1)", " (2)"... Dla każdej nazwy bierze NAJNOWSZĄ wersję (wg git),
# zapisuje ją pod właściwą nazwą i pomija pliki wewnętrzne.
import os, re, shutil, subprocess
SRC = '.'
OUT = '_site'
POMIN_KAT = {'.git', OUT, 'FSJ_strona', 'node_modules'}
POMIN = re.compile(r'(^(0[1-4]|0[7-9]|1[0135])-|\.docx$|\.zip$|^Pakiet-|^Zarzadzenie|^netlify|^porzadki_strony|^strona_fsj|^README)', re.I)
NUM = re.compile(r'^(.*?) \((\d+)\)(\.[^.]+)$')

def czas(sciezka):
    try:
        out = subprocess.run(['git', 'log', '-1', '--format=%ct', '--', sciezka], capture_output=True, text=True).stdout.strip()
        return int(out) if out else 0
    except Exception:
        return 0

if os.path.exists(OUT): shutil.rmtree(OUT)
os.makedirs(OUT)
grupy = {}
for kat, podkat, pliki in os.walk(SRC):
    rel = os.path.relpath(kat, SRC)
    if rel != '.' and rel.split(os.sep)[0] in POMIN_KAT or rel.split(os.sep)[0].startswith('strona_fsj'):
        podkat[:] = []; continue
    podkat[:] = [d for d in podkat if d not in POMIN_KAT and not d.startswith('strona_fsj')]
    for p in pliki:
        if POMIN.search(p): continue
        m = NUM.match(p)
        baza, nr = (m.group(1) + m.group(3), int(m.group(2))) if m else (p, 0)
        sciezka = os.path.normpath(os.path.join(rel, p))
        cel = os.path.normpath(os.path.join(rel, baza))
        grupy.setdefault(cel, []).append((czas(sciezka), nr, sciezka))
for cel, wersje in grupy.items():
    wersje.sort()
    najnowsza = wersje[-1][2]
    os.makedirs(os.path.join(OUT, os.path.dirname(cel)), exist_ok=True)
    shutil.copy2(najnowsza, os.path.join(OUT, cel))
    if len(wersje) > 1: print(f'{cel} <- {najnowsza}')
print('Plików na stronie:', len(grupy))
