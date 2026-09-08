# AssessIQ AI

### Adaptive AI-Powered Online Examination & Proctoring Platform

AssessIQ AI is an intelligent online examination platform that combines **adaptive assessment, artificial intelligence, computer vision, semantic question recommendation, and performance analytics** into a unified examination experience.

The platform is designed to make online assessments more **personalized, secure, data-driven, and explainable**. Students can select an assessment domain and difficulty level, complete a timed examination under AI-assisted proctoring, and receive detailed performance insights after submission.

---

## ✨ Key Features

* 🎯 **Adaptive Assessments** — Adjusts question difficulty based on student performance
* 🧠 **Semantic Question Recommendation** — Identifies conceptually similar questions using sentence embeddings
* 🔐 **AI-Assisted Proctoring** — Monitors examination integrity using computer vision
* 👁️ **Eye & Attention Monitoring** — Detects potential instances of looking away from the examination
* 👤 **Face & Person Detection** — Detects candidate presence and multiple-person scenarios
* 📱 **Phone Detection** — Detects mobile phones during examinations
* 📚 **Multi-Domain Assessments** — Supports multiple technical and aptitude domains
* ⏱️ **Timed Examinations** — Domain- and difficulty-based examination durations
* ⚠️ **Automated Warning System** — Records and manages proctoring violations
* 📊 **Topic-Level Analytics** — Identifies strengths and areas requiring improvement
* 🏆 **Knowledge-Level Classification** — Categorizes overall performance
* 📝 **Detailed Answer Review** — Provides question-by-question examination analysis
* 📈 **Performance History** — Allows students to review previous assessments
* 🎨 **Modern Examination Interface** — Clean, focused, responsive UI

---

# 🧠 What Makes AssessIQ AI Different?

Traditional online examination systems generally follow a fixed model:

> Select test → Answer fixed questions → Receive score

AssessIQ AI extends this workflow by combining **assessment + personalization + integrity monitoring + analytics**.

```text
                    ┌───────────────────────┐
                    │       Student         │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │       Dashboard       │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │ Domain + Difficulty   │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │ Pre-Exam Verification │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │    AI Proctoring      │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │ Adaptive Examination  │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │ Performance Analysis │
                    └───────────┬───────────┘
                                │
                    ┌───────────┴───────────┐
                    ▼                       ▼
             ┌─────────────┐        ┌─────────────┐
             │   Results   │        │   Analytics  │
             └─────────────┘        └─────────────┘
```

---

# 🚀 Core Features

## 1. 🔐 Student Authentication

Students enter the platform through an authentication workflow before accessing their examination dashboard.

The application maintains the student's examination state and associates assessments with the corresponding student account.

---

## 2. 📊 Assessment Dashboard

The dashboard acts as the central starting point for the examination experience.

Students can:

* Explore available assessment domains
* Start a new assessment
* View examination activity
* Access performance analytics
* Review previous assessments
* Access their profile

The interface is designed to keep the examination workflow simple and focused.

---

## 3. 📚 Multiple Assessment Domains

AssessIQ AI currently supports:

| Domain                    | Description                                         |
| ------------------------- | --------------------------------------------------- |
| **AI & Machine Learning** | Machine learning, AI, and related concepts          |
| **Data Analytics**        | Data analysis and analytical concepts               |
| **Full Stack**            | Full-stack development concepts                     |
| **DevOps**                | DevOps, CI/CD, infrastructure, and related concepts |
| **Aptitude**              | Quantitative and logical aptitude                   |

The question banks are stored as structured datasets and loaded by the examination service.

---

# 🎯 4. Difficulty Selection

Students can select one of four assessment modes:

### Easy

Designed around lower-difficulty questions.

### Medium

Designed around intermediate-level questions.

### Hard

Designed around higher-difficulty questions.

### Adaptive

Designed to provide a more personalized examination experience based on question difficulty and student performance.

---

# 🧠 5. Adaptive Assessment Engine

The adaptive component maintains a student's examination state, including:

* Current difficulty
* Score
* Answered questions
* Student identifier
* Selected domain

The system can increase or decrease the target difficulty based on whether the student answers correctly or incorrectly.

```text
                 Correct Answer
                       │
                       ▼
             Increase Difficulty
                       │
                       ▼
                  Next Question


                 Wrong Answer
                       │
                       ▼
             Decrease Difficulty
                       │
                       ▼
                  Next Question
```

The system also attempts to avoid previously answered questions while selecting subsequent questions.

---

# 🧠 6. Semantic Question Recommendation

AssessIQ AI includes a semantic recommendation subsystem based on **Sentence Transformers**.

Instead of relying only on exact keyword matching, semantic representations allow questions with similar meaning or concepts to be compared.

