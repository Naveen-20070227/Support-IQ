# Customer Review Sentiment Analysis — Full-Stack Web Application

A production-grade, full-stack **Customer Review Sentiment Analysis** web application. Customers submit reviews of their experience, which are instantly analyzed by an in-memory Scikit-Learn Machine Learning model (trained on customer review data with 99%+ overall accuracy) via a FastAPI backend. Results are automatically classified into **Positive**, **Neutral**, and **Negative** categories and populated onto an interactive Support Team Dashboard.

---

## 1. Project Overview

This project automates the workflow of interpreting customer feedback. 

- **Customers** register, log in, and submit reviews without picking a sentiment label.
- **FastAPI Backend** passes review text through the loaded ML model (`joblib`), predicts sentiment, and persists records in **SQLite**.
- **Support Team** logs into a protected dashboard where feedback is automatically organized into **Testimonials** (Positive), **Neutral**, and **Improvement** (Negative) columns with real-time statistics and filtering.

---

## 2. Key Features

- **Automated ML Sentiment Inference**: Model loaded once into memory at app startup via `joblib`; no per-request re-training or disk reads.
- **Role-Based Security**: Strict backend API authorization separating Customer and Support Team access with JWT Bearer tokens and bcrypt password hashing.
- **Automated Dashboard Categorization**: Support dashboard automatically groups reviews by predicted sentiment.
- **Modern Glassmorphic UI**: Responsive Vanilla HTML/CSS/JS frontend featuring dark mode aesthetics, loading spinners, character counter, search, sorting, and toast notifications.
- **Persistent Storage**: Full SQLite persistence via SQLAlchemy ORM.

---

## 3. Technology Stack

- **Frontend**: HTML5, CSS3 (Vanilla CSS with CSS Variables & Glassmorphism), JavaScript (ES6+ Fetch API).
- **Backend**: Python 3.10+, FastAPI, Uvicorn, SQLAlchemy, Pydantic v2, PyJWT, Passlib (bcrypt).
- **Database**: SQLite (`data/app.db`).
- **Machine Learning**: Scikit-Learn (TF-IDF Vectorizer + Logistic Regression pipeline), joblib.

---

## 4. Project Structure

```text
sentiment analysis/
│
├── app/
│   ├── main.py                # FastAPI initialization, lifespan lifecycle & static mounting
│   ├── database.py            # SQLite engine & SessionLocal setup
│   ├── dependencies.py        # JWT auth & role-authorization dependencies
│   ├── models/
│   │   ├── user.py            # User SQLAlchemy model (customer / support)
│   │   └── feedback.py        # Feedback SQLAlchemy model
│   ├── schemas/
│   │   ├── auth.py            # Pydantic auth schemas
│   │   └── feedback.py        # Pydantic feedback & stats schemas
│   ├── services/
│   │   ├── auth_service.py    # Bcrypt password hashing & JWT token management
│   │   └── sentiment_service.py # Singleton ML model loader & inference service
│   └── routes/
│       ├── auth.py            # Registration, Customer Login, Support Login endpoints
│       ├── feedback.py        # Feedback submission & customer history endpoints
│       └── support.py         # Support dashboard stats & categorized feedback APIs
│
├── ml/
│   └── model/
│       └── sentiment_pipeline.joblib # Serialized ML pipeline artifact
│
├── frontend/
│   ├── index.html             # Landing page
│   ├── register.html          # Customer registration
│   ├── customer-login.html    # Customer login
│   ├── feedback.html          # Customer feedback submission page
│   ├── support-login.html     # Dedicated Support Team login
│   ├── dashboard.html        # Support Team Dashboard
│   ├── css/
│   │   └── style.css          # Design system & responsive styles
│   └── js/
│       ├── auth.js            # Token management & auth utilities
│       ├── feedback.js        # Customer feedback form logic
│       └── dashboard.js       # Support dashboard rendering logic
│
├── data/
│   ├── sentiment-analysis.csv # Training dataset
│   └── app.db                 # SQLite database (auto-created)
│
├── train_model.py             # Model training & joblib serialization script
├── requirements.txt           # Python dependencies
├── .env                       # Environment configuration
└── README.md                  # Project documentation
```

