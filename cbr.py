# cbr.py
import pandas as pd
import numpy as np

SYMPTOM_COLS = ["acne","blackheads","dryness","redness","dark_spots","aging"]

def load_cases(path="cases.csv"):
    df = pd.read_csv(path)
    for c in SYMPTOM_COLS:
        if c in df.columns:
            df[c] = df[c].fillna(0).astype(int)
    return df

def age_similarity(a1, a2):
    diff = abs(a1 - a2)
    return max(0, 1 - diff/100)

def skin_type_similarity(a, b):
    return 1.0 if str(a).lower() == str(b).lower() else 0.0

def symptom_jaccard(sym_new, sym_case):
    a = np.array([sym_new.get(k,0) for k in SYMPTOM_COLS])
    b = np.array([sym_case.get(k,0) for k in SYMPTOM_COLS])
    inter = np.sum((a == 1) & (b == 1))
    union = np.sum((a == 1) | (b == 1))
    return inter / union if union != 0 else 0

def compute_similarity(new_case, row):
    weights = {"skin":0.2, "age":0.1, "symptom":0.7}
    sim_skin = skin_type_similarity(new_case["skin_type"], row["skin_type"])
    sim_age = age_similarity(new_case["age"], row["age"])
    sym_new = {k:new_case[k] for k in SYMPTOM_COLS}
    sym_old = {k:row[k] for k in SYMPTOM_COLS}
    sim_sym = symptom_jaccard(sym_new, sym_old)

    total = (
        weights["skin"]*sim_skin +
        weights["age"]*sim_age +
        weights["symptom"]*sim_sym
    )
    
    return {
        "sim_total": total,
        "sim_skin": sim_skin,
        "sim_age": sim_age,
        "sim_symptom": sim_sym
    }

def retrieve(new_case, df_cases, k=3):
    results = []
    for _, row in df_cases.iterrows():
        sims = compute_similarity(new_case, row)
        results.append({**row.to_dict(), **sims})
    res_df = pd.DataFrame(results)
    return res_df.sort_values("sim_total", ascending=False).head(k)

def retain_case(new_case, path="cases.csv"):
    import pandas as pd
    # Load CSV aman
    try:
        df = pd.read_csv(path)
    except Exception:
        df = pd.DataFrame(columns=[
            "id","age","gender","skin_type","acne","blackheads",
            "dryness","redness","dark_spots","aging","solution","notes"
        ])

    # Tentukan ID baru
    if "id" not in df.columns or df.empty:
        new_id = 1
    else:
        try:
            new_id = int(df["id"].max()) + 1
        except:
            new_id = 1

    new_case["id"] = new_id

    # Tambahkan baris menggunakan concat (append sudah dihapus!)
    new_row = pd.DataFrame([new_case])
    df = pd.concat([df, new_row], ignore_index=True)

    # Simpan kembali
    df.to_csv(path, index=False)

    return new_id






