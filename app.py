import streamlit as st
import pandas as pd
from cbr import retrieve_cases, retain_case

st.title("🔍 CBR Skincare Recommendation System")

# -----------------------------
# Input Pengguna
# -----------------------------
st.header("Masukkan Kondisi Kulit Anda")

skin = st.text_input("Jenis kulit (contoh: oily, dry, combination)")
age = st.number_input("Usia", min_value=10, max_value=80, step=1)
symptoms = st.text_input("Keluhan (jerawat, kusam, bruntusan)")

if st.button("Cari Rekomendasi"):
    if skin == "" or symptoms == "":
        st.warning("Mohon masukkan semua data.")
        st.stop()

    user_input = {
        "skin_type": skin,
        "age": age,
        "symptoms": symptoms
    }

    results = retrieve_cases(user_input, "cases.csv")

    st.subheader("3 Kasus Paling Mirip")
    top3 = results.head(3)

    for i, row in top3.iterrows():
        st.write("---")
        st.write(f"**Case ID:** {row['case_id']}")
        st.write(f"Similarity: **{row['similarity']}**")
        st.write(f"Skin: {row['skin_type']}")
        st.write(f"Age: {row['age']}")
        st.write(f"Symptoms: {row['symptoms']}")
        st.write(f"Solution: **{row['solution']}**")

        # -----------------------------
        # Feedback user (Revise)
        # -----------------------------
        feedback = st.radio(
            f"Apakah solusi dari Case {row['case_id']} cocok?",
            ["Ya", "Tidak"],
            key=f"feedback_{i}"
        )

        if feedback == "Ya":
            st.success(f"Solusi dari Case {row['case_id']} diterima.")
        else:
            st.warning("Masukkan solusi baru:")
            new_solution = st.text_input("Solusi Baru", key=f"solution_{i}")

            if st.button(f"Simpan revisi Case baru {i}"):
                save_case = {
                    "skin_type": skin,
                    "age": age,
                    "symptoms": symptoms,
                    "solution": new_solution,
                }

                new_id = retain_case(save_case, "cases.csv")

                st.success(f"Kasus baru berhasil disimpan dengan ID {new_id}.")
                st.balloons()
