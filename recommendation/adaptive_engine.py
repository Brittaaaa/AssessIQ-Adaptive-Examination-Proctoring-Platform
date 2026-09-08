import joblib
import numpy as np

# Load dataset
questions = joblib.load("models/questions_semantic.pkl")


class Student:

    def __init__(self, student_id, domain):

        self.student_id = student_id
        self.domain = domain
        self.current_difficulty = 5
        self.answered_questions = []
        self.score = 0

    def correct_answer(self):
        self.score += 1
        self.current_difficulty = min(10, self.current_difficulty + 1)

    def wrong_answer(self):
        self.current_difficulty = max(1, self.current_difficulty - 1)

    def add_answered_question(self, question_id):
        self.answered_questions.append(question_id)

def get_first_question(student):

    # Filter by selected domain
    domain_questions = questions[
        questions["domain"] == student.domain
    ]

    # Remove already answered questions
    domain_questions = domain_questions[
        ~domain_questions["question_id"].isin(student.answered_questions)
    ]

    # Keep questions within ±1 difficulty
    filtered = domain_questions[
        abs(domain_questions["difficulty_level"] - student.current_difficulty) <= 1
    ]

    # If none found, use all domain questions
    if len(filtered) == 0:
        filtered = domain_questions

    # Keep only MCQ questions
    filtered = filtered[
        filtered["option_a"].fillna("").str.strip() != ""
    ]

    filtered = filtered[
        filtered["option_b"].fillna("").str.strip() != ""
    ]

    filtered = filtered[
        filtered["option_c"].fillna("").str.strip() != ""
    ]

    filtered = filtered[
        filtered["option_d"].fillna("").str.strip() != ""
    ]

    # Randomly select one question
    question = filtered.sample(1).iloc[0]

    return question

def ask_question(student):

    # Get one question
    question = get_first_question(student)

    # Save question as answered
    student.add_answered_question(question["question_id"])

    print("\n====================================")
    print("QUESTION")
    print("====================================")

    print(question["question"])
    print()

    print("A.", question["option_a"])
    print("B.", question["option_b"])
    print("C.", question["option_c"])
    print("D.", question["option_d"])

    answer = input("\nEnter your answer (A/B/C/D): ").strip().upper()

    correct = str(question["correct_answer"]).strip().upper()

    if answer == correct:

        print("\n✅ Correct!")

        student.correct_answer()

    else:

        print("\n❌ Wrong!")

        print("Correct Answer :", correct)

        student.wrong_answer()

    print("\nCurrent Score      :", student.score)
    print("Current Difficulty :", student.current_difficulty)
    return
student = Student("S001", "AI/ML")

TOTAL_QUESTIONS = 10

for i in range(TOTAL_QUESTIONS):

    print(f"\n========== QUESTION {i+1} OF {TOTAL_QUESTIONS} ==========")

    ask_question(student)

print("\n====================================")
print("EXAM FINISHED")
print("====================================")

print("Student ID :", student.student_id)
print("Domain     :", student.domain)
print("Score      :", student.score, "/", TOTAL_QUESTIONS)
print("Final Difficulty :", student.current_difficulty)