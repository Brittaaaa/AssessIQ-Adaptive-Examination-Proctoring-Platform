import pandas as pd

# Load the master dataset
df = pd.read_csv("datasets/master_questions.csv")

# Display basic information
print("\n===== DATASET INFORMATION =====")
print(df.info())

print("\n===== FIRST 5 ROWS =====")
print(df.head())

print("\n===== COLUMN NAMES =====")
print(df.columns)

print("\n===== MISSING VALUES =====")
print(df.isnull().sum())

print("\n===== DUPLICATE ROWS =====")
print(df.duplicated().sum())