import os
import pandas as pd

DATASET_FOLDER = "datasets"

all_data = []

# Map filenames to domains
domain_mapping = {
    "aiml": "AI/ML",
    "aptitude": "Aptitude",
    "coding": "Coding",
    "data_analyst": "Data Analyst",
    "devops": "DevOps",
    "fullstack": "Full Stack",
    "placement": "Placement",
    "mcq": "General MCQ",
}

for file in os.listdir(DATASET_FOLDER):

    if not file.endswith(".csv"):
        continue

    # Skip generated files
    if file in ["master_questions.csv", "clean_questions.csv"]:
        continue

    file_path = os.path.join(DATASET_FOLDER, file)

    print(f"Reading {file}")

    df = pd.read_csv(file_path)

    if "domain" not in df.columns:

        assigned_domain = "Other"

        filename = file.lower()

        for key, value in domain_mapping.items():
            if key in filename:
                assigned_domain = value
                break

        df["domain"] = assigned_domain

    all_data.append(df)
    master_df = pd.concat(all_data, ignore_index=True)

master_df.to_csv("datasets/master_questions.csv", index=False)

print("Master dataset created successfully!")
print("Total Questions:", len(master_df))