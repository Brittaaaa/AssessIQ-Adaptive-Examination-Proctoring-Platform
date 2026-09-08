import joblib
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Load data
questions = joblib.load("models/questions_semantic.pkl")
embeddings = joblib.load("models/question_embeddings.pkl")


def recommend(question_id, top_n=5):
    # Find the row index from question_id
    matches = questions[questions["question_id"] == question_id]

    if matches.empty:
        print("Question ID not found!")
        return

    question_index = matches.index[0]

    # Get embedding of selected question
    query_embedding = embeddings[question_index].reshape(1, -1)

    # Compute similarity
    similarities = cosine_similarity(query_embedding, embeddings)[0]

    # Sort by similarity
    ranked = np.argsort(similarities)[::-1]

    selected = questions.iloc[question_index]

    print("\n==========================================")
    print("SELECTED QUESTION")
    print("==========================================")
    print(selected["question"])
    print(f"\nQuestion ID : {selected['question_id']}")
    print(f"Domain      : {selected['domain']}")
    print(f"Topic       : {selected['topic']}")
    print(f"Difficulty  : {selected['difficulty_level']}")

    print("\n==========================================")
    print("RECOMMENDED QUESTIONS")
    print("==========================================")

    count = 0

    for idx in ranked:

        if idx == question_index:
            continue

        row = questions.iloc[idx]
        # Keep only questions from the same domain
        if row["domain"] != selected["domain"]:
          continue
        # Skip questions with very different difficulty
        selected_difficulty = float(selected["difficulty_level"])
        current_difficulty = float(row["difficulty_level"])

        if abs(current_difficulty - selected_difficulty) > 2:
          continue

        print("\n--------------------------------------")
        print(f"Similarity : {similarities[idx]:.4f}")
        print(f"Question ID: {row['question_id']}")
        print(f"Domain     : {row['domain']}")
        print(f"Topic      : {row['topic']}")
        print(f"Difficulty : {row['difficulty_level']}")
        print(f"Question   : {row['question']}")

        count += 1

        if count == top_n:
            break


if __name__ == "__main__":
    recommend("AIML_0093")