"""
Extract Table S3 from Meijer et al. 2021 supplementary PDF and match to outfall shapefile.
All values in Table S3 are monthly (tons/month) — annualize by *12 or sum-of-months * 12/n.
"""
import pandas as pd
import numpy as np
import geopandas as gpd
from scipy import stats

records = []

# Annual rivers (monthly value * 12)
year_rivers = [
    ('Eems','DEU',0.7,6.4),('Weser','DEU',2.2,19.0),('Elbe','DEU',145.7,41.6),
    ('Chao Phraya','THA',1425.0,4027.0),('Thachin','THA',361.0,728.0),
    ('Mae Klong','THA',173.0,341.0),('Bangpakong','THA',166.0,1335.0),
    ('Bang Taboon','THA',48.0,105.0),
    ('Aichi','JPN',40.4,165.8),('Akita','JPN',38.1,14.9),
    ('Aomori','JPN',26.3,10.6),('Chiba','JPN',31.2,75.7),
    ('Ehime','JPN',18.0,15.0),('Fukui','JPN',19.8,17.9),
    ('Fukuoka','JPN',35.1,46.2),('Fukushima','JPN',35.3,5.9),
    ('Hiroshima','JPN',24.0,37.8),('Hokkaido','JPN',91.6,36.5),
    ('Hyogo','JPN',28.8,85.5),('Ibaraki','JPN',23.5,36.9),
    ('Ishikawa','JPN',22.2,22.5),('Iwate','JPN',33.6,2.9),
    ('Kagawa','JPN',5.9,7.4),('Kagoshima','JPN',40.4,33.0),
    ('Kanagawa','JPN',31.6,268.9),('Kochi','JPN',23.1,17.7),
    ('Kumamoto','JPN',33.9,29.6),('Kyoto','JPN',16.3,3.6),
    ('Mie','JPN',26.5,53.8),('Miyagi','JPN',21.8,32.1),
    ('Miyazaki','JPN',35.5,25.2),('Nagasaki','JPN',16.0,16.1),
    ('Niigata','JPN',70.6,48.3),('Oita','JPN',21.2,10.6),
    ('Okayama','JPN',17.2,14.2),('Okinawa','JPN',11.2,9.1),
    ('Osaka','JPN',24.0,168.0),('Saga','JPN',12.1,22.7),
    ('Shimane','JPN',18.9,9.7),('Shizuoka','JPN',45.0,92.7),
    ('Tokushima','JPN',14.0,7.3),('Tokyo','JPN',36.0,328.6),
    ('Tottori','JPN',13.3,8.8),('Toyama','JPN',24.1,21.2),
    ('Wakayama','JPN',18.7,8.3),('Yamagata','JPN',32.7,9.5),
    ('Yamaguchi','JPN',20.8,12.5),
]
for name, country, obs_m, mod_m in year_rivers:
    records.append({
        'name': name, 'country': country,
        'obs_annual': obs_m * 12, 'model_annual': mod_m * 12, 'n_months': 12
    })

# Multi-month rivers
multi = {
    'Motagua': ('GTM', [39.7,2.4,17.7,6.1,93.2,215.9,250.9], [12.3,8.7,22.1,29.2,31.4,36.4,35.7]),
    'Seine': ('FRA', [8.3,1.0], [1.5,0.2]),
    'Rhone': ('FRA', [0.9,1.1,1.5,0.7,2.2,0.7,0.8,0.4,0.4,0.1,0.4,0.5], [1.0,0.9,1.0,1.0,1.0,0.8,0.5,0.4,0.4,0.5,0.9,1.1]),
    'Tiber': ('ITA', [1.3,1.3,0.7,0.7,0.7,0.5,0.5,0.5,1.3,1.3,1.3,1.3], [1.3,1.6,1.8,1.3,1.5,0.8,0.3,0.2,0.3,0.4,1.2,1.5]),
    'Rhine': ('NLD', [2.4,0.8], [3.0,2.4]),
    'Cengkareng': ('IDN', [95.4,198.7], [68.0,60.0]),
    'Jones Falls': ('USA', [1.3,3.2,2.3,9.3,3.3,7.7,6.0,4.6,3.2,2.4,3.0,3.0], [1.6,1.9,2.5,2.7,1.7,1.1,0.6,0.5,0.9,1.1,1.0,1.6]),
    'Saigon': ('VNM', [302.1,165.2,161.9,67.7,45.7,167.7,249.9,218.8,421.5], [89.4,158.9,99.3,158.9,149.0,188.7,198.6,218.5,198.6]),
    'Llobregat': ('ESP', [0.2,0.3,0.7,0.2,0.4,0.1,0.1,0.1,0.1,0.1,0.1,0.1], [0.6,0.6,0.9,1.1,1.3,0.9,0.5,0.3,0.4,0.4,0.7,0.5]),
    'Besos': ('ESP', [0.1,0.0,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1], [1.2,0.7,1.0,0.9,1.6,1.6,1.8,1.1,0.7,0.5]),
}
for name, (country, obs_list, mod_list) in multi.items():
    n = len(obs_list)
    records.append({
        'name': name, 'country': country,
        'obs_annual': sum(obs_list) * 12 / n, 'model_annual': sum(mod_list) * 12 / n,
        'n_months': n
    })