The project uses the **all-MiniLM-L6-v2** sentence-transformer model for generating question embeddings.

The recommendation process considers:

* Question meaning
* Domain
* Topic
* Difficulty

This enables the platform to identify related questions even when they use different wording.

---

# 🔐 7. AI-Assisted Examination Proctoring

Examination integrity is supported through computer-vision-based monitoring.

The proctoring subsystem includes components for detecting:

* Candidate face
* Number of people
* Eye / attention direction
* Mobile phones
* Books and other detected objects
* Camera availability

The system records detected violations as examination events.

---

# 👁️ 8. Eye & Attention Monitoring

The proctoring system monitors the candidate's visual attention during the examination.

Potential attention violations can generate a warning such as:

> Please focus on the examination screen.

The system uses a cooldown mechanism to prevent the same violation from being repeatedly recorded within a very short period.

---

# 👤 9. Person Detection

The platform checks whether the expected candidate is present.

Potential situations include:

```text
0 people  → Candidate missing
1 person  → Expected state
2+ people → Potential violation
```

Multiple-person detection can therefore contribute to the examination warning system.

---

# 📱 10. Prohibited Object Detection

The computer-vision subsystem can detect prohibited objects such as mobile phones.

The platform can also identify detected books and record corresponding proctoring events.

---

# ⚠️ 11. Automated Warning System

Proctoring violations are recorded as examination events.

Current violation categories include:

* `CAMERA_DISCONNECTED`
* `FACE_MISSING`
* `MULTIPLE_PERSON`
* `PHONE`
* `BOOK`
* `LOOKING_AWAY`

Warnings are rate-limited to avoid repeatedly recording the same event within a short period.

When the configured warning threshold is reached, the system can automatically submit the examination.

### Current threshold

**3 recorded warnings**

```text
Violation
    │
    ▼
Record Event
    │
    ▼
Increase Warning Count
    │
    ▼
Warning Count ≥ 3?
    │
   YES
    │
    ▼
Auto Submit Examination
```

---

# ⏱️ 12. Timed Examinations

Each difficulty mode has an associated examination duration.

| Difficulty |   Duration |
| ---------- | ---------: |
| Easy       | 20 minutes |
| Medium     | 25 minutes |
| Hard       | 30 minutes |
| Adaptive   | 25 minutes |

The examination page calculates the remaining time based on the stored examination start time.

---

# 📝 13. Examination Workflow

The complete student workflow is:

```text
Login
  ↓
Dashboard
  ↓
Select Domain
  ↓
Select Difficulty
  ↓
Pre-Exam Verification
  ↓
Start Verification
  ↓
Begin Examination
  ↓
Answer Questions
  ↓
AI-Assisted Proctoring
  ↓
Submit Examination
  ↓
Calculate Score
  ↓
Determine Knowledge Level
  ↓
Analyze Topics
  ↓
View Results
  ↓
Review Answers
  ↓
View History & Analytics
```

---

# 📊 14. Performance Analysis

After an assessment is submitted, AssessIQ AI calculates multiple performance indicators.

These include:

* Overall score
* Correct answers
* Incorrect answers
* Unanswered questions
* Knowledge level
* Topic-wise accuracy
* Strengths
* Weaknesses
* Strongest topic
* Weakest topic
* Performance insights

This allows students to understand **why** they received their score rather than seeing only a single percentage.

---

# 🏆 15. Knowledge-Level Classification

The current performance classification is:

|         Score | Knowledge Level |
| ------------: | --------------- |
|   **85–100%** | Advanced        |
|  **70–84.9%** | Strong          |
|  **50–69.9%** | Intermediate    |
| **Below 50%** | Beginner        |

The knowledge level is calculated from the student's final examination score.

---

# 📚 16. Topic-Level Performance

AssessIQ AI analyzes performance at the topic level.

For each topic, the system can calculate:

* Number of questions
* Number of correct answers
* Accuracy percentage

Topics can then be classified into:

### Strengths

Topics with accuracy of **70% or above**.

### Areas for Improvement

Topics with accuracy **below 70%**.

The system also identifies:

* Strongest topic
* Weakest topic

This makes the results more actionable for students.

---

# 🔎 17. Detailed Answer Review

After completing an assessment, students can inspect individual questions.

The answer review includes:

* Question number
* Question text
* Topic
* Available options
* Selected answer
* Correct answer
* Correct / incorrect status

This provides transparency into the final assessment result.

---

# 📈 18. History & Analytics

The platform provides dedicated views for reviewing examination activity and performance.

Students can use these sections to understand:

* Previous assessment results
* Score progression
* Topic performance
* Strengths
* Weaknesses
* Overall assessment activity

---

# 🏗️ System Architecture

