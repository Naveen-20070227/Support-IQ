# Customer Review Sentiment Analysis — Full-Stack Project Specification

## 1. Project Overview

Build a full-stack **Customer Review Sentiment Analysis** web application for a company that provides an application/service.

Customers can log in and submit reviews about their experience. The backend automatically analyzes each review using a trained sentiment-analysis model and classifies it as:

* Positive
* Neutral
* Negative

A single Support Team account can log in to a dashboard where all customer reviews are automatically organized according to their predicted sentiment.

The Support Team does **not** manually classify reviews.

---

## 2. Main Objective

Automate the process of understanding customer feedback.

### Workflow

```text
Customer
   ↓
Customer Login
   ↓
Feedback Form
   ↓
Submit Review
   ↓
FastAPI Backend
   ↓
Loaded ML Model
   ↓
Sentiment Prediction
   ↓
SQLite Database
   ↓
Support Team Dashboard
   ↓
Automatic Organization
```

---

## 3. User Roles

There are only two roles.

### Customer

There can be multiple customer accounts.

Customer capabilities:

* Register
* Log in
* Submit feedback/review
* Receive confirmation after submission
* Optionally view their own submitted feedback

Customers must not have access to the Support Team dashboard.

### Support Team

There is one Support Team role/account.

Support capabilities:

* Log in through a separate Support Team login
* View customer feedback
* View predicted sentiment
* View automatically organized feedback:

  * Positive → Testimonials
  * Neutral → Neutral
  * Negative → Improvement
* View sentiment counts/statistics

The Support Team does **not** manually classify feedback.

---

## 4. Sentiment Classification

The ML model predicts exactly three classes:

```text
positive
neutral
negative
```

The application must use the trained ML model for prediction.

Do not create a separate rule-based sentiment classifier in JavaScript or FastAPI.

---

## 5. Current ML Performance

Current test results:

| Class                | Precision |   Recall |       F1 | Support |
| -------------------- | --------: | -------: | -------: | ------: |
| Negative             |      0.99 |     0.99 |     0.99 |     111 |
| Neutral              |      0.99 |     0.99 |     0.99 |     120 |
| Positive             |      0.98 |     0.98 |     0.98 |     129 |
| **Overall Accuracy** |  **0.99** | **0.99** | **0.99** | **360** |

These metrics describe the trained model. They should not be hard-coded into the application's prediction logic.

---

## 6. ML Model Integration

The FastAPI backend must load the trained ML model using **joblib**.

### Important

The model must be loaded **once when the FastAPI application starts**.

Do not load the model for every customer request.

Correct flow:

```text
FastAPI starts
      ↓
Load ML model with joblib
      ↓
Keep model in memory
      ↓
Customer submits feedback
      ↓
Use loaded model
      ↓
Return prediction
```

If multiple model artifacts are required, such as preprocessing objects, vectorizers, classifiers, or other saved components, load them during application startup as well.

The model path must be configurable.

---

## 7. Technology Stack

### Frontend

Use:

* HTML
* CSS
* JavaScript

Do **not** use:

* React
* Vue
* Angular
* Next.js

unless explicitly requested later.

### Backend

* Python
* FastAPI

### Database

* SQLite

### ML

* Existing trained sentiment model
* joblib for model loading

---

## 8. Frontend Pages

### 8.1 Landing Page

Provide:

* Short project/application introduction
* Customer Login
* Customer Registration
* Support Team Login

Clearly explain that customer feedback is automatically analyzed.

---

### 8.2 Customer Registration

Fields:

* Name
* Email
* Password
* Confirm Password

Requirements:

* Validate required fields
* Validate email format
* Validate password confirmation
* Prevent duplicate email registration
* Show useful validation messages
* Redirect to customer login after successful registration

---

### 8.3 Customer Login

Fields:

* Email
* Password

Requirements:

* Authenticate through FastAPI
* Show invalid-login errors
* Redirect authenticated customers to the feedback page

---

### 8.4 Customer Feedback Page

The authenticated customer can submit a review about the company's application/service.

Required field:

* Feedback / Review text

Requirements:

