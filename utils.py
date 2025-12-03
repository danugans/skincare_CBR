# utils.py
import os

def ensure_data_folder():
    if not os.path.exists("data"):
        os.makedirs("data")

def create_sample_if_missing(path="cases.csv"):
    ensure_data_folder()
    if not os.path.exists(path):
        sample = """id,age,gender,skin_type,acne,blackheads,dryness,redness,dark_spots,aging,solution,notes
1,22,female,oily,1,1,0,0,0,0,"Cleanser + salicylic acid","Sample base case"
"""
        with open(path, "w") as f:
            f.write(sample)
