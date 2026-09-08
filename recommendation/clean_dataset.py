import pandas as pd

# Load merged dataset
df = pd.read_csv("datasets/master_questions.csv")

# Fill missing values from alternate column names
df["question_id"] = df["question_id"].fillna(df["id"])
df["option_a"] = df["option_a"].fillna(df["A"])
df["option_b"] = df["option_b"].fillna(df["B"])
df["option_c"] = df["option_c"].fillna(df["C"])
df["option_d"] = df["option_d"].fillna(df["D"])
df["correct_answer"] = df["correct_answer"].fillna(df["answer"])
df["topic"] = df["topic"].fillna(df["section"])
df["difficulty_level"] = df["difficulty_level"].fillna(df["difficulty"])

# Keep only the required columns
clean_df = df[
    [
        "question_id",
        "question",
        "option_a",
        "option_b",
        "option_c",
        "option_d",
        "correct_answer",
        "domain",
        "topic",
        "difficulty_level",
    ]
]

# Remove rows without questions
clean_df = clean_df.dropna(subset=["question"])

# Save cleaned dataset
clean_df.to_csv("datasets/clean_questions.csv", index=False)

print("Dataset cleaned successfully!")
print(clean_df.head())
print("\nTotal Questions:", len(clean_df))
print("\nColumns:")
print(clean_df.columns)