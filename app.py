import logging
import os
from datetime import datetime, timezone
from functools import wraps

from flask import (
    Flask,
    Response,
    abort,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from database.db import Database
from proctoring.camera import camera_manager
from proctoring.proctor import verify_candidate
from services.exam_service import (
    ExamService,
    VALID_DIFFICULTIES,
    VALID_DOMAINS,
)


# =========================================================
# APPLICATION SETUP
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)


app = Flask(__name__)

app.config.update(
    SECRET_KEY=os.environ.get(
        "ASSESSIQ_SECRET",
        "local-development-key-change-me",
    )
)


# =========================================================
# DATABASE
# =========================================================

db = Database(
    os.path.join(
        BASE_DIR,
        "database",
        "assessiq.db",
    )
)

db.initialize()


# =========================================================
# EXAM SERVICE
# =========================================================

exams = ExamService(
    db,
    os.path.join(
        BASE_DIR,
        "datasets",
    ),
)


# =========================================================
# LOGIN PROTECTION
# =========================================================

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):

        if not session.get("user_id"):
            return redirect(
                url_for("login")
            )

        return view(*args, **kwargs)

    return wrapped


# =========================================================
# ACTIVE EXAM HELPER
# =========================================================

def active_exam_or_404(exam_id):

    exam = db.get_exam(
        exam_id,
        session["user_id"],
    )

    if not exam:
        abort(404)

    return exam


# =========================================================
# LANDING PAGE
# =========================================================

@app.route("/")
def landing():

    return render_template(
        "landing.html"
    )


# =========================================================
# LOGIN
# =========================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        if not username:

            flash(
                "Please enter a username.",
                "error"
            )

            return render_template(
                "login.html"
            )

        user = db.get_or_create_student(
            username
        )

        session.clear()

        session["user_id"] = user["id"]
        session["username"] = user["username"]

        return redirect(
            url_for("dashboard")
        )

    return render_template(
        "login.html"
    )


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("login")
    )


# =========================================================
# FORGOT PASSWORD
# =========================================================

@app.route("/forgot-password")
def forgot_password():

    return render_template(
        "forgot_password.html"
    )


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/dashboard")
@login_required
def dashboard():

    user_id = session["user_id"]

    return render_template(
        "dashboard.html",
        username=session["username"],
        stats=db.dashboard_stats(
            user_id
        ),
        recent=db.recent_exams(
            user_id
        ),
    )


# =========================================================
# DOMAINS
# =========================================================

@app.route("/domains")
@login_required
def domains():

    domain_list = [

        {
            "slug": "aiml",
            "name": "AI & Machine Learning",
            "icon": "brain",
            "description": (
                "Assess your knowledge of artificial "
                "intelligence, machine learning, and "
                "related concepts."
            ),
        },

        {
            "slug": "data_analytics",
            "name": "Data Analytics",
            "icon": "chart-column",
            "description": (
                "Test your skills in data analysis, "
                "statistics, visualization, and "
                "data-driven insights."
            ),
        },

        {
            "slug": "fullstack",
            "name": "Full Stack",
            "icon": "code",
            "description": (
                "Evaluate your knowledge of frontend, "
                "backend, databases, and full-stack "
                "development."
            ),
        },

        {
            "slug": "devops",
            "name": "DevOps",
            "icon": "server",
            "description": (
                "Assess your understanding of DevOps, "
                "CI/CD, cloud, containers, and "
                "deployment practices."
            ),
        },

        {
            "slug": "aptitude",
            "name": "Aptitude",
            "icon": "calculator",
            "description": (
                "Test your logical reasoning, "
                "quantitative aptitude, and "
                "problem-solving abilities."
            ),
        },

    ]

    return render_template(
        "domains.html",
        domains=domain_list,
    )


# =========================================================
# DIFFICULTY SELECTION
# =========================================================