---

## 5. Virtual Environment Setup

### Windows (PowerShell / CMD)
```powershell
python -m venv venv
.\venv\Scripts\activate
```

### Linux / macOS
```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 6. Dependency Installation

Install all required Python packages using pip:

```bash
pip install -r requirements.txt
```

---

## 7. Environment Variables

Create or edit `.env` in the root directory:

```env
SECRET_KEY=9a8d7f6e5c4b3a210fedcba987654321abcdef0123456789
DATABASE_URL=sqlite:///./data/app.db
MODEL_PATH=ml/model/sentiment_pipeline.joblib
SUPPORT_EMAIL=support@company.com
SUPPORT_PASSWORD=SupportPassword123!
```

---

## 8. ML Model Placement & Training

To train the sentiment model on `data/sentiment-analysis.csv` and export the `.joblib` model artifact:

```bash
python train_model.py
```

Output will display the test classification metrics (~99% accuracy across Positive, Neutral, Negative) and save the model to `ml/model/sentiment_pipeline.joblib`.

---

## 9. Database Initialization & Support Account Creation

Database tables (`users` and `feedback`) and the initial **Support Team** account are automatically initialized when FastAPI starts up via the lifespan event handler in `app/main.py`.

Default Support Team Credentials (configured in `.env`):
- **Email**: `support@company.com`
- **Password**: `SupportPassword123!`

---

## 10. Starting the Application

Run the FastAPI application with Uvicorn server:

```bash
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The server will initialize the database, seed the default support account, load the ML model into memory, and start serving requests at `http://127.0.0.1:8000`.

---

## 11. Accessing Frontend Pages

Open your browser and navigate to:

- **Landing Page**: `http://127.0.0.1:8000/` or `http://127.0.0.1:8000/static/index.html`
- **Customer Registration**: `http://127.0.0.1:8000/static/register.html`
- **Customer Login**: `http://127.0.0.1:8000/static/customer-login.html`
- **Customer Feedback Submission**: `http://127.0.0.1:8000/static/feedback.html`
- **Support Team Login**: `http://127.0.0.1:8000/static/support-login.html`
- **Support Dashboard**: `http://127.0.0.1:8000/static/dashboard.html`

---

## 12. ML Prediction Flow

```text
Customer Submits Review → JavaScript sends POST /feedback
       ↓
FastAPI validates request & customer JWT token
       ↓
SentimentService passes review text to pre-loaded joblib pipeline
       ↓
Model predicts label ('positive', 'neutral', or 'negative')
       ↓
Feedback record saved in SQLite app.db (text + sentiment + customer_id + timestamp)
       ↓
Support Dashboard reads database & renders into Testimonials / Neutral / Improvement
```

---

## 13. API Endpoints

### Authentication
- `POST /auth/register` — Register a customer account
- `POST /auth/login` — Customer authentication (returns JWT token)
- `POST /auth/support-login` — Support Team authentication (returns JWT token)
- `GET /auth/me` — Fetch profile of current user

### Customer Feedback
- `POST /feedback` — Submit a review (triggers ML prediction & storage)
- `GET /feedback/my` — Fetch submission history for authenticated customer

### Support Team
- `GET /support/stats` — Summary breakdown counts (Total, Positive, Neutral, Negative)
- `GET /support/feedback` — All customer feedback (supports `search`, `sentiment`, and `sort`)
- `GET /support/feedback/positive` — Categorized Testimonials (Positive)
- `GET /support/feedback/neutral` — Categorized Neutral feedback
- `GET /support/feedback/negative` — Categorized Improvement feedback (Negative)

---

## 14. Example Usage Walkthrough

1. Navigate to `http://127.0.0.1:8000/static/register.html` and create a customer account.
2. Log in at `customer-login.html` and submit a review (e.g. *"The dark mode option is amazing and customer support was very helpful!"*).
3. The system confirms the review and displays its predicted sentiment (**positive**).
4. Log out and navigate to `support-login.html`. Log in with `support@company.com` / `SupportPassword123!`.
5. The **Support Dashboard** shows updated KPI stats and automatically displays the review under **Testimonials**.
