# cbr.py
import pandas as pd
import numpy as np

SYMPTOM_COLS = ["acne","blackheads","dryness","redness","dark_spots","aging"]

def load_cases(path="cases.csv"):
    df = pd.read_csv(path)
    # ensure types
    for c in SYMPTOM_COLS:
        if c in df.columns:
            df[c] = df[c].fillna(0).astype(int)
    return df

def age_similarity(age1, age2):
    diff = abs(age1 - age2)
    sim = max(0, 1 - diff/100)  # normalize over 100 years
    return sim

def skin_type_similarity(skin_new, skin_case):
    return 1.0 if str(skin_new).lower() == str(skin_case).lower() else 0.0

def symptom_jaccard(sym_new, sym_case):
    # sym_new & sym_case are dicts or arrays with same symptom keys
    a = np.array([int(sym_new.get(k,0)) for k in SYMPTOM_COLS])
    b = np.array([int(sym_case.get(k,0)) for k in SYMPTOM_COLS])
    inter = np.sum((a==1) & (b==1))
    union = np.sum((a==1) | (b==1))
    if union == 0:
        return 0.0
    return inter/union

def compute_similarity(new_case, case_row, weights=None):
    if weights is None:
        weights = {"skin":0.2, "age":0.1, "symptom":0.7}
    sim_skin = skin_type_similarity(new_case["skin_type"], case_row["skin_type"])
    sim_age = age_similarity(float(new_case["age"]), float(case_row["age"]))
    sym_new = {k:int(new_case.get(k,0)) for k in SYMPTOM_COLS}
    sym_case = {k:int(case_row.get(k,0)) for k in SYMPTOM_COLS}
    sim_sym = symptom_jaccard(sym_new, sym_case)
    total = weights["skin"]*sim_skin + weights["age"]*sim_age + weights["symptom"]*sim_sym
    return {
        "sim_total": total,
        "sim_skin": sim_skin,
        "sim_age": sim_age,
        "sim_symptom": sim_sym
    }

def retrieve(new_case, df_cases, k=3, weights=None):
    results = []
    for _, row in df_cases.iterrows():
        sims = compute_similarity(new_case, row, weights=weights)
        results.append({
            "id": row["id"],
            "age": row["age"],
            "gender": row.get("gender",""),
            "skin_type": row["skin_type"],
            "solution": row.get("solution",""),
            "notes": row.get("notes",""),
            **sims
        })
    res_df = pd.DataFrame(results)
    res_df = res_df.sort_values("sim_total", ascending=False)
    return res_df.head(k)

def retain_case(new_case, path="cases.csv"):
    df = load_cases(path)
    # generate new id
    try:
        max_id = int(df["id"].max())
    except:
        max_id = 0
    new_id = max_id + 1
    # prepare new row dict
    row = {
        "id": new_id,
        "age": new_case.get("age"),
        "gender": new_case.get("gender"),
        "skin_type": new_case.get("skin_type"),
        "acne": int(new_case.get("acne",0)),
        "blackheads": int(new_case.get("blackheads",0)),
        "dryness": int(new_case.get("dryness",0)),
        "redness": int(new_case.get("redness",0)),
        "dark_spots": int(new_case.get("dark_spots",0)),
        "aging": int(new_case.get("aging",0)),
        "solution": new_case.get("solution",""),
        "notes": new_case.get("notes","")
    }
    df = df.append(row, ignore_index=True)
    df.to_csv(path, index=False)
    return new_id