@app.route("/difficulty/<domain>")
@login_required
def difficulty(domain):

    if domain not in VALID_DOMAINS:
        abort(404)

    return render_template(
        "difficulty.html",
        domain=domain,
        domain_name=VALID_DOMAINS[domain],
    )


# =========================================================
# CAMERA VIDEO FEED
# =========================================================

@app.route("/video_feed")
@login_required
def video_feed():

    if not camera_manager.start():

        return (
            "Camera unavailable",
            503
        )

    return Response(
        camera_manager.frames(),
        mimetype=(
            "multipart/x-mixed-replace; "
            "boundary=frame"
        ),
    )


# =========================================================
# AI VERIFICATION
# =========================================================

@app.route("/verify")
@login_required
def verify():

    frame = camera_manager.get_frame()

    if frame is None:

        return jsonify(
            {
                "camera": False,
                "face": False,
                "person": False,
                "person_count": 0,
                "phone": False,
                "book": False,
                "eye": False,
                "eye_state": "CAMERA_UNAVAILABLE",
            }
        )

    return jsonify(
        verify_candidate(frame)
    )


# =========================================================
# CREATE EXAM
# =========================================================

@app.route(
    "/api/exam/create",
    methods=["POST"]
)
@login_required
def create_exam():

    payload = (
        request.get_json(silent=True)
        or request.form
    )

    domain = payload.get("domain")
    difficulty = payload.get("difficulty")

    if (
        domain not in VALID_DOMAINS
        or difficulty not in VALID_DIFFICULTIES
    ):

        return jsonify(
            error="Invalid domain or difficulty."
        ), 400

    exam = exams.create_exam(
        session["user_id"],
        domain,
        difficulty,
    )

    session["pending_exam_id"] = exam["id"]

    return jsonify(
        exam_id=exam["id"]
    )


# =========================================================
# EXAM VERIFICATION
# =========================================================

@app.route(
    "/api/exam/<int:exam_id>/verify",
    methods=["POST"]
)
@login_required
def mark_verified(exam_id):

    exam = active_exam_or_404(
        exam_id
    )

    if exam["status"] != "CREATED":

        return jsonify(
            error=(
                "Exam is no longer "
                "awaiting verification."
            )
        ), 409

    # Get the latest shared camera frame once.
    frame = camera_manager.get_frame()

    if frame is not None:

        result = verify_candidate(
            frame
        )

    else:

        result = {
            "camera": False,
            "face": False,
            "person": False,
            "person_count": 0,
            "phone": False,
            "book": False,
            "eye": False,
            "eye_state": "CAMERA_UNAVAILABLE",
        }

    passed = (
        all(
            result.get(key)
            for key in (
                "camera",
                "face",
                "person",
                "eye",
            )
        )
        and not result.get("phone")
        and not result.get("book")
    )

    if not passed:

        return jsonify(
            error=(
                "All security checks "
                "must pass before beginning."
            )
        ), 403

    db.set_exam_verified(
        exam_id
    )

    return jsonify(
        ok=True,
        exam_url=url_for(
            "exam_page",
            exam_id=exam_id,
        ),
    )


# =========================================================
# EXAM PAGE
# =========================================================

@app.route("/exam/<int:exam_id>")
@login_required
def exam_page(exam_id):

    exam = active_exam_or_404(
        exam_id
    )

    if exam["status"] == "CREATED":

        return redirect(
            url_for(
                "difficulty",
                domain=exam["domain"],
            )
        )

    if exam["status"] in (
        "SUBMITTED",
        "AUTO_SUBMITTED",
    ):

        return redirect(
            url_for(
                "results",
                exam_id=exam_id,
            )
        )

    exams.ensure_started(
        exam_id
    )

    return render_template(
        "exam.html",
        exam=exams.exam_view(
            exam_id
        ),
        domain_name=VALID_DOMAINS[
            exam["domain"]
        ],
    )


# =========================================================
# SAVE EXAM ANSWER
# =========================================================

