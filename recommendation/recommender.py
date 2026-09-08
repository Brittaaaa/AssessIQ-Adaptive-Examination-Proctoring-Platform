import joblib

# Load saved files
questions = joblib.load("models/questions.pkl")
similarity_matrix = joblib.load("models/similarity_matrix.pkl")


def recommend(question_index, n=5):
    """
    Recommend similar questions.
    """

    similarity_scores = list(enumerate(similarity_matrix[question_index]))

    similarity_scores = sorted(
        similarity_scores,
        key=lambda x: x[1],
        reverse=True
    )

    # Skip the first one (it's the same question)
    recommendations = similarity_scores[1:n+1]

    print("\nSelected Question:\n")
    print(questions.iloc[question_index]["question"])

    print("\nRecommended Questions:\n")

    for i, score in recommendations:

        print("---------------------------------------")

        print("Question ID :", questions.iloc[i]["question_id"])

        print("Domain      :", questions.iloc[i]["domain"])

        print("Topic       :", questions.iloc[i]["topic"])

        print("Difficulty  :", questions.iloc[i]["difficulty_level"])

        print("Similarity  :", round(score, 3))

        print("Question    :", questions.iloc[i]["question"])


if __name__ == "__main__":

    recommend(100)