* Text area
* Character limit
* Client-side validation
* Server-side validation
* Submit button
* Loading state
* Success confirmation

The customer must **not** select the sentiment.

The sentiment is predicted automatically.

---

### 8.5 Support Team Login

A separate login page for the Support Team.

Do not use the customer login page for support authentication.

After successful authentication, redirect to the Support Dashboard.

---

### 8.6 Support Dashboard

The dashboard should contain:

### Summary

* Total feedback
* Positive count
* Neutral count
* Negative count

### Positive — Testimonials

Automatically display positive feedback here.

### Neutral

Automatically display neutral feedback here.

### Negative — Improvement

Automatically display negative feedback here.

The Support Team should never have to manually move feedback between these sections.

---

## 9. Feedback Display

Each feedback item should display:

* Customer name
* Feedback text
* Sentiment
* Submission date/time

Example:

```text
Customer: John

"The application is very easy to use and helpful."

Sentiment: Positive
Submitted: 27 Sep 2026
```

---

## 10. Database

Use SQLite.

### users table

```text
id
name
email
password_hash
role
created_at
```

Roles:

```text
customer
support
```

### feedback table

```text
id
customer_id
feedback_text
sentiment
created_at
```

Relationship:

```text
User
  1
  │
  │ submits
  ▼
Many Feedback Records
```

One customer can submit multiple reviews.

---

## 11. Authentication

Authentication must be implemented in FastAPI.

Requirements:

* Passwords must never be stored as plain text
* Store password hashes
* Separate customer and support roles
* Protect authenticated endpoints
* Protect support endpoints with role authorization
* Customers must not access support endpoints

Frontend-only protection is not sufficient.

Authorization must be enforced on the backend.

---

## 12. API Structure

Suggested endpoints:

### Authentication

```text
POST /auth/register
POST /auth/login
POST /auth/support-login
```

### Customer

```text
POST /feedback
GET /feedback/my
```

### Support

```text
GET /support/feedback
GET /support/feedback/positive
GET /support/feedback/neutral
GET /support/feedback/negative
GET /support/stats
```

The exact structure can be adjusted if a cleaner FastAPI architecture is appropriate.

---

## 13. Feedback Submission Flow

When a customer submits feedback:

```text
1. Customer submits feedback
2. JavaScript sends request to FastAPI
3. FastAPI validates the request
4. Sentiment service receives the text
5. Loaded ML model predicts sentiment
6. Prediction becomes:
      positive
      neutral
      negative
7. Feedback + customer ID + prediction + timestamp
   are stored in SQLite
8. FastAPI returns success
9. Frontend displays confirmation
```

Do not require the customer to manually choose a sentiment.

---

## 14. Automatic Organization

Organization must be completely automatic.

```text
positive
    ↓
Testimonials

neutral
    ↓
Neutral

negative
    ↓
Improvement
```

The dashboard reads the stored sentiment and places the feedback into the appropriate section.

---

## 15. Backend Architecture

Suggested structure:

```text
project/
│
├── app/
│   ├── main.py
│   │
│   ├── routes/
│   │   ├── auth.py
│   │   ├── feedback.py
│   │   └── support.py
│   │
│   ├── models/
│   │   ├── user.py
│   │   └── feedback.py
│   │
│   ├── schemas/
│   │   ├── auth.py
│   │   └── feedback.py
│   │
│   ├── services/
│   │   ├── auth_service.py
│   │   └── sentiment_service.py
│   │
│   ├── database.py
│   └── dependencies.py
│
├── ml/
│   └── model/
│
├── frontend/
│   ├── index.html
│   ├── register.html
│   ├── customer-login.html
│   ├── feedback.html
│   ├── support-login.html
│   ├── dashboard.html
│   │
│   ├── css/
│   │   └── style.css
│   │
│   └── js/
│       ├── auth.js
│       ├── feedback.js
│       └── dashboard.js
│
├── data/
│   └── app.db
│
├── requirements.txt
├── .env
└── README.md
```

Keep the architecture understandable. Do not over-engineer the project.

---

## 16. Sentiment Service

Create a dedicated ML service.

