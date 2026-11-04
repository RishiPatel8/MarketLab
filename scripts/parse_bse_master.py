import zipfile
import io
import csv
import urllib.request

url = 'https://www.bseindia.com/downloads/Help/file/SCRIP.zip'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=15) as resp:
    zf = zipfile.ZipFile(io.BytesIO(resp.read()))

# 1. CI dict: ScripCode -> Company Name
ci = zf.read('SCRIP/CI261026.txt').decode('utf-8', errors='ignore')
ci_map = {}
for line in ci.splitlines()[2:]:
    parts = line.strip().split('\t')
    if len(parts) >= 2:
        ci_map[parts[0].strip()] = parts[1].strip()
print('CI map entries:', len(ci_map))

# 2. ISIN map from SCRIP_261026.TXT
txt = zf.read('SCRIP/SCRIP_261026.TXT').decode('utf-8', errors='ignore')
isin_map_by_sym = {}
isin_map_by_code = {}
for line in txt.splitlines():
    parts = line.split('|')
    if len(parts) > 17:
        raw_code = parts[0].strip()
        sym = parts[2].rstrip('#').strip().upper()
        isin = parts[17].strip()
        if isin and isin.startswith('IN'):
            isin_map_by_sym[sym] = isin
            if raw_code.startswith('1') and len(raw_code) == 6:
                derived = '5' + raw_code[1:]
                isin_map_by_code[derived] = isin
            else:
                isin_map_by_code[raw_code] = isin

# Also check BSE_EQ_SCRIP for ISINs
eq_file = [f for f in zf.namelist() if 'BSE_EQ_SCRIP' in f][0]
eq_content = zf.read(eq_file).decode('utf-8', errors='ignore')
eq_reader = csv.DictReader(io.StringIO(eq_content))
for r in eq_reader:
    raw_id = r.get('FinInstrmId', '').strip()
    sym = r.get('TckrSymb', '').rstrip('#').strip().upper()
    isin = r.get('ISIN', '').strip().upper()
    name = r.get('FinInstrmNm', '').strip()
    if isin and isin.startswith('IN'):
        isin_map_by_sym[sym] = isin
        if raw_id.startswith('1') and len(raw_id) == 6:
            derived = '5' + raw_id[1:]
            isin_map_by_code[derived] = isin
        else:
            isin_map_by_code[raw_id] = isin
        if raw_id not in ci_map and name:
            ci_map[raw_id] = name
            if raw_id.startswith('1') and len(raw_id) == 6:
                ci_map['5' + raw_id[1:]] = name

print('Total Scrips with ISIN by code:', len(isin_map_by_code))
print('Total Scrips with ISIN by sym:', len(isin_map_by_sym))

# 3. Check REG file
reg_file = [f for f in zf.namelist() if 'REG1_IND' in f or 'REG_IND' in f][0]
reg_content = zf.read(reg_file).decode('utf-8', errors='ignore')
reg_reader = csv.DictReader(io.StringIO(reg_content))
reg_items = list(reg_reader)
print('Total REG items:', len(reg_items))

active_items = [r for r in reg_items if r['Status'] == 'A']
print('Active items (Status == A):', len(active_items))
active_exclusive = [r for r in active_items if r['BSE Exclusive'].upper() == 'Y']
print('Active BSE Exclusive (Status == A and Exclusive == Y):', len(active_exclusive))
active_sme = [r for r in active_items if r['GroupName'] == 'M']
print('Active BSE SME (Group M):', len(active_sme))

# Sample 10 active items
for r in active_items[:10]:
    code = r['ScripCode']
    sym = r['ScripId']
    name = ci_map.get(code, 'Unknown')
    isin = isin_map_by_code.get(code) or isin_map_by_sym.get(sym)
    grp = r['GroupName']
    excl = r['BSE Exclusive']
    print(f'Code: {code}, Sym: {sym}, Group: {grp}, Excl: {excl}, ISIN: {isin}, Name: {name[:30]}')