```text
                         ┌────────────────────────┐
                         │      Student Browser   │
                         │   HTML / CSS / JS       │
                         └────────────┬───────────┘
                                      │
                                      ▼
                         ┌────────────────────────┐
                         │       Flask App        │
                         │        app.py           │
                         └────────────┬───────────┘
                                      │
             ┌────────────────────────┼────────────────────────┐
             │                        │                        │
             ▼                        ▼                        ▼
     ┌───────────────┐        ┌───────────────┐        ┌───────────────┐
     │ Exam Service  │        │    Database   │        │   Proctoring  │
     │               │        │    SQLite     │        │ Computer Vision│
     └───────┬───────┘        └───────────────┘        └───────┬───────┘
             │                                                  │
             ▼                                                  ▼
     ┌───────────────┐                                 ┌────────────────┐
     │ Question Bank │                                 │ OpenCV         │
     │ CSV Datasets  │                                 │ MediaPipe      │
     └───────┬───────┘                                 │ YOLO           │
             │                                         └────────────────┘
             ▼
     ┌─────────────────────┐
     │ Recommendation      │
     │ & Adaptive Engine   │
     └─────────────────────┘
```

---

# 🛠️ Technology Stack

## Backend

* **Python**
* **Flask**
* **SQLite**
* **Jinja2**

## Machine Learning & Data Processing

* **Pandas**
* **NumPy**
* **Scikit-learn**
* **Sentence Transformers**
* **PyTorch**
* **Transformers**

## Computer Vision

* **OpenCV**
* **MediaPipe**
* **Ultralytics YOLO**

## Frontend

* **HTML5**
* **CSS3**
* **JavaScript**
* **Jinja Templates**

## Development & Deployment

* **Git**
* **GitHub**
* **Gunicorn**
* **Render**

---

# 📁 Project Structure

```text
AssessIQ-Adaptive-Examination-Proctoring-Platform/
│
├── app.py
├── requirements.txt
├── .gitignore
├── yolov8n.pt
│
├── database/
│   └── db.py
│
├── datasets/
│   ├── aiml_questions_balanced_final.csv
│   ├── aptitude_questions_balanced_final.csv
│   ├── data_analyst_questions_balanced_final.csv
│   ├── devops_questions_balanced_final.csv
│   ├── fullstack_questions_balanced_final.csv
│   ├── master_questions.csv
│   └── ...
│
├── models/
│   ├── questions.pkl
│   ├── questions_semantic.pkl
│   └── tfidf_vectorizer.pkl
│
├── proctoring/
│   ├── camera.py
│   ├── eye_tracking.py
│   ├── face_detection.py
│   ├── object_detection.py
│   ├── person_detection.py
│   ├── phone_detection.py
│   ├── proctor.py
│   └── yolo_model.py
│
├── recommendation/
│   ├── adaptive_engine.py
│   ├── check_dataset.py
│   ├── clean_dataset.py
│   ├── eda.py
│   ├── normalize_difficulty.py
│   ├── preprocess.py
│   ├── recommender.py
│   ├── semantic_recommender.py
│   ├── train_model.py
│   └── train_semantic.py
│
├── services/
│   └── exam_service.py
│
├── static/
│   ├── css/
│   ├── images/
│   └── js/
│
├── templates/
│   ├── analytics.html
│   ├── answer_review.html
│   ├── base.html
│   ├── dashboard.html
│   ├── difficulty.html
│   ├── domains.html
│   ├── exam.html
│   ├── history.html
│   ├── landing.html
│   ├── login.html
│   ├── pre_exam.html
│   ├── profile.html
│   ├── results.html
│   └── ...
│
└── test_*.py
```

---

# 🚀 Installation & Setup

## Prerequisites

Make sure the following are installed:

* Python 3.12+
* Git
* A working webcam for local proctoring
* A modern web browser

---

## 1. Clone the Repository

```bash
git clone https://github.com/Brittaaaa/AssessIQ-Adaptive-Examination-Proctoring-Platform.git
```

Move into the project directory:

```bash
cd AssessIQ-Adaptive-Examination-Proctoring-Platform
```

---

## 2. Create a Virtual Environment

### Windows

```powershell
python -m venv venv
```

Activate it:

```powershell
venv\Scripts\activate
```

---

## 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

---

## 4. Run the Application

```powershell
python app.py
```

The application will be available at:

```text
http://127.0.0.1:5000
```

---

# 🧪 Testing

The project includes individual test scripts for the computer-vision components.

```text
test_face_detection.py
test_person_detection.py
test_phone_detection.py
test_proctor.py
test_yolo.py
```

For example:

```powershell
python test_face_detection.py
```

---

# 🧠 Machine Learning Pipeline

The recommendation subsystem contains a data-processing and model-building workflow.