Conceptually:

```text
FastAPI feedback route
        ↓
sentiment_service.py
        ↓
loaded model
        ↓
predict_sentiment(text)
        ↓
positive / neutral / negative
```

The API route should not contain all the ML implementation details.

---

## 17. Frontend ↔ Backend

Use JavaScript `fetch()` for API communication.

```text
HTML Form
   ↓
JavaScript
   ↓
fetch()
   ↓
FastAPI
   ↓
JSON response
   ↓
Update UI
```

Show:

* Loading state
* Success state
* Validation errors
* Authentication errors
* Server errors

Avoid unnecessary page reloads.

---

## 18. Support Dashboard Features

The Support Dashboard should show:

### Statistics

```text
Total Feedback
Positive
Neutral
Negative
```

### Feedback sections

```text
Testimonials
─────────────
Positive feedback


Neutral
────────
Neutral feedback


Improvement
───────────
Negative feedback
```

The dashboard should automatically refresh or fetch updated data after new feedback is submitted.

Optional usability features:

* Filter by sentiment
* Sort newest/oldest
* Search customer/feedback text

---

## 19. Security

### Passwords

Use secure password hashing.

Never store plain-text passwords.

### Authentication

Use an appropriate FastAPI authentication mechanism.

### Authorization

Enforce:

```text
Customer → customer endpoints
Support → support endpoints
```

Customers must not access support data by manually changing URLs.

### Input validation

Validate feedback on both frontend and backend.

Reject:

* Empty feedback
* Invalid requests
* Excessively large input

### Database

Use safe database operations and avoid unsafe SQL string construction.

---

## 20. Error Handling

Use appropriate HTTP status codes.

```text
400 → Invalid input
401 → Not authenticated
403 → Insufficient permissions
404 → Resource not found
409 → Duplicate registration
500 → Internal server error
```

Frontend should display user-friendly messages.

Never expose Python stack traces to users.

---

## 21. Environment Variables

Use environment variables for configurable/sensitive values.

Example:

```text
SECRET_KEY=
DATABASE_URL=
MODEL_PATH=
```

The model path must be configurable.

Do not hard-code sensitive credentials.

---

## 22. Startup

When FastAPI starts:

```text
1. Initialize database
2. Load ML model
3. Validate model files
4. Start API server
```

If the model cannot be loaded, report the error clearly during startup.

Do not wait until the first customer submits feedback to discover that the model is missing.

---

## 23. Performance

The application must not retrain the ML model during normal operation.

Correct:

```text
Startup
  ↓
Load model
  ↓
Customer request
  ↓
Inference
  ↓
Database
```

Incorrect:

```text
Customer request
  ↓
Load model
  ↓
Train model
  ↓
Predict
```

The expensive model initialization should happen only once.

---

## 24. Persistence

SQLite must be the persistent storage.

Do not use a Python list as the primary database.

After restarting FastAPI:

* Users must remain
* Feedback must remain
* Sentiment predictions must remain

---

## 25. Support Account

Provide a safe method to create the initial Support Team account.

Do not put a real password directly in source code.

Use environment variables or a setup command/script.

---

## 26. README

The README must explain:

1. Project overview
2. Features
3. Technology stack
4. Project structure
5. Virtual environment setup
6. Dependency installation
7. Environment variables
8. Model placement
9. Database initialization
10. Support account creation
11. Starting FastAPI
12. Running/accessing frontend
13. ML prediction flow
14. API endpoints
15. Example usage

---

## 27. Dependencies

Keep dependencies minimal.

Expected dependencies may include:

```text
fastapi
uvicorn
sqlalchemy
pydantic
joblib
password hashing/authentication libraries
ML dependencies required by the saved model
```

Only install packages that are actually needed.

Do not introduce a frontend framework.

---

## 28. Development Phases

### Phase 1 — Backend

* FastAPI setup
* SQLite connection
* Database models
* Configuration

### Phase 2 — Authentication

* Customer registration
* Customer login
* Support login
* Password hashing
* Role-based authorization

### Phase 3 — ML