@app.route(
    "/api/exam/<int:exam_id>/answer",
    methods=["POST"]
)
@login_required
def save_answer(exam_id):

    active_exam_or_404(
        exam_id
    )

    payload = request.get_json(
        force=True
    )

    try:

        next_index = exams.save_answer(
            exam_id,
            int(
                payload["question_index"]
            ),
            payload.get("answer"),
        )

    except (
        KeyError,
        ValueError,
        IndexError,
    ):

        return jsonify(
            error="Invalid answer payload."
        ), 400

    return jsonify(
        ok=True,
        next_index=next_index,
    )


# =========================================================
# LIVE PROCTORING
# =========================================================

@app.route(
    "/api/exam/<int:exam_id>/proctor"
)
@login_required
def proctor_exam(exam_id):

    exam = active_exam_or_404(
        exam_id
    )

    if exam["status"] not in (
        "IN_PROGRESS",
        "VERIFIED",
    ):

        return jsonify(
            error="Exam is not active."
        ), 409

    frame = camera_manager.get_frame()

    if frame is not None:

        result = verify_candidate(
            frame
        )

    else:

        result = {
            "camera": False,
            "face": False,
            "person": False,
            "person_count": 0,
            "phone": False,
            "book": False,
            "eye": False,
            "eye_state": "CAMERA_UNAVAILABLE",
        }

    return jsonify(
        exams.record_proctor_result(
            exam_id,
            result,
        )
    )


# =========================================================
# SUBMIT EXAM
# =========================================================

@app.route(
    "/api/exam/<int:exam_id>/submit",
    methods=["POST"]
)
@login_required
def submit_exam(exam_id):

    active_exam_or_404(
        exam_id
    )

    reason = (
        request.get_json(
            silent=True
        )
        or {}
    ).get(
        "reason",
        "MANUAL",
    )

    report = exams.submit(
        exam_id,
        reason,
    )

    return jsonify(
        ok=True,
        results_url=url_for(
            "results",
            exam_id=exam_id,
        ),
        report=report,
    )


# =========================================================
# RESULTS
# =========================================================

@app.route(
    "/results/<int:exam_id>"
)
@login_required
def results(exam_id):

    exam = active_exam_or_404(
        exam_id
    )

    if exam["status"] not in (
        "SUBMITTED",
        "AUTO_SUBMITTED",
    ):

        return redirect(
            url_for(
                "exam_page",
                exam_id=exam_id,
            )
        )

    return render_template(
        "results.html",
        report=exams.report(
            exam_id
        ),
        domain_name=VALID_DOMAINS[
            exam["domain"]
        ],
    )


# =========================================================
# ANSWER REVIEW
# =========================================================

@app.route(
    "/answer-review/<int:exam_id>"
)
@login_required
def answer_review(exam_id):

    exam = active_exam_or_404(
        exam_id
    )

    if exam["status"] not in (
        "SUBMITTED",
        "AUTO_SUBMITTED",
    ):

        return redirect(
            url_for(
                "exam_page",
                exam_id=exam_id,
            )
        )

    report = exams.report(
        exam_id
    )

    return render_template(
        "answer_review.html",
        report=report,
        domain_name=VALID_DOMAINS[
            exam["domain"]
        ],
    )


# =========================================================
# HISTORY / REPORTS
# =========================================================

@app.route("/history")
@login_required
def history():

    return render_template(
        "history.html",
        exams=db.all_exams(
            session["user_id"]
        ),
    )


# =========================================================
# AI ANALYTICS
# =========================================================

@app.route("/analytics")
@login_required
def analytics():

    return render_template(
        "analytics.html",
        analytics=db.analytics(
            session["user_id"]
        ),
    )


# =========================================================
# PROFILE
# =========================================================

@app.route("/profile")
@login_required
def profile():

    user_id = session["user_id"]

    # Retrieve the complete profile information
    # directly from the SQLite database.
    profile = db.profile_data(
        user_id
    )

    return render_template(
        "profile.html",
        username=session["username"],
        profile=profile,
    )


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True,
        threaded=True,
    )