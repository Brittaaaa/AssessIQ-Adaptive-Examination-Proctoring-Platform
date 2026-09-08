import json
import os
import random
from datetime import datetime, timezone

import pandas as pd


VALID_DOMAINS = {
    "aiml": "AI & Machine Learning",
    "data_analytics": "Data Analytics",
    "fullstack": "Full Stack",
    "devops": "DevOps",
    "aptitude": "Aptitude",
}


VALID_DIFFICULTIES = {
    "easy": 1200,
    "medium": 1500,
    "hard": 1800,
    "adaptive": 1500,
}


class ExamService:

    def __init__(self, db, datasets):
        self.db = db
        self.questions = self._load(datasets)
        self.last_violations = {}


    # =========================================================
    # LOAD QUESTIONS
    # =========================================================

    def _load(self, path):

        files = {
            "aiml": "aiml_questions_balanced_final.csv",
            "data_analytics": "data_analyst_questions_balanced_final.csv",
            "fullstack": "fullstack_questions_balanced_final.csv",
            "devops": "devops_questions_balanced_final.csv",
            "aptitude": "aptitude_questions_balanced_final.csv",
        }

        rows = []

        for domain, file in files.items():

            data = pd.read_csv(
                os.path.join(path, file)
            ).fillna("")

            for _, r in data.iterrows():

                if all(
                    str(r.get(k, "")).strip()
                    for k in (
                        "question",
                        "option_a",
                        "option_b",
                        "option_c",
                        "option_d",
                        "correct_answer",
                    )
                ):

                    rows.append({
                        "question_id": str(
                            r.get("question_id", "")
                        ),

                        "question": str(
                            r["question"]
                        ),

                        "options": {
                            k: str(
                                r[
                                    "option_"
                                    + k.lower()
                                ]
                            )
                            for k in "ABCD"
                        },

                        "correct_answer": str(
                            r["correct_answer"]
                        ).strip().upper(),

                        "domain": domain,

                        "topic": str(
                            r.get(
                                "topic",
                                "General Concepts"
                            )
                        ),

                        "difficulty_level": float(
                            r.get(
                                "difficulty_level",
                                5
                            ) or 5
                        ),
                    })

        return rows


    # =========================================================
    # SELECT QUESTIONS
    # =========================================================

    def _select(self, domain, difficulty):

        pool = [
            q
            for q in self.questions
            if q["domain"] == domain
        ]

        target = {
            "easy": 3,
            "medium": 5,
            "hard": 8,
            "adaptive": 5,
        }[difficulty]

        filtered = [
            q
            for q in pool
            if abs(
                q["difficulty_level"] - target
            ) <= 2
        ] or pool

        random.shuffle(filtered)

        chosen = filtered[:20]

        while len(chosen) < 20 and pool:

            chosen.append(
                random.choice(pool)
            )

        return chosen


    # =========================================================
    # CREATE EXAM
    # =========================================================

    def create_exam(
        self,
        uid,
        domain,
        difficulty
    ):

        return self.db.create_exam(
            uid,
            domain,
            difficulty,
            VALID_DIFFICULTIES[difficulty],
            self._select(
                domain,
                difficulty
            )
        )


    # =========================================================
    # START EXAM
    # =========================================================

    def ensure_started(self, eid):

        ex = self.db.get_exam(
            eid,
            self._owner(eid)
        )

        if ex["status"] == "VERIFIED":
            self.db.start_exam(eid)


    # =========================================================
    # GET EXAM OWNER
    # =========================================================

    def _owner(self, eid):

        # Ownership was validated by the request;
        # retrieve directly only for state transition helper.

        with self.db.connection() as c:

            return c.execute(
                """
                SELECT student_id
                FROM exams
                WHERE id=?
                """,
                (eid,)
            ).fetchone()[0]


    # =========================================================
    # EXAM VIEW
    # =========================================================

    def exam_view(self, eid):

        with self.db.connection() as c:

            ex = dict(
                c.execute(
                    """
                    SELECT *
                    FROM exams
                    WHERE id=?
                    """,
                    (eid,)
                ).fetchone()
            )

        qs = json.loads(
            ex["questions_json"]
        )

        answers = {
            a["question_index"]:
                a["selected_answer"]

            for a in self.db.answers(eid)
        }

        started = datetime.fromisoformat(
            ex["started_at"]
        )

        elapsed = (
            datetime.now(timezone.utc)
            - started
        ).total_seconds()

        return {
            "id": eid,

            "domain": ex["domain"],

            "difficulty": ex["difficulty"],

            "duration": ex["duration_seconds"],

            "remaining": max(
                0,
                int(
                    ex["duration_seconds"]
                    - elapsed
                )
            ),

            "questions": [
                {
                    "question": q["question"],
                    "options": q["options"],
                    "topic": q["topic"],
                }
                for q in qs
            ],

            "answers": answers,

            "warnings": ex["warning_count"],
        }


    # =========================================================
    # SAVE ANSWER
    # =========================================================

    def save_answer(
        self,
        eid,
        index,
        answer
    ):

        with self.db.connection() as c:

            qs = json.loads(
                c.execute(
                    """
                    SELECT questions_json
                    FROM exams
                    WHERE id=?
                    """,
                    (eid,)
                ).fetchone()[0]
            )

        q = qs[index]

        self.db.save_answer(
            eid,
            index,
            q["question_id"],
            answer,
            q["correct_answer"]
        )

        return min(
            index + 1,
            len(qs) - 1
        )


    # =========================================================
    # PROCTORING
    # =========================================================

    def record_proctor_result(
        self,
        eid,
        result
    ):

        violations = []

        if not result.get("camera"):

            violations.append(
                (
                    "CAMERA_DISCONNECTED",
                    "Camera disconnected."
                )
            )

        elif not result.get("face"):

            violations.append(
                (
                    "FACE_MISSING",
                    "Face not detected."
                )
            )

        elif result.get("person_count") != 1:

            violations.append(
                (
                    "MULTIPLE_PERSON",
                    "Multiple people or no candidate detected."
                )
            )

        elif result.get("phone"):

            violations.append(
                (
                    "PHONE",
                    "Mobile phone detected."
                )
            )

        elif result.get("book"):

            violations.append(
                (
                    "BOOK",
                    "Book detected."
                )
            )

        elif not result.get("eye"):

            violations.append(
                (
                    "LOOKING_AWAY",
                    "Please focus on the examination screen."
                )
            )


        now = datetime.now(
            timezone.utc
        ).timestamp()

        warning = None


        for kind, msg in violations:

            key = (
                eid,
                kind
            )

            if (
                now
                - self.last_violations.get(
                    key,
                    0
                )
                >= 12
            ):

                self.last_violations[key] = now

                self.db.add_event(
                    eid,
                    kind,
                    msg,
                    True
                )

                warning = {
                    "type": kind,
                    "message": msg,
                    "count": self.db.warning_count(eid),
                }


        count = self.db.warning_count(
            eid
        )

        auto = count >= 3


        if auto:

            self.submit(
                eid,
                "MAX_WARNINGS"
            )


        return {
            **result,

            "warnings": count,

            "warning": warning,

            "auto_submitted": auto,
        }


    # =========================================================
    # SUBMIT EXAM
    # =========================================================

    def submit(
        self,
        eid,
        reason
    ):

        with self.db.connection() as c:

            ex = dict(
                c.execute(
                    """
                    SELECT *
                    FROM exams
                    WHERE id=?
                    """,
                    (eid,)
                ).fetchone()
            )


        # Already submitted

        if ex["status"] in (
            "SUBMITTED",
            "AUTO_SUBMITTED"
        ):

            return self.report(eid)


        qs = json.loads(
            ex["questions_json"]
        )


        answers = {
            a["question_index"]: a
            for a in self.db.answers(eid)
        }


        # =====================================================
        # SCORE CALCULATION
        # =====================================================

        correct = sum(
            1
            for a in answers.values()
            if a["is_correct"]
        )


        answered = len([
            a
            for a in answers.values()
            if a["selected_answer"]
        ])


        total = len(qs)

        incorrect = (
            answered
            - correct
        )

        unanswered = (
            total
            - answered
        )


        score = round(
            correct * 100 / total,
            1
        ) if total else 0


        # =====================================================
        # KNOWLEDGE LEVEL
        # =====================================================

        if score >= 85:

            level = "Advanced"

        elif score >= 70:

            level = "Strong"

        elif score >= 50:

            level = "Intermediate"

        else:

            level = "Beginner"


        # =====================================================
        # TOPIC PERFORMANCE
        # =====================================================

        topics = []


        unique_topics = sorted(
            {
                q.get(
                    "topic",
                    "General Concepts"
                )
                for q in qs
            }
        )


        for topic in unique_topics:

            indices = [
                i
                for i, q in enumerate(qs)
                if q.get(
                    "topic",
                    "General Concepts"
                ) == topic
            ]


            good = sum(
                1
                for i in indices
                if answers.get(
                    i,
                    {}
                ).get(
                    "is_correct"
                )
            )


            topic_total = len(indices)


            percentage = (
                round(
                    good * 100 / topic_total
                )
                if topic_total
                else 0
            )


            topics.append({
                "topic": topic,

                "total": topic_total,

                "correct": good,

                "percentage": percentage,
            })


        # =====================================================
        # SAVE RESULT
        # =====================================================

        self.db.submit(
            eid,

            {
                "status":
                    "AUTO_SUBMITTED"
                    if reason != "MANUAL"
                    else "SUBMITTED",

                "score": score,

                "correct": correct,

                "incorrect": incorrect,

                "unanswered": unanswered,

                "level": level,

                "reason": reason,
            },

            topics
        )


        return self.report(eid)


    # =========================================================
    # REAL PERFORMANCE REPORT
    # =========================================================

    def report(self, eid):

        # -----------------------------------------------------
        # EXAM DATA
        # -----------------------------------------------------

        with self.db.connection() as c:

            ex = dict(
                c.execute(
                    """
                    SELECT *
                    FROM exams
                    WHERE id=?
                    """,
                    (eid,)
                ).fetchone()
            )


        # -----------------------------------------------------
        # QUESTIONS
        # -----------------------------------------------------

        qs = json.loads(
            ex["questions_json"]
        )


        # -----------------------------------------------------
        # ANSWERS
        # -----------------------------------------------------

        answers = {
            a["question_index"]: a
            for a in self.db.answers(eid)
        }


        # -----------------------------------------------------
        # TOPIC PERFORMANCE
        # -----------------------------------------------------

        topics = self.db.topic_performance(
            eid
        )


        # -----------------------------------------------------
        # STRENGTHS
        # -----------------------------------------------------

        strengths = [
            x
            for x in topics
            if x["percentage"] >= 70
        ]


        # -----------------------------------------------------
        # WEAKNESSES
        # -----------------------------------------------------

        weaknesses = [
            x
            for x in topics
            if x["percentage"] < 70
        ]


        # -----------------------------------------------------
        # QUESTION-BY-QUESTION REVIEW
        # -----------------------------------------------------

        question_review = []


        for index, question in enumerate(qs):

            answer = answers.get(
                index,
                {}
            )


            selected = answer.get(
                "selected_answer"
            )


            correct_answer = question.get(
                "correct_answer"
            )


            is_correct = None


            if selected:

                is_correct = (
                    str(selected).upper()
                    == str(correct_answer).upper()
                )


            question_review.append({

                "number": index + 1,

                "question":
                    question.get(
                        "question",
                        ""
                    ),

                "topic":
                    question.get(
                        "topic",
                        "General Concepts"
                    ),

                "options":
                    question.get(
                        "options",
                        {}
                    ),

                "selected_answer":
                    selected,

                "correct_answer":
                    correct_answer,

                "is_correct":
                    is_correct,

            })


        # -----------------------------------------------------
        # REAL SCORE
        # -----------------------------------------------------

        score = float(
            ex.get("score") or 0
        )


        level = (
            ex.get("knowledge_level")
            or "Beginner"
        )


        # -----------------------------------------------------
        # PERFORMANCE INSIGHT
        # -----------------------------------------------------

        if score >= 85:

            insight = (
                "Excellent performance. You demonstrated "
                "a strong understanding across most areas "
                "of this assessment."
            )

        elif score >= 70:

            insight = (
                "Good performance with a solid understanding "
                "of the core concepts. Focus on weaker topics "
                "to improve further."
            )

        elif score >= 50:

            insight = (
                "You have a developing understanding of the "
                "subject. Targeted practice in weaker areas "
                "will significantly improve your performance."
            )

        else:

            insight = (
                "This assessment highlights important areas "
                "for improvement. Review the fundamentals "
                "and practice topic-wise questions before "
                "attempting another assessment."
            )


        # -----------------------------------------------------
        # BEST TOPIC
        # -----------------------------------------------------

        best_topic = None


        if topics:

            best_topic = max(
                topics,
                key=lambda x:
                    x.get(
                        "percentage",
                        0
                    )
            )


        # -----------------------------------------------------
        # WEAKEST TOPIC
        # -----------------------------------------------------

        weakest_topic = None


        if topics:

            weakest_topic = min(
                topics,
                key=lambda x:
                    x.get(
                        "percentage",
                        0
                    )
            )


        # -----------------------------------------------------
        # PERFORMANCE MESSAGE
        # -----------------------------------------------------

        if best_topic:

            strongest_message = (
                f"Your strongest area was "
                f"{best_topic['topic']} with "
                f"{best_topic['percentage']}% accuracy."
            )

        else:

            strongest_message = (
                "Topic-wise performance is not available."
            )


        if weakest_topic:

            improvement_message = (
                f"Focus on {weakest_topic['topic']}, "
                f"where your current accuracy was "
                f"{weakest_topic['percentage']}%."
            )

        else:

            improvement_message = (
                "No specific improvement area was identified."
            )


        # -----------------------------------------------------
        # FINAL REPORT
        # -----------------------------------------------------

        return {

            "exam": ex,

            "topics": topics,

            "strengths": strengths,

            "weaknesses": weaknesses,

            "events":
                self.db.events(eid),

            "question_review":
                question_review,

            "insight":
                insight,

            "strongest_message":
                strongest_message,

            "improvement_message":
                improvement_message,

            "best_topic":
                best_topic,

            "weakest_topic":
                weakest_topic,

            "summary": (
                f"Performance was {level} with "
                f"{ex.get('correct_count') or 0} "
                f"correct answers out of "
                f"{len(qs)} questions."
            ),
        }