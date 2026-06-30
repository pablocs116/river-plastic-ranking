#!/usr/bin/env python3
"""Extract MERIT elv and upa tiles for needed outfall tiles without pandas."""
import csv
import tarfile
import zipfile
from io import BytesIO
from pathlib import Path

root = Path(__file__).resolve().parent.parent
fm = root / 'river_outfalls.csv'
zip_path = root / 'data' / 'raw' / 'MERIT_Hydro.zip'
out_root = root / 'data' / 'raw' / 'merit_15s_filtered'

if not fm.exists():
    raise SystemExit(f'Missing outfalls CSV: {fm}')
if not zip_path.exists():
    raise SystemExit(f'Missing ZIP: {zip_path}')

needed = set()
with fm.open(newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        lat = float(row['lat'])
        lon = float(row['lon'])
        ns = 'n' if lat >= 0 else 's'
        ew = 'e' if lon >= 0 else 'w'
        t_lat = abs(int(lat // 30) * 30)
        t_lon = abs(int(lon // 30) * 30)
        needed.add(f'{ns}{t_lat:02d}{ew}{t_lon:03d}')

(elv_out := out_root / '15s' / 'elv').mkdir(parents=True, exist_ok=True)
(upa_out := out_root / '15s' / 'upa').mkdir(parents=True, exist_ok=True)

matched = []
with zipfile.ZipFile(zip_path, 'r') as z:
    for name in z.namelist():
        if not name.startswith('v1.0.1/'):
            continue
        base = Path(name).name
        if not base.endswith('.tar'):
            continue
        if base.startswith('elv_'):
            var = 'elv'
            tile = base[4:-4]
        elif base.startswith('upa_'):
            var = 'upa'
            tile = base[4:-4]
        else:
            continue
        if tile not in needed:
            continue
        matched.append((name, var, tile))

    print(f'Matched tar entries: {len(matched)}')
    for name, var, tile in matched:
        print('extracting', var, tile)
        data = z.read(name)
        with tarfile.open(fileobj=BytesIO(data), mode='r:*') as tf:
            target_dir = elv_out if var == 'elv' else upa_out
            for member in tf.getmembers():
                if member.isreg() and member.name.lower().endswith('.tif'):
                    outpath = target_dir / Path(member.name).name
                    with tf.extractfile(member) as f, open(outpath, 'wb') as out_f:
                        out_f.write(f.read())

elv_count = sum(1 for _ in elv_out.glob('*.tif'))
upa_count = sum(1 for _ in upa_out.glob('*.tif'))
print(f'elv .tif count: {elv_count}')
print(f'upa .tif count: {upa_count}')
