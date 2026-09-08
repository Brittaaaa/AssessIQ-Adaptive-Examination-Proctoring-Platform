import pandas as pd

# Load cleaned dataset
df = pd.read_csv("datasets/clean_questions.csv")


def normalize(value):
    """
    Convert all difficulty values to a 1-10 scale.
    """

    if pd.isna(value):
        return 5

    value = str(value).strip().lower()

    if value == "easy":
        return 3

    if value == "medium":
        return 6

    if value == "hard":
        return 9

    try:
        value = float(value)

        if value < 1:
            return 1

        if value > 10:
            return 10

        return int(value)

    except:
        return 5


# Apply normalization
df["difficulty_level"] = df["difficulty_level"].apply(normalize)

# Save dataset
df.to_csv("datasets/clean_questions.csv", index=False)

print("Difficulty normalization completed!")

print("\nSample difficulties:")

print(df["difficulty_level"].head(20))