```text
Raw Question Datasets
        │
        ▼
Data Cleaning
        │
        ▼
Question Normalization
        │
        ▼
Difficulty Normalization
        │
        ▼
Question Preprocessing
        │
        ├───────────────┐
        │               │
        ▼               ▼
   TF-IDF Model    Sentence Transformer
        │               │
        ▼               ▼
 Similarity         Embeddings
        │               │
        ▼               ▼
 Recommendation   Semantic Recommendation
```

---

# 📦 Data

The project contains multiple question datasets covering the supported assessment domains.

The datasets are processed into structured question banks containing information such as:

* Question
* Options A–D
* Correct answer
* Domain
* Topic
* Difficulty level
* Question ID

The examination service validates the required question fields before adding questions to the examination pool.

---

# 🔒 Security & Integrity Considerations

AssessIQ AI is designed with examination integrity in mind.

The system:

* Associates examinations with student accounts
* Tracks examination state
* Records proctoring events
* Maintains warning counts
* Supports automatic submission after repeated violations
* Stores examination answers and results
* Separates examination logic from presentation logic

For a production deployment, additional security hardening should be implemented, including:

* Secure production secrets
* HTTPS
* Strong authentication
* Session hardening
* Input validation
* Rate limiting
* Production database configuration
* Secure model and artifact storage
* Privacy controls for camera data

---

# ⚠️ Current Deployment Considerations

The current proctoring implementation was developed primarily for local execution, where the Flask server and student's camera are on the same machine.

For a true remote examination deployment, browser-based webcam access should be integrated with the server-side proctoring pipeline.

Similarly, very large generated ML artifacts should not be committed directly to a standard Git repository. They should be managed through appropriate model or artifact storage while keeping the source code repository lightweight.

---

# 🔮 Future Enhancements

AssessIQ AI can be extended with:

### 🤖 Advanced Adaptive Testing

* Item Response Theory (IRT)
* More sophisticated student ability estimation
* Dynamic question selection
* Historical performance-based calibration

### 👁️ Advanced Proctoring

* Browser-native webcam streaming
* Real-time remote proctoring
* Head-pose estimation
* Improved gaze analysis
* Audio anomaly detection
* More robust prohibited-object detection

### 📊 Advanced Analytics

* Longitudinal performance tracking
* Personalized learning recommendations
* Topic mastery prediction
* Difficulty-vs-performance analysis
* Instructor analytics dashboard

### 👨‍🏫 Instructor / Administrator Features

* Question-bank management
* Assessment creation
* Student monitoring
* Examination reports
* Question difficulty management
* Candidate performance comparison

### ☁️ Production Infrastructure

* Cloud database
* Cloud model storage
* Scalable backend
* Background processing
* Monitoring and logging
* Role-based access control

---

# 🎯 Design Principles

AssessIQ AI is built around five core principles.

### 1. Accuracy

Assessment results should be calculated consistently from structured examination data.

### 2. Adaptability

Assessment difficulty should be capable of responding to student performance.

### 3. Integrity

AI-assisted monitoring should help identify potential examination violations.

### 4. Explainability

Students should receive meaningful information about their performance rather than only a final score.

### 5. Usability

The examination interface should remain clear, focused, and easy to navigate.

---

# 📌 Project Status

**Status: Active Development**

Current implementation includes:

* ✅ Flask web application
* ✅ Student authentication workflow
* ✅ Assessment dashboard
* ✅ Multiple assessment domains
* ✅ Difficulty selection
* ✅ Adaptive assessment components
* ✅ Question-bank integration
* ✅ AI-assisted proctoring components
* ✅ Face detection
* ✅ Person detection
* ✅ Phone detection
* ✅ Eye / attention monitoring
* ✅ Automated warning system
* ✅ Timed examinations
* ✅ SQLite persistence
* ✅ Results generation
* ✅ Topic-level analysis
* ✅ Answer review
* ✅ Examination history
* ✅ Analytics
* ✅ Semantic recommendation components
* ✅ GitHub repository

---

# 👩‍💻 Author

## Britta Biju

**B.Tech — Artificial Intelligence & Machine Learning**

AssessIQ AI was developed as an AI/ML-focused engineering project combining:

**Artificial Intelligence + Machine Learning + Computer Vision + NLP + Data Analytics + Full-Stack Development**

---

# 🌐 Repository

**GitHub**

https://github.com/Brittaaaa/AssessIQ-Adaptive-Examination-Proctoring-Platform

---

# 📄 License

This project is currently intended primarily for **educational, academic, and demonstration purposes**.

A formal open-source license can be added when the project's distribution and reuse requirements are finalized.

---

## ⭐ AssessIQ AI

**Smarter Assessments. Adaptive Learning. Trusted Examination.**