* Load model using joblib
* Build sentiment service
* Test prediction
* Integrate prediction with feedback API

### Phase 4 — Feedback API

* Submit feedback
* Predict sentiment
* Save feedback
* Retrieve customer feedback
* Retrieve support feedback
* Statistics endpoint

### Phase 5 — Customer Frontend

* Landing page
* Registration
* Login
* Feedback form
* Submission confirmation

### Phase 6 — Support Frontend

* Support login
* Dashboard
* Statistics
* Testimonials
* Neutral
* Improvement

### Phase 7 — Integration

* Connect frontend to FastAPI
* Authentication
* Authorization
* Loading states
* Error handling
* Responsive UI

### Phase 8 — Testing

Test:

* Registration
* Duplicate registration
* Valid login
* Invalid login
* Support login
* Unauthorized dashboard access
* Feedback submission
* Empty feedback
* ML prediction
* Database persistence
* Multiple customers
* Multiple feedback submissions
* Dashboard organization
* Server restart

---

## 29. Acceptance Criteria

### Customer

* [ ] Multiple customers can register
* [ ] Customer can log in
* [ ] Customer can access feedback form
* [ ] Customer can submit feedback
* [ ] Empty feedback is rejected
* [ ] Feedback is automatically classified
* [ ] Customer receives confirmation

### ML

* [ ] Model is loaded using joblib
* [ ] Model loads once at application startup
* [ ] No training occurs during customer requests
* [ ] Prediction is positive, neutral, or negative
* [ ] Prediction is stored with feedback

### Support

* [ ] Support has a separate login
* [ ] Dashboard is protected
* [ ] Support can view all customer feedback
* [ ] Positive feedback automatically appears under Testimonials
* [ ] Neutral feedback automatically appears under Neutral
* [ ] Negative feedback automatically appears under Improvement
* [ ] Sentiment counts update automatically

### Database

* [ ] Multiple customers supported
* [ ] Multiple reviews per customer supported
* [ ] Feedback persists after restart
* [ ] Customer-feedback relationship maintained

### Security

* [ ] Passwords hashed
* [ ] Authentication enforced by FastAPI
* [ ] Customer cannot access support endpoints
* [ ] Support data is protected

### Frontend

* [ ] HTML/CSS/JavaScript only
* [ ] Responsive design
* [ ] Clear loading states
* [ ] Clear errors
* [ ] Clear success messages
* [ ] Modern customer UI
* [ ] Modern support dashboard

---

## 30. Scope Restrictions

Do not add these unless explicitly requested:

* React
* Vue
* Angular
* Node.js backend
* PostgreSQL
* MongoDB
* Manual sentiment classification
* Multiple support roles
* Team-based issue routing
* Microservices
* LLM integration
* Retraining from the web application
* Unnecessary AI features

Keep the code understandable and explainable.

The target stack is:

**HTML + CSS + JavaScript + Python + FastAPI + SQLite + joblib + trained sentiment model**

---

## 31. Final Application Flow

```text
                         CUSTOMER
                            │
                            ▼
                     Customer Login
                            │
                            ▼
                      Feedback Form
                            │
                            ▼
                       Submit Review
                            │
                            ▼
                       FastAPI API
                            │
                            ▼
                    Loaded ML Model
                       (joblib)
                            │
                            ▼
                   Sentiment Prediction
                            │
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
           Positive       Neutral       Negative
              │             │             │
              ▼             ▼             ▼
        Testimonials      Neutral      Improvement
              │             │             │
              └─────────────┼─────────────┘
                            ▼
                       SQLite DB
                            │
                            ▼
                  SUPPORT TEAM LOGIN
                            │
                            ▼
                   SUPPORT DASHBOARD
                            │
                            ▼
              Automatically organized feedback
```

## 32. Final Goal

Build a complete, practical, resume-level full-stack ML application where:

**A customer submits a review → the FastAPI backend sends it through the trained sentiment model → the sentiment is automatically stored in SQLite → the Support Team sees the feedback automatically organized as Positive/Testimonials, Neutral, or Negative/Improvement.**

The application should be simple enough for the developer to understand and explain every major part of the implementation.
