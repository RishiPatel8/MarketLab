import os
import zipfile
import io
import csv

def build_bse_reference():
    ref_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend", "app", "data", "reference"))
    zip_path = os.path.join(ref_dir, "bse_scrip.zip")
    
    with zipfile.ZipFile(zip_path, "r") as zf:
        # 1. Company names from CI
        ci_name = [f for f in zf.namelist() if "CI" in f and f.endswith(".txt")][0]
        ci_content = zf.read(ci_name).decode("utf-8", errors="ignore")
        ci_map = {}
        for line in ci_content.splitlines()[2:]:
            parts = line.strip().split("\t")
            if len(parts) >= 2:
                ci_map[parts[0].strip()] = parts[1].strip()

        # 2. ISINs
        eq_name = [f for f in zf.namelist() if "BSE_EQ_SCRIP" in f][0]
        eq_content = zf.read(eq_name).decode("utf-8", errors="ignore")
        reader = csv.DictReader(io.StringIO(eq_content))
        isin_by_code = {}
        isin_by_sym = {}
        for r in reader:
            raw_id = r.get("FinInstrmId", "").strip()
            sym = r.get("TckrSymb", "").rstrip("#").strip().upper()
            isin = r.get("ISIN", "").strip().upper()
            name = r.get("FinInstrmNm", "").strip()
            if isin and isin.startswith("IN"):
                isin_by_sym[sym] = isin
                if raw_id.startswith("1") and len(raw_id) == 6:
                    code = "5" + raw_id[1:]
                    isin_by_code[code] = isin
                else:
                    isin_by_code[raw_id] = isin
                if raw_id not in ci_map and name:
                    ci_map[raw_id] = name
                    if raw_id.startswith("1") and len(raw_id) == 6:
                        ci_map["5" + raw_id[1:]] = name

        # 3. REG items
        reg_name = [f for f in zf.namelist() if "REG1_IND" in f or "REG_IND" in f][0]
        reg_content = zf.read(reg_name).decode("utf-8", errors="ignore")
        reg_reader = csv.DictReader(io.StringIO(reg_content))

        out_path = os.path.join(ref_dir, "bse_active_securities.csv")
        with open(out_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "SCRIP_CODE", "SCRIP_ID", "COMPANY_NAME", "ISIN_NUMBER", 
                "GROUP", "IS_BSE_EXCLUSIVE", "INSTRUMENT_TYPE", "STATUS"
            ])
            writer.writeheader()
            count = 0
            exclusive_count = 0
            sme_count = 0
            with_isin = 0
            for r in reg_reader:
                status = r.get("Status", "").strip().upper()
                if status != "A":
                    continue  # Active listings only
                code = r.get("ScripCode", "").strip()
                sym = r.get("ScripId", "").strip().upper()
                grp = r.get("GroupName", "").strip().upper()
                excl = r.get("BSE Exclusive", "").strip().upper() == "Y"
                
                name = ci_map.get(code) or ci_map.get(sym) or sym
                isin = isin_by_code.get(code) or isin_by_sym.get(sym) or ""
                
                inst_type = "SME_EQUITY" if grp == "M" else ("ETF" if grp == "E" else "EQUITY")
                
                writer.writerow({
                    "SCRIP_CODE": code,
                    "SCRIP_ID": sym,
                    "COMPANY_NAME": name,
                    "ISIN_NUMBER": isin,
                    "GROUP": grp,
                    "IS_BSE_EXCLUSIVE": str(excl),
                    "INSTRUMENT_TYPE": inst_type,
                    "STATUS": "ACTIVE"
                })
                count += 1
                if excl: exclusive_count += 1
                if grp == "M": sme_count += 1
                if isin: with_isin += 1

        print(f"Successfully generated {out_path}:")
        print(f"  Total Active BSE Securities: {count:,}")
        print(f"  BSE Exclusive: {exclusive_count:,}")
        print(f"  BSE SMEs (Group M): {sme_count:,}")
        print(f"  With Verified ISIN: {with_isin:,}")

if __name__ == "__main__":
    build_bse_reference()
