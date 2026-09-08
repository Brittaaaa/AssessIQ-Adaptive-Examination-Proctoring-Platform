import pandas as pd
import joblib

from sentence_transformers import SentenceTransformer

print("Loading dataset...")

df = pd.read_csv("datasets/clean_questions.csv")

df = df.fillna("")

print("Loading Sentence Transformer model...")

model = SentenceTransformer("all-MiniLM-L6-v2")

print("Generating embeddings...")

# Create richer text for embeddings
df["combined_text"] = (
    df["question"].astype(str)
    + " [SEP] "
    + df["topic"].astype(str)
    + " [SEP] "
    + df["domain"].astype(str)
    + " [SEP] Difficulty "
    + df["difficulty_level"].astype(str)
)

embeddings = model.encode(
    df["combined_text"].tolist(),
    show_progress_bar=True,
    convert_to_numpy=True
)


joblib.dump(df, "models/questions_semantic.pkl")
joblib.dump(embeddings, "models/question_embeddings.pkl")

print("Semantic model created successfully!")
print("Total Questions:", len(df))
print("Embedding Shape:", embeddings.shape)