# app.py
import streamlit as st
import pandas as pd
from cbr import load_cases, retrieve, retain_case
from utils import create_sample_if_missing

create_sample_if_missing()

st.set_page_config(page_title="Skincare CBR", layout="centered")

st.title("Sistem Rekomendasi Treatment Kulit Wajah (Case-Based Reasoning)")
st.markdown("Masukkan profil kulit & gejala, lalu sistem akan mencari kasus serupa dan merekomendasikan solusi.")

# Sidebar input
st.sidebar.header("Masukkan profil")
age = st.sidebar.number_input("Umur", min_value=8, max_value=100, value=25)
gender = st.sidebar.selectbox("Gender", ["female","male","other"])
skin_type = st.sidebar.selectbox("Tipe kulit", ["oily","dry","combination","sensitive","normal"])
st.sidebar.markdown("**Gejala / masalah** (centang jika ada)")
acne = st.sidebar.checkbox("Acne / Jerawat")
blackheads = st.sidebar.checkbox("Blackheads / Komedo")
dryness = st.sidebar.checkbox("Kekeringan")
redness = st.sidebar.checkbox("Kemerahan")
dark_spots = st.sidebar.checkbox("Noda / Dark spots")
aging = st.sidebar.checkbox("Tanda penuaan (garis halus)")

if st.sidebar.button("Cari Rekomendasi"):
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
    df = load_cases("cases.csv")
    topk = retrieve(new_case, df, k=3)
    st.subheader("Kasus yang paling mirip")
    for idx, row in topk.iterrows():
        st.markdown(f"**Case ID:** {int(row['id'])} — similarity: **{row['sim_total']:.3f}**")
        st.write(f"- Age: {row['age']}, Gender: {row['gender']}, Skin: {row['skin_type']}")
        st.write(f"- Solution: {row['solution']}")
        st.write(f"- Notes: {row['notes']}")
        st.write("---")
        
# Show best solution by highest similarity
best = topk.iloc[0]
st.subheader("Rekomendasi Awal (Reuse)")
st.info(best['solution'])

st.write("Apakah rekomendasi ini sesuai untuk kondisi Anda?")
choice = st.radio(
    "Pilih salah satu:",
    ("Terima rekomendasi", "Tolak dan gunakan rekomendasi sendiri")
)

if choice == "Tolak dan gunakan rekomendasi sendiri":
    new_solution = st.text_area(
        "Masukkan rekomendasi treatment wajah versi Anda:",
        placeholder="Contoh: Gunakan moisturizer tanpa fragrance + serum niacinamide..."
    )
else:
    new_solution = best['solution']  # langsung pakai solusi dari kasus mirip

if st.button("Simpan Ke Dataset (Retain)"):
    save_case = new_case.copy()
    save_case["solution"] = new_solution

    if choice == "Terima rekomendasi":
        save_case["notes"] = f"User accepted solution from case {int(best['id'])}"
    else:
        save_case["notes"] = f"User rejected solution from case {int(best['id'])} and provided custom solution"

    new_id = retain_case(save_case, path="data/cases.csv")

    st.success(f"Kasus baru berhasil disimpan dengan ID {new_id}.")
    st.balloons()


# Admin / lihat dataset
st.sidebar.header("Admin")
if st.sidebar.checkbox("Tampilkan semua kasus"):
    df_all = load_cases("cases.csv")
    st.subheader("Semua kasus di database")
    st.dataframe(df_all)



