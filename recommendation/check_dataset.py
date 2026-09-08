import pandas as pd

df = pd.read_csv("datasets/clean_questions.csv")

# Questions without options
coding = df[
    df["option_a"].isna() |
    (df["option_a"].astype(str).str.strip() == "")
]

print("Coding/Non-MCQ Questions:", len(coding))

print("\nSample:\n")

print(
    coding[
        ["question", "correct_answer"]
    ].head(10)
)