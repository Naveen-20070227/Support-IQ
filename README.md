# SupportIQ

**AI-powered customer feedback and sentiment analysis platform.**

SupportIQ lets customers submit free-text reviews and automatically classifies each one as **Positive**, **Neutral**, or **Negative** using a BERT-embedding + Logistic Regression model. The support team gets a protected dashboard where feedback is organized on its own into *Testimonials*, *Neutral*, and *Improvement* columns, with live statistics, search, and sorting. No one has to label anything by hand.

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688?logo=fastapi&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.4%2B-F7931E?logo=scikit-learn&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-2.0%2B-EE4C2C?logo=pytorch&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?logo=sqlite&logoColor=white)

---

## Table of Contents

- [Features](#features)
- [How It Works](#how-it-works)
- [Tech Stack](#tech-stack)
- [Model Performance](#model-performance)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Reference](#api-reference)
- [Testing](#testing)
- [Security Notes](#security-notes)
- [Limitations and Roadmap](#limitations-and-roadmap)
- [Author](#author)

---

## Features

- **Automated sentiment classification.** Every review is classified server-side by a trained ML model. There is no manual tagging and no rule-based fallback.
- **Load once, serve fast.** The BERT encoder and classifier are loaded a single time at application startup through FastAPI's lifespan hook and reused for every request.
- **Role-based access control.** Two roles, `customer` and `support`, enforced on the backend with JWT bearer tokens (24-hour expiry) and bcrypt password hashing. Customers cannot reach support endpoints.
- **Support dashboard.** Feedback is grouped by predicted sentiment, with KPI counts, keyword search across review text, customer name, and email, and newest/oldest sorting.
- **Customer portal.** Customers register, sign in, submit reviews (up to 2,000 characters), and see their own submission history along with the predicted sentiment.
- **Zero-setup persistence.** SQLite via SQLAlchemy, with tables and the support account created automatically on first launch.
- **Lightweight frontend.** Responsive vanilla HTML/CSS/JavaScript with a dark, glassmorphic design, served directly by FastAPI. No build step required.
- **Health endpoint.** `GET /health` reports API status and whether the model is loaded.

## How It Works

```text
Customer submits review  ──►  POST /feedback  (customer JWT required)
                                   │
                                   ▼
                    Validate input (non-empty, ≤ 2000 chars)
                                   │
                                   ▼
        bert-base-uncased  ──►  768-d [CLS] embedding  (max 128 tokens)
                                   │
                                   ▼
             Logistic Regression  ──►  positive | neutral | negative
                                   │
                                   ▼
        Persist to SQLite (text, sentiment, customer_id, timestamp)
                                   │
                                   ▼
     Support dashboard reads the DB and groups results automatically
```

**Model design.** Text is encoded with the pretrained `bert-base-uncased` transformer, and the `[CLS]` token embedding (768 dimensions) is fed to a scikit-learn `LogisticRegression` classifier. Only the lightweight classifier is trained and serialized (`joblib`), while the BERT weights are downloaded from Hugging Face on first run.

## Tech Stack

| Layer | Technology |
| --- | --- |
| **Frontend** | HTML5, CSS3 (custom properties, glassmorphism), JavaScript (ES6+, Fetch API) |
| **Backend** | Python 3.10+, FastAPI, Uvicorn, Pydantic v2 |
| **Auth** | PyJWT (HS256), bcrypt |
| **Database** | SQLite (WAL mode) with SQLAlchemy 2.0 ORM |
| **Machine Learning** | Hugging Face Transformers, PyTorch, scikit-learn, pandas, joblib |
| **Testing** | `unittest` with FastAPI `TestClient` |

## Model Performance

Evaluated on a stratified 80/20 train/test split (`random_state=42`) of the 1,799-review dataset in `data/sentiment-analysis.csv` (360 held-out reviews):

| Class | Precision | Recall | F1 | Support |
| --- | ---: | ---: | ---: | ---: |
| Negative | 0.99 | 0.99 | 0.99 | 111 |
| Neutral | 0.99 | 0.99 | 0.99 | 120 |
| Positive | 0.98 | 0.98 | 0.98 | 129 |
| **Overall accuracy** | | | **0.99** | **360** |

Re-run `python train.py` to reproduce these metrics on your machine. Exact figures may shift slightly with library versions and hardware.

## Project Structure

```text
Support-IQ/
├── app/
│   ├── main.py                    # App factory, lifespan (DB init, seeding, model load), static mounting
│   ├── database.py                # SQLAlchemy engine, session factory, SQLite WAL pragmas
│   ├── dependencies.py            # JWT auth and role-guard dependencies
│   ├── models/
│   │   ├── user.py                # User model (customer / support)
│   │   └── feedback.py            # Feedback model
│   ├── schemas/
│   │   ├── auth.py                # Auth request/response schemas
│   │   └── feedback.py            # Feedback and stats schemas
│   ├── services/
│   │   ├── auth_service.py        # Password hashing and JWT creation/decoding
│   │   └── sentiment_service.py   # Singleton BERT + classifier inference service
│   └── routes/
│       ├── auth.py                # Register, customer login, support login, profile
│       ├── feedback.py            # Submit feedback, customer history
│       └── support.py             # Dashboard stats and categorized feedback
├── frontend/
│   ├── index.html                 # Landing page
│   ├── register.html              # Customer registration
│   ├── customer-login.html        # Customer sign-in
│   ├── feedback.html              # Review submission
│   ├── support-login.html         # Support team sign-in
│   ├── dashboard.html             # Support dashboard
│   ├── css/style.css              # Design system and responsive styles
│   └── js/                        # auth.js, feedback.js, dashboard.js
├── data/
│   └── sentiment-analysis.csv     # Training dataset (id, feedback, sentiment)
├── ml/model/                      # Serialized classifier (sentiment_classifier.joblib)
├── models/                        # Mirror copy of the classifier artifact
├── train_model.py                 # Embedding extraction, training, evaluation, export
├── train.py                       # Convenience entry point for training
├── test_app.py                    # Integration test suite
├── requirements.txt
└── README.md
```

## Getting Started

### Prerequisites

- Python **3.10** or newer
- `pip`
- Internet access on first launch (downloads `bert-base-uncased`, roughly 440 MB, and caches it locally)
- Optional: a CUDA-capable GPU. Inference automatically uses it when available and falls back to CPU otherwise.

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/Support-IQ.git
cd Support-IQ
```

### 2. Create and activate a virtual environment

```bash
# Linux / macOS
python3 -m venv venv
source venv/bin/activate

# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root (see [Configuration](#configuration)).

### 5. Train the model (optional)

A pre-trained classifier is included in `ml/model/` and `models/`. To retrain from the dataset:

```bash
python train.py
```

This extracts BERT embeddings, fits the classifier, prints accuracy, precision, recall, and F1 with a per-class report, and saves the artifact to both `ml/model/` and `models/`.

### 6. Run the application

```bash
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

On startup the app creates the database tables, seeds the support account (if none exists), and loads the model into memory. Once you see the `BERT [CLS] Sentiment Service initialized` message, open **http://127.0.0.1:8000**.

## Configuration

Create a `.env` file in the project root:

```env
SECRET_KEY=replace-with-a-long-random-string
DATABASE_URL=sqlite:///./data/app.db
MODEL_PATH=models/sentiment_classifier.joblib
SUPPORT_EMAIL=support@company.com
SUPPORT_PASSWORD=choose-a-strong-password
```

| Variable | Description | Default |
| --- | --- | --- |
| `SECRET_KEY` | Key used to sign JWTs. **Must be set to a unique random value** in any real deployment. | Insecure built-in fallback |
| `DATABASE_URL` | SQLAlchemy connection string | `sqlite:///./data/app.db` |
| `MODEL_PATH` | Path to the classifier artifact. Falls back to `ml/model/sentiment_classifier.joblib`. | `models/sentiment_classifier.joblib` |
| `SUPPORT_EMAIL` | Email of the support account seeded on first startup | `support@company.com` |
| `SUPPORT_PASSWORD` | Password of the seeded support account | Insecure built-in fallback |

Generate a strong secret with:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## Usage

| Page | URL |
| --- | --- |
| Landing page | `http://127.0.0.1:8000/` |
| Customer registration | `http://127.0.0.1:8000/register.html` |
| Customer login | `http://127.0.0.1:8000/customer-login.html` |
| Submit feedback | `http://127.0.0.1:8000/feedback.html` |
| Support login | `http://127.0.0.1:8000/support-login.html` |
| Support dashboard | `http://127.0.0.1:8000/dashboard.html` |
| Interactive API docs (Swagger) | `http://127.0.0.1:8000/docs` |

**Quick walkthrough**

1. Register a customer account and sign in.
2. Submit a review, for example: *"The dark mode is fantastic and support responded within minutes!"*
3. The confirmation shows the predicted sentiment (**positive**).
4. Sign out, then log in through the **Support login** page with the credentials from your `.env`.
5. The dashboard shows updated statistics, and the review appears under **Testimonials**.

## API Reference

All protected endpoints expect an `Authorization: Bearer <token>` header.

### Authentication

| Method | Endpoint | Access | Description |
| --- | --- | --- | --- |
| `POST` | `/auth/register` | Public | Register a customer and receive a token |
| `POST` | `/auth/login` | Public | Customer login |
| `POST` | `/auth/support-login` | Public | Support team login |
| `GET` | `/auth/me` | Authenticated | Current user profile |

### Customer feedback

| Method | Endpoint | Access | Description |
| --- | --- | --- | --- |
| `POST` | `/feedback` | Customer | Submit a review; runs ML prediction and stores the result |
| `GET` | `/feedback/my` | Customer | The caller's submission history |

### Support dashboard

| Method | Endpoint | Access | Description |
| --- | --- | --- | --- |
| `GET` | `/support/stats` | Support | Counts: total, positive, neutral, negative |
| `GET` | `/support/feedback` | Support | All feedback; supports `sentiment`, `search`, and `sort` (`asc` / `desc`) query params |
| `GET` | `/support/feedback/positive` | Support | Testimonials |
| `GET` | `/support/feedback/neutral` | Support | Neutral feedback |
| `GET` | `/support/feedback/negative` | Support | Improvement feedback |

### System

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/health` | Service status and model-loaded flag |

**Example request**

```bash
curl -X POST http://127.0.0.1:8000/feedback \
  -H "Authorization: Bearer <customer_token>" \
  -H "Content-Type: application/json" \
  -d '{"feedback_text": "Checkout was quick and the order tracking is excellent."}'
```

```json
{
  "id": 1,
  "customer_id": 2,
  "customer_name": "Alice Green",
  "customer_email": "alice@test.com",
  "feedback_text": "Checkout was quick and the order tracking is excellent.",
  "sentiment": "positive",
  "created_at": "2026-01-01T12:00:00"
}
```

## Testing

The integration suite covers health checks, support-account seeding, registration (including duplicate handling), authentication, role-based access control, and the feedback pipeline. It runs against a separate database (`data/test_app.db`), so your real data is untouched.

```bash
python -m unittest test_app -v
```

## Security Notes

- **Never commit `.env`.** Keep it out of version control and provide a `.env.example` with placeholder values instead.
- Always set a unique `SECRET_KEY` and change the seeded support password before deploying anywhere reachable.
- Passwords are hashed with bcrypt, and role checks are enforced server-side on every protected route.
- For production, restrict CORS and serve over HTTPS behind a reverse proxy. Consider adding rate limiting to the auth endpoints.

## Limitations and Roadmap

**Current limitations**

- The training dataset is small (1,799 samples), so accuracy on diverse, real-world review language may be lower than the reported test score.
- English-only, since the encoder is `bert-base-uncased`.
- Reviews are truncated to 128 tokens for inference.
- Single support account, and SQLite is best suited to development and small deployments.

**Ideas for future work**

- Train on larger, real-world review data and add confidence scores to predictions
- Fine-tune the transformer end-to-end rather than using frozen embeddings
- Dashboard analytics: sentiment trends over time and topic extraction
- Multiple support agents with an admin role
- Docker setup and PostgreSQL support
- CI pipeline running the test suite

## Author

**Naveen Prasanth K**

- GitHub: [github.com/Naveen-20070227](https://github.com/Naveen-20070227)
- LinkedIn: [linkedin.com/in/naveen-prasanth-k](https://linkedin.com/in/naveen-prasanth-k)
