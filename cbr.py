import pandas as pd

# -----------------------------
# Hitung Jaccard Similarity
# -----------------------------
def jaccard_similarity(a, b):
    set_a = set(str(a).lower().split(','))
    set_b = set(str(b).lower().split(','))
    return len(set_a & set_b) / len(set_a | set_b) if len(set_a | set_b) > 0 else 0


# -----------------------------
# Hitung Total Similarity
# -----------------------------
def compute_similarity(user, case):
    w_skin = 0.5
    w_age = 0.2
    w_symptom = 0.3

    sim_skin = jaccard_similarity(user["skin_type"], case["skin_type"])
    sim_age = 1 - (abs(int(user["age"]) - int(case["age"])) / 100)
    sim_symptom = jaccard_similarity(user["symptoms"], case["symptoms"])

    total = (w_skin * sim_skin) + (w_age * sim_age) + (w_symptom * sim_symptom)

    return round(total, 4)


# -----------------------------
# Retrieve: ambil semua similarity
# -----------------------------
def retrieve_cases(user_input, path="cases.csv"):
    df = pd.read_csv(path)
    df["similarity"] = df.apply(lambda row: compute_similarity(user_input, row), axis=1)
    df_sorted = df.sort_values(by="similarity", ascending=False)
    return df_sorted


# -----------------------------
# Retain Case (FIX append)
# -----------------------------
def retain_case(case, path="cases.csv"):
    df = pd.read_csv(path)

    # Tentukan ID baru
    new_id = df["case_id"].max() + 1 if "case_id" in df else 1
    case["case_id"] = new_id

    # Convert dict → DataFrame
    new_row = pd.DataFrame([case])

    # GABUNGKAN → sudah ganti append
    df = pd.concat([df, new_row], ignore_index=True)

    # Simpan ulang
    df.to_csv(path, index=False)
    return new_id
