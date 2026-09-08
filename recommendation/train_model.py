import pandas as pd
import joblib

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load cleaned dataset
df = pd.read_csv("datasets/clean_questions.csv")

# Fill missing values
df["question"] = df["question"].fillna("")
df["topic"] = df["topic"].fillna("")
df["domain"] = df["domain"].fillna("")
df["difficulty_level"] = df["difficulty_level"].fillna("")

# Create one combined text column
df["combined_text"] = (
    df["question"].astype(str)
    + " "
    + df["topic"].astype(str)
    + " "
    + df["domain"].astype(str)
    + " "
    + df["difficulty_level"].astype(str)
)

# TF-IDF Vectorizer
vectorizer = TfidfVectorizer(stop_words="english")

tfidf_matrix = vectorizer.fit_transform(df["combined_text"])

# Cosine Similarity
similarity_matrix = cosine_similarity(tfidf_matrix)

# Save everything
joblib.dump(vectorizer, "models/tfidf_vectorizer.pkl")
joblib.dump(similarity_matrix, "models/similarity_matrix.pkl")
joblib.dump(df, "models/questions.pkl")

print("Model trained successfully!")
print("Questions:", len(df))
print("TF-IDF shape:", tfidf_matrix.shape)