# Single-month rivers
single = [
    ('Pasig','PHL',85.0,544.0),('Tullahan','PHL',21.6,61.0),
    ('Meycuayan','PHL',392.0,160.0),('Kuantan','MYS',1.0,62.6),
    ('Ciliwung','IDN',308.0,205.0),('Pahang','MYS',10.7,65.0),
    ('Can Tho QT','VNM',29.4,12.1),('Can Tho RCK','VNM',1.8,0.3),
    ('Chao Phraya Nov','THA',97.0,147.7),
]
for name, country, obs_m, mod_m in single:
    records.append({
        'name': name, 'country': country,
        'obs_annual': obs_m * 12, 'model_annual': mod_m * 12, 'n_months': 1
    })

df = pd.DataFrame(records)
df['log_obs'] = np.log10(df['obs_annual'].clip(lower=0.01))
df['log_model'] = np.log10(df['model_annual'].clip(lower=0.01))

# Load shapefile and match
gdf = gpd.read_file('data/raw/meijer2021/Meijer2021_midpoint_emissions.shp')
me_vals = gdf['dots_exten'].values

matched = []
for _, row in df.iterrows():
    target = row['model_annual']
    diffs = np.abs(me_vals - target)
    best_idx = int(np.argmin(diffs))
    rel_err = diffs[best_idx] / target if target > 0 else 999
    match = gdf.iloc[best_idx]
    matched.append({
        'name': row['name'], 'country': row['country'],
        'obs_annual': row['obs_annual'], 'model_annual': row['model_annual'],
        'log_obs': row['log_obs'], 'log_model': row['log_model'],
        'n_months': row['n_months'],
        'outfall_idx': best_idx,
        'lon': match.geometry.x, 'lat': match.geometry.y,
        'outfall_ME': match['dots_exten'],
        'rel_err': rel_err,
    })

match_df = pd.DataFrame(matched)

# Stats
r2_all = 1 - np.sum((match_df.log_model - match_df.log_obs)**2) / np.sum((match_df.log_obs - match_df.log_obs.mean())**2)
no_k = match_df[match_df.name != 'Kuantan']
r2_nk = 1 - np.sum((no_k.log_model - no_k.log_obs)**2) / np.sum((no_k.log_obs - no_k.log_obs.mean())**2)
sp_all = stats.spearmanr(match_df.log_obs, match_df.log_model).statistic
sp_nk = stats.spearmanr(no_k.log_obs, no_k.log_model).statistic

print(f'Total observed rivers: {len(match_df)}')
print(f'Matched (rel_err<5%): {(match_df.rel_err < 0.05).sum()}')
print(f'All (n={len(match_df)}): R²={r2_all:.3f}, ρ={sp_all:.3f}')
print(f'No Kuantan (n={len(no_k)}): R²={r2_nk:.3f}, ρ={sp_nk:.3f}')
print(f'Paper: R²≈0.71 (n=51, no Kuantan)')
print()

# Check duplicates
dups = match_df[match_df.duplicated(subset='outfall_idx', keep=False)]
if len(dups) > 0:
    print(f'Duplicate outfall assignments ({len(dups)} rows):')
    print(dups[['name','outfall_idx','model_annual','outfall_ME']].to_string(index=False))
else:
    print('No duplicate outfall assignments')

# Save
match_df.to_csv('data/processed/observed_flux_matched_S3.csv', index=False)
print(f'\nSaved to data/processed/observed_flux_matched_S3.csv')
print(f'Unique outfalls: {match_df.outfall_idx.nunique()}')
