# app.py
import streamlit as st
import pandas as pd
from cbr import load_cases, retrieve, retain_case
from utils import create_sample_if_missing

# Pastikan dataset tersedia
create_sample_if_missing("data/cases.csv")

st.set_page_config(page_title="CBR Treatment Kulit Wajah", layout="centered")

st.title("Sistem Rekomendasi Treatment Kulit Wajah (Case-Based Reasoning)")
st.markdown("Masukkan profil kulit & gejala, lalu sistem akan mencari kasus serupa dan memberikan rekomendasi treatment wajah.")

# =====================================
# INPUT PENGGUNA
# =====================================

st.sidebar.header("Masukkan Profil Anda")
age = st.sidebar.number_input("Umur", min_value=8, max_value=100, value=25)
gender = st.sidebar.selectbox("Gender", ["female", "male", "other"])
skin_type = st.sidebar.selectbox("Tipe Kulit", ["oily", "dry", "combination", "sensitive", "normal"])

st.sidebar.markdown("### Gejala / Masalah Kulit")
acne = st.sidebar.checkbox("Jerawat (Acne)")
blackheads = st.sidebar.checkbox("Komedo (Blackheads)")
dryness = st.sidebar.checkbox("Kekeringan (Dryness)")
redness = st.sidebar.checkbox("Kemerahan (Redness)")
dark_spots = st.sidebar.checkbox("Noda hitam (Dark Spots)")
aging = st.sidebar.checkbox("Penuaan / Garis Halus (Aging)")

# Tombol proses CBR
proceed = st.sidebar.button("Cari Rekomendasi")

# =====================================
# PROSES RETRIEVE
# =====================================

if proceed:

    new_case = {
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

    df = load_cases("data/cases.csv")
    topk = retrieve(new_case, df, k=3)

    st.subheader("🔍 Kasus yang Paling Mirip (Retrieve)")
    for idx, row in topk.iterrows():
        st.markdown(f"**Case ID:** {int(row['id'])} — Similarity: **{row['sim_total']:.3f}**")
        st.write(f"- Umur: {row['age']}, Gender: {row['gender']}, Kulit: {row['skin_type']}")
        st.write(f"- Solusi: {row['solution']}")
        st.write(f"- Catatan: {row['notes']}")
        st.write("---")

    # =====================================
    # REUSE – rekomendasi awal
    # =====================================
    best = topk.iloc[0]

    st.subheader("✨ Rekomendasi Awal Sistem (Reuse)")
    st.info(best['solution'])

    # =====================================
    # REVISE – user accept/reject
    # =====================================

    st.write("Apakah rekomendasi ini sesuai untuk kondisi Anda?")
    choice = st.radio(
        "Pilih salah satu:",
        ("Terima rekomendasi", "Tolak dan masukkan rekomendasi sendiri")
    )

    if choice == "Tolak dan masukkan rekomendasi sendiri":
        new_solution = st.text_area(
            "Masukkan rekomendasi treatment wajah versi Anda:",
            placeholder="Contoh: gunakan moisturizer non-fragrance + serum niacinamide..."
        )
    else:
        new_solution = best['solution']

    # =====================================
    # RETAIN – simpan ke dataset
    # =====================================

    if st.button("Simpan Kasus ke Dataset (Retain)"):

        save_case = new_case.copy()
        save_case["solution"] = new_solution

        # Catatan berdasarkan pilihan user
        if choice == "Terima rekomendasi":
            save_case["notes"] = f"User accepted solution from case {int(best['id'])}"
        else:
            save_case["notes"] = f"User rejected solution from case {int(best['id'])} and added custom solution"

        new_id = retain_case(save_case, path="data/cases.csv")

        st.success(f"Kasus baru berhasil disimpan dengan ID {new_id}.")
        st.balloons()

# =====================================
# ADMIN PANEL
# =====================================

st.sidebar.header("Admin")
if st.sidebar.checkbox("Tampilkan semua kasus"):
    df_all = load_cases("data/cases.csv")
    st.subheader("📄 Semua Kasus di Dataset")
    st.dataframe(df_all)
