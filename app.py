# app.py
import streamlit as st
import pandas as pd
from cbr import load_cases, retrieve, retain_case
from utils import create_sample_if_missing

# Dataset
create_sample_if_missing("cases.csv")

st.set_page_config(page_title="CBR Treatment Kulit Wajah", layout="centered")

st.title("Sistem Rekomendasi Treatment Kulit Wajah (Case-Based Reasoning)")
st.markdown("Masukkan profil & gejala kulit, lalu sistem akan mencari kasus serupa.")

# ==========================================================
# SIAPKAN SESSION_STATE
# ==========================================================

if "retrieved" not in st.session_state:
    st.session_state.retrieved = False

if "topk" not in st.session_state:
    st.session_state.topk = None

if "best" not in st.session_state:
    st.session_state.best = None

if "new_case" not in st.session_state:
    st.session_state.new_case = None

# ==========================================================
# INPUT PENGGUNA
# ==========================================================

st.sidebar.header("Masukkan Profil Anda")
age = st.sidebar.number_input("Umur", min_value=8, max_value=100, value=25)
gender = st.sidebar.selectbox("Gender", ["female", "male", "other"])
skin_type = st.sidebar.selectbox("Tipe kulit", ["oily", "dry", "combination", "sensitive", "normal"])

st.sidebar.markdown("### Gejala / Masalah Kulit")
acne = st.sidebar.checkbox("Jerawat")
blackheads = st.sidebar.checkbox("Komedo")
dryness = st.sidebar.checkbox("Kulit Kering")
redness = st.sidebar.checkbox("Kemerahan")
dark_spots = st.sidebar.checkbox("Noda Hitam")
aging = st.sidebar.checkbox("Penuaan")

if st.sidebar.button("Cari Rekomendasi"):

    # Simpan input ke session
    st.session_state.new_case = {
        "age": age,
        "gender": gender,
        "skin_type": skin_type,
        "acne": int(acne),
        "blackheads": int(blackheads),
        "dryness": int(dryness),
        "redness": int(redness),
        "dark_spots": int(dark_spots),
        "aging": int(aging)
    }

    df = load_cases("cases.csv")
    st.session_state.topk = retrieve(st.session_state.new_case, df, k=3)
    st.session_state.best = st.session_state.topk.iloc[0]
    st.session_state.retrieved = True

# ==========================================================
# TAMPILKAN HASIL RETRIEVE
# ==========================================================

if st.session_state.retrieved:

    st.subheader("🔍 Kasus Paling Mirip (Retrieve)")
    for idx, row in st.session_state.topk.iterrows():
        st.markdown(f"**Case ID:** {int(row['id'])} — Similarity: **{row['sim_total']:.3f}**")
        st.write(f"- Umur: {row['age']}, Gender: {row['gender']}, Kulit: {row['skin_type']}")
        st.write(f"- Solusi: {row['solution']}")
        st.write(f"- Catatan: {row['notes']}")
        st.write("---")

    # ==========================================================
    # REUSE
    # ==========================================================

    best = st.session_state.best
    st.subheader("✨ Rekomendasi Awal Sistem (Reuse)")
    st.info(best['solution'])

    # ==========================================================
    # REVISE
    # ==========================================================

    st.write("Apakah rekomendasi ini sesuai untuk kondisi Anda?")
    choice = st.radio(
        "Pilih salah satu:",
        ("Terima rekomendasi", "Tolak dan gunakan rekomendasi sendiri")
    )

    if choice == "Tolak dan gunakan rekomendasi sendiri":
        new_solution = st.text_area(
            "Masukkan rekomendasi treatment versi Anda:",
            placeholder="Contoh: moisturizer tanpa fragrance + serum niacinamide..."
        )
    else:
        new_solution = best["solution"]

    # ==========================================================
    # RETAIN
    # ==========================================================

    if st.button("Simpan Kasus ke Dataset (Retain)"):

        save_case = st.session_state.new_case.copy()
        save_case["solution"] = new_solution

        if choice == "Terima rekomendasi":
            save_case["notes"] = f"User accepted solution from case {int(best['id'])}"
        else:
            save_case["notes"] = f"User rejected solution from case {int(best['id'])} and provided custom treatment"

        new_id = retain_case(save_case, path="cases.csv")

        st.success(f"Kasus baru disimpan dengan ID {new_id}.")
        st.balloons()

# ==========================================================
# ADMIN PANEL
# ==========================================================

st.sidebar.header("Admin")
if st.sidebar.checkbox("Tampilkan semua kasus"):
    df_all = load_cases("cases.csv")
    st.subheader("📄 Semua Kasus di Dataset")
    st.dataframe(df_all)
