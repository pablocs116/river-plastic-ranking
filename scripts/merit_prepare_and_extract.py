#!/usr/bin/env python3
"""Prepare MERIT 15s tiles: filter ZIP for elv/slp/upa, extract .tar tiles, and unpack .tif files.

Usage:
  python scripts/merit_prepare_and_extract.py \
    --zip data/raw/MERIT_Hydro.zip \
    --fm data/processed/feature_matrix_v1.csv \
    --outdir data/raw/merit_15s_filtered --untar

Set --all to extract all tiles for the variables instead of computing tiles from the feature matrix.
"""
import argparse
import csv
import zipfile
import tarfile
from pathlib import Path
import tempfile
import shutil
import os


def tile_name(lat, lon):
    ns = "n" if lat >= 0 else "s"
    ew = "e" if lon >= 0 else "w"
    t_lat = abs(int(lat // 30) * 30)
    t_lon = abs(int(lon // 30) * 30)
    return f"{ns}{t_lat:02d}{ew}{t_lon:03d}"


def needed_tiles_from_fm(fm_path):
    tiles = set()
    if not fm_path.exists():
        return sorted(tiles)
    with fm_path.open(newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            tiles.add(tile_name(row["lat"], row["lon"]))
    return sorted(tiles)


def extract_matching_from_zip(zip_path, out_dir, tiles=None, vars=("elv","slp","upa")):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    temp_root = tempfile.TemporaryDirectory()
    extracted_tars = []
    with zipfile.ZipFile(zip_path, 'r') as z:
        names = z.namelist()
        for name in names:
            n = name.replace('\\','/')
            for v in vars:
                # support multiple archive layouts: 15s/{var}/..., v1.0.1/{var}_<tile>.tar, or {var}_*.tar
                matches_layout = (
                    f'15s/{v}/' in n or
                    f'/{v}_' in n or
                    f'/{v}/' in n or
                    n.startswith(f'{v}_')
                )
                if matches_layout:
                    if not tiles or any(t in n for t in tiles):
                        z.extract(name, path=temp_root.name)
                        member_path = Path(temp_root.name) / name
                        if member_path.suffix == '.tar' or member_path.is_dir() or member_path.suffix in ('.tar.gz', '.tgz'):
                            extracted_tars.append(member_path)
                        else:
                            # move/take file into out_dir preserving variable folder when possible
                            try:
                                if '15s' in member_path.parts:
                                    rel_index = member_path.parts.index('15s')
                                    rel = Path(*member_path.parts[rel_index:])
                                    dest = out_dir / rel
                                else:
                                    # place under out_dir/15s/<var>/
                                    dest = out_dir / '15s' / v / member_path.name
                                dest.parent.mkdir(parents=True, exist_ok=True)
                                try:
                                    shutil.move(str(member_path), str(dest))
                                except Exception:
                                    shutil.copy(str(member_path), str(dest))
                            except Exception:
                                dest = out_dir / member_path.name
                                try:
                                    shutil.move(str(member_path), str(dest))
                                except Exception:
                                    shutil.copy(str(member_path), str(dest))
                        break
    return temp_root, extracted_tars


def untar_and_collect_tifs(tar_paths, out_dir):
    out_dir = Path(out_dir)
    for tarp in tar_paths:
        if not tarp.exists():
            continue
        # Determine variable from path string if present
        parts = [p for p in tarp.parts]
        var = None
        if '15s' in parts:
            idx = parts.index('15s')
            if len(parts) > idx+1:
                var = parts[idx+1]
        if var is None:
            base = tarp.name.lower()
            if 'elv_' in base or base.startswith('elv'):
                var = 'elv'
            elif 'upa_' in base or base.startswith('upa'):
                var = 'upa'
            elif 'slp_' in base or base.startswith('slp'):
                var = 'slp'
        if var is None:
            var = 'unknown'
        target_var_dir = out_dir / '15s' / var
        target_var_dir.mkdir(parents=True, exist_ok=True)
        # If tarp is a directory (zip may have extracted directories), walk and move tifs
        if tarp.is_dir():
            for p in tarp.rglob('*.tif'):
                try:
                    shutil.move(str(p), str(target_var_dir / p.name))
                except Exception:
                    shutil.copy(str(p), str(target_var_dir / p.name))
            continue
        try:
            with tarfile.open(tarp, 'r:*') as tf:
                for member in tf.getmembers():
                    if not member.isreg() or not member.name.lower().endswith('.tif'):
                        continue
                    member_name = Path(member.name).name.lower()
                    if var == 'unknown':
                        if member_name.endswith('_elv.tif'):
                            target_var_dir = out_dir / '15s' / 'elv'
                            target_var_dir.mkdir(parents=True, exist_ok=True)
                        elif member_name.endswith('_upa.tif'):
                            target_var_dir = out_dir / '15s' / 'upa'
                            target_var_dir.mkdir(parents=True, exist_ok=True)
                        elif member_name.endswith('_slp.tif'):
                            target_var_dir = out_dir / '15s' / 'slp'
                            target_var_dir.mkdir(parents=True, exist_ok=True)
                    f = tf.extractfile(member)
                    if f is None:
                        continue
                    outpath = target_var_dir / Path(member.name).name
                    with open(outpath, 'wb') as out_f:
                        shutil.copyfileobj(f, out_f)
        except tarfile.TarError:
            try:
                with tarfile.open(tarp, 'r:gz') as tf:
                    for member in tf.getmembers():
                        if not member.isreg() or not member.name.lower().endswith('.tif'):
                            continue
                        member_name = Path(member.name).name.lower()
                        if var == 'unknown':
                            if member_name.endswith('_elv.tif'):
                                target_var_dir = out_dir / '15s' / 'elv'
                                target_var_dir.mkdir(parents=True, exist_ok=True)
                            elif member_name.endswith('_upa.tif'):
                                target_var_dir = out_dir / '15s' / 'upa'
                                target_var_dir.mkdir(parents=True, exist_ok=True)
                            elif member_name.endswith('_slp.tif'):
                                target_var_dir = out_dir / '15s' / 'slp'
                                target_var_dir.mkdir(parents=True, exist_ok=True)
                        f = tf.extractfile(member)
                        if f is None:
                            continue
                        outpath = target_var_dir / Path(member.name).name
                        with open(outpath, 'wb') as out_f:
                            shutil.copyfileobj(f, out_f)
            except Exception as e:
                print(f"Failed to read tar {tarp}: {e}")


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--zip', required=True, help='Path to MERIT_Hydro.zip')
    p.add_argument('--fm', required=False, help='feature_matrix_v1.csv to compute needed tiles')
    p.add_argument('--outdir', required=True, help='Output directory for filtered MERIT 15s files')
    p.add_argument('--vars', default='elv,slp,upa', help='Comma-separated variables to extract')
    p.add_argument('--all', action='store_true', help='Extract all tiles for the variables (do not filter by feature matrix)')
    p.add_argument('--untar', action='store_true', help='Untar extracted .tar files and collect .tif files')
    args = p.parse_args()

    zip_path = Path(args.zip)
    fm_path = Path(args.fm) if args.fm else None
    out_dir = Path(args.outdir)
    vars = tuple(v.strip() for v in args.vars.split(','))

    tiles = None
    if not args.all and fm_path and fm_path.exists():
        tiles = needed_tiles_from_fm(fm_path)
        print(f"Tiles needed: {len(tiles)}")
    else:
        print("Extracting all tiles for variables: ", vars)

    temp_root, tar_paths = extract_matching_from_zip(zip_path, out_dir, tiles=tiles, vars=vars)
    print(f"Extracted {len(tar_paths)} tar/directory entries from zip to temp area.")

    if args.untar:
        print("Unpacking .tar files and collecting .tif files...")
        untar_and_collect_tifs(tar_paths, out_dir)
        print("Done untarring and collecting .tif files into:", out_dir)

    print("Finished.")
