
import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone


class Database:

    def __init__(self, path):
        self.path = path


    # =========================================================
    # DATABASE CONNECTION
    # =========================================================

    @contextmanager
    def connection(self):

        conn = sqlite3.connect(self.path)

        conn.row_factory = sqlite3.Row

        try:
            yield conn
            conn.commit()

        finally:
            conn.close()


    # =========================================================
    # INITIALIZE DATABASE
    # =========================================================

    def initialize(self):

        with self.connection() as c:

            c.executescript(
                '''
                CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    created_at TEXT NOT NULL
                );


                CREATE TABLE IF NOT EXISTS exams (
                    id INTEGER PRIMARY KEY,
                    student_id INTEGER NOT NULL,
                    domain TEXT NOT NULL,
                    difficulty TEXT NOT NULL,
                    status TEXT NOT NULL,
                    started_at TEXT,
                    ended_at TEXT,
                    duration_seconds INTEGER NOT NULL,
                    score REAL,
                    correct_count INTEGER,
                    incorrect_count INTEGER,
                    unanswered_count INTEGER,
                    knowledge_level TEXT,
                    warning_count INTEGER NOT NULL DEFAULT 0,
                    submission_reason TEXT,
                    questions_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );


                CREATE TABLE IF NOT EXISTS exam_answers (
                    id INTEGER PRIMARY KEY,
                    exam_id INTEGER NOT NULL,
                    question_index INTEGER NOT NULL,
                    question_id TEXT,
                    selected_answer TEXT,
                    correct_answer TEXT,
                    is_correct INTEGER,
                    UNIQUE(exam_id, question_index)
                );


                CREATE TABLE IF NOT EXISTS proctoring_events (
                    id INTEGER PRIMARY KEY,
                    exam_id INTEGER NOT NULL,
                    event_type TEXT NOT NULL,
                    message TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );


                CREATE TABLE IF NOT EXISTS topic_performance (
                    id INTEGER PRIMARY KEY,
                    exam_id INTEGER NOT NULL,
                    topic TEXT NOT NULL,
                    total INTEGER NOT NULL,
                    correct INTEGER NOT NULL,
                    percentage REAL NOT NULL
                );
                '''
            )


    # =========================================================
    # CURRENT UTC TIME
    # =========================================================

    def now(self):

        return datetime.now(timezone.utc).isoformat()


    # =========================================================
    # STUDENT
    # =========================================================

    def get_or_create_student(self, username):

        with self.connection() as c:

            c.execute(
                '''
                INSERT OR IGNORE INTO students (
                    username,
                    created_at
                )
                VALUES (?, ?)
                ''',
                (
                    username,
                    self.now()
                )
            )

            row = c.execute(
                '''
                SELECT *
                FROM students
                WHERE username = ?
                ''',
                (username,)
            ).fetchone()

            return dict(row)


    # =========================================================
    # CREATE EXAM
    # =========================================================

    def create_exam(
        self,
        student_id,
        domain,
        difficulty,
        duration,
        questions
    ):

        with self.connection() as c:

            cur = c.execute(
                '''
                INSERT INTO exams (
                    student_id,
                    domain,
                    difficulty,
                    status,
                    duration_seconds,
                    questions_json,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''',
                (
                    student_id,
                    domain,
                    difficulty,
                    "CREATED",
                    duration,
                    json.dumps(questions),
                    self.now(),
                ),
            )

            exam_id = cur.lastrowid

            row = c.execute(
                '''
                SELECT *
                FROM exams
                WHERE id = ?
                AND student_id = ?
                ''',
                (
                    exam_id,
                    student_id
                )
            ).fetchone()

            return dict(row)


    # =========================================================
    # GET EXAM
    # =========================================================

    def get_exam(self, exam_id, student_id):

        with self.connection() as c:

            row = c.execute(
                '''
                SELECT *
                FROM exams
                WHERE id = ?
                AND student_id = ?
                ''',
                (
                    exam_id,
                    student_id
                )
            ).fetchone()

            return dict(row) if row else None


    # =========================================================
    # VERIFY EXAM
    # =========================================================

    def set_exam_verified(self, eid):

        with self.connection() as c:

            c.execute(
                '''
                UPDATE exams
                SET status = 'VERIFIED'
                WHERE id = ?
                ''',
                (eid,)
            )


    # =========================================================
    # START EXAM
    # =========================================================

    def start_exam(self, eid):

        with self.connection() as c:

            c.execute(
                '''
                UPDATE exams
                SET
                    status = 'IN_PROGRESS',
                    started_at = ?
                WHERE id = ?
                AND status = 'VERIFIED'
                ''',
                (
                    self.now(),
                    eid
                )
            )


    # =========================================================
    # SAVE ANSWER
    # =========================================================

    def save_answer(
        self,
        eid,
        index,
        qid,
        answer,
        correct
    ):

        with self.connection() as c:

            c.execute(
                '''
                INSERT INTO exam_answers (
                    exam_id,
                    question_index,
                    question_id,
                    selected_answer,
                    correct_answer,
                    is_correct
                )
                VALUES (?, ?, ?, ?, ?, ?)

                ON CONFLICT(exam_id, question_index)
                DO UPDATE SET
                    selected_answer = excluded.selected_answer,
                    is_correct = excluded.is_correct
                ''',
                (
                    eid,
                    index,
                    qid,
                    answer,
                    correct,
                    int(answer == correct) if answer else 0
                )
            )


    # =========================================================
    # GET ANSWERS
    # =========================================================

    def answers(self, eid):

        with self.connection() as c:

            return [
                dict(r)
                for r in c.execute(
                    '''
                    SELECT *
                    FROM exam_answers
                    WHERE exam_id = ?
                    ''',
                    (eid,)
                )
            ]


    # =========================================================
    # WARNING COUNT
    # =========================================================

    def warning_count(self, eid):

        with self.connection() as c:

            return c.execute(
                '''
                SELECT warning_count
                FROM exams
                WHERE id = ?
                ''',
                (eid,)
            ).fetchone()[0]


    # =========================================================
    # ADD PROCTORING EVENT
    # =========================================================

    def add_event(
        self,
        eid,
        kind,
        message,
        warning=False
    ):

        with self.connection() as c:

            c.execute(
                '''
                INSERT INTO proctoring_events (
                    exam_id,
                    event_type,
                    message,
                    created_at
                )
                VALUES (?, ?, ?, ?)
                ''',
                (
                    eid,
                    kind,
                    message,
                    self.now()
                )
            )

            if warning:

                c.execute(
                    '''
                    UPDATE exams
                    SET warning_count = warning_count + 1
                    WHERE id = ?
                    ''',
                    (eid,)
                )


    # =========================================================
    # GET PROCTORING EVENTS
    # =========================================================

    def events(self, eid):

        with self.connection() as c:

            return [
                dict(r)
                for r in c.execute(
                    '''
                    SELECT *
                    FROM proctoring_events
                    WHERE exam_id = ?
                    ORDER BY id
                    ''',
                    (eid,)
                )
            ]


    # =========================================================
    # SUBMIT EXAM
    # =========================================================

    def submit(self, eid, fields, topics):

        with self.connection() as c:

            c.execute(
                '''
                UPDATE exams
                SET
                    status = ?,
                    ended_at = ?,
                    score = ?,
                    correct_count = ?,
                    incorrect_count = ?,
                    unanswered_count = ?,
                    knowledge_level = ?,
                    submission_reason = ?
                WHERE id = ?
                AND status NOT IN (
                    'SUBMITTED',
                    'AUTO_SUBMITTED'
                )
                ''',
                (
                    fields['status'],
                    self.now(),
                    fields['score'],
                    fields['correct'],
                    fields['incorrect'],
                    fields['unanswered'],
                    fields['level'],
                    fields['reason'],
                    eid
                )
            )

            c.execute(
                '''
                DELETE FROM topic_performance
                WHERE exam_id = ?
                ''',
                (eid,)
            )

            c.executemany(
                '''
                INSERT INTO topic_performance (
                    exam_id,
                    topic,
                    total,
                    correct,
                    percentage
                )
                VALUES (?, ?, ?, ?, ?)
                ''',
                [
                    (
                        eid,
                        t['topic'],
                        t['total'],
                        t['correct'],
                        t['percentage']
                    )
                    for t in topics
                ]
            )


    # =========================================================
    # TOPIC PERFORMANCE
    # =========================================================

    def topic_performance(self, eid):

        with self.connection() as c:

            return [
                dict(r)
                for r in c.execute(
                    '''
                    SELECT *
                    FROM topic_performance
                    WHERE exam_id = ?
                    ORDER BY percentage DESC
                    ''',
                    (eid,)
                )
            ]


    # =========================================================
    # ALL EXAMS FOR STUDENT
    # =========================================================

    def all_exams(self, uid):

        with self.connection() as c:

            return [
                dict(r)
                for r in c.execute(
                    '''
                    SELECT *
                    FROM exams
                    WHERE student_id = ?
                    ORDER BY id DESC
                    ''',
                    (uid,)
                )
            ]


    # =========================================================
    # DASHBOARD STATISTICS
    # =========================================================

    def dashboard_stats(self, uid):

        rows = self.all_exams(uid)

        complete = [
            r
            for r in rows
            if r['status'] in (
                'SUBMITTED',
                'AUTO_SUBMITTED'
            )
        ]

        scores = [
            r['score']
            for r in complete
            if r['score'] is not None
        ]

        latest = complete[0] if complete else {}

        return {
            'tests': len(complete),

            'average': (
                round(sum(scores) / len(scores))
                if scores
                else 0
            ),

            'best': (
                round(max(scores))
                if scores
                else 0
            ),

            'level': latest.get(
                'knowledge_level',
                'No assessments yet'
            ),

            'latest_domain': latest.get(
                'domain',
                '—'
            )
        }


    # =========================================================
    # RECENT EXAMS
    # =========================================================

    def recent_exams(self, uid):

        return self.all_exams(uid)[:5]


    # =========================================================
    # ANALYTICS
    # =========================================================

    def analytics(self, uid):

        rows = [
            r
            for r in self.all_exams(uid)
            if r['score'] is not None
        ]

        by = {}

        for r in rows:

            by.setdefault(
                r['domain'],
                []
            ).append(r['score'])


        domains = [
            {
                'domain': k,
                'score': round(
                    sum(v) / len(v)
                )
            }

            for k, v in by.items()
        ]


        domains.sort(
            key=lambda x: x['score'],
            reverse=True
        )


        return {
            'tests': len(rows),

            'average': (
                round(
                    sum(
                        r['score']
                        for r in rows
                    ) / len(rows)
                )
                if rows
                else 0
            ),

            'domains': domains,

            'best': (
                domains[0]['domain']
                if domains
                else '—'
            ),

            'weakest': (
                domains[-1]['domain']
                if domains
                else '—'
            )
        }


    # =========================================================
    # COMPLETE STUDENT PROFILE DATA
    # =========================================================

    def profile_data(self, uid):

        with self.connection() as c:

            # -------------------------------------------------
            # STUDENT INFORMATION
            # -------------------------------------------------

            student_row = c.execute(
                '''
                SELECT
                    id,
                    username,
                    created_at
                FROM students
                WHERE id = ?
                ''',
                (uid,)
            ).fetchone()


            if not student_row:

                return None


            student = dict(student_row)


            # -------------------------------------------------
            # COMPLETED ASSESSMENTS
            # -------------------------------------------------

            exams = [
                dict(row)

                for row in c.execute(
                    '''
                    SELECT
                        id,
                        domain,
                        difficulty,
                        status,
                        started_at,
                        ended_at,
                        duration_seconds,
                        score,
                        correct_count,
                        incorrect_count,
                        unanswered_count,
                        knowledge_level,
                        warning_count,
                        submission_reason,
                        created_at
                    FROM exams
                    WHERE student_id = ?

                    AND status IN (
                        'SUBMITTED',
                        'AUTO_SUBMITTED'
                    )

                    ORDER BY id DESC
                    ''',
                    (uid,)
                ).fetchall()
            ]


            # -------------------------------------------------
            # SCORES
            # -------------------------------------------------

            scores = [
                exam['score']

                for exam in exams

                if exam['score'] is not None
            ]


            # -------------------------------------------------
            # BASIC STATISTICS
            # -------------------------------------------------

            tests_taken = len(exams)


            average_score = (
                round(
                    sum(scores) /
                    len(scores)
                )
                if scores
                else 0
            )


            best_score = (
                round(max(scores))
                if scores
                else 0
            )


            # -------------------------------------------------
            # CURRENT KNOWLEDGE LEVEL
            # -------------------------------------------------

            current_level = (
                exams[0]['knowledge_level']

                if (
                    exams
                    and exams[0]['knowledge_level']
                )

                else 'No assessments yet'
            )


            # -------------------------------------------------
            # LATEST ASSESSMENT
            # -------------------------------------------------

            latest = (
                exams[0]
                if exams
                else None
            )


            # -------------------------------------------------
            # TOTAL QUESTION PERFORMANCE
            # -------------------------------------------------

            total_correct = sum(
                exam['correct_count'] or 0
                for exam in exams
            )


            total_incorrect = sum(
                exam['incorrect_count'] or 0
                for exam in exams
            )


            total_unanswered = sum(
                exam['unanswered_count'] or 0
                for exam in exams
            )


            # -------------------------------------------------
            # DOMAIN PERFORMANCE
            # -------------------------------------------------

            domain_data = {}


            for exam in exams:

                domain = exam['domain']


                if domain not in domain_data:

                    domain_data[domain] = []


                if exam['score'] is not None:

                    domain_data[domain].append(
                        exam['score']
                    )


            domain_performance = []


            for domain, domain_scores in domain_data.items():

                if not domain_scores:
                    continue


                domain_performance.append(
                    {
                        'domain': domain,

                        'average': round(
                            sum(domain_scores) /
                            len(domain_scores)
                        ),

                        'tests': len(domain_scores)
                    }
                )


            domain_performance.sort(
                key=lambda x: x['average'],
                reverse=True
            )


            # -------------------------------------------------
            # RETURN COMPLETE PROFILE
            # -------------------------------------------------

            return {

                'student': student,

                'tests_taken': tests_taken,

                'average_score': average_score,

                'best_score': best_score,

                'current_level': current_level,

                'total_correct': total_correct,

                'total_incorrect': total_incorrect,

                'total_unanswered': total_unanswered,

                'latest': latest,

                'domain_performance': domain_performance,

                'recent_exams': exams[:5]
            }

