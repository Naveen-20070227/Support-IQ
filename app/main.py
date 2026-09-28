import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv

from app.database import engine, Base, SessionLocal
from app.models.user import User
from app.services.auth_service import hash_password
from app.services.sentiment_service import sentiment_service
from app.routes import auth, feedback, support

load_dotenv()

def init_support_account():
    db = SessionLocal()
    try:
        support_user = db.query(User).filter(User.role == "support").first()
        if not support_user:
            support_email = os.getenv("SUPPORT_EMAIL", "support@company.com").lower().strip()
            support_password = os.getenv("SUPPORT_PASSWORD", "SupportPassword123!")
            
            # Check if user with this email already exists
            existing_email = db.query(User).filter(User.email == support_email).first()
            if not existing_email:
                hashed = hash_password(support_password)
                new_support = User(
                    name="Support Admin",
                    email=support_email,
                    password_hash=hashed,
                    role="support"
                )
                db.add(new_support)
                db.commit()
                print(f"[Database Seed] Default Support Team account created: {support_email}")
            else:
                existing_email.role = "support"
                db.commit()
                print(f"[Database Seed] Updated existing account to support role: {support_email}")
        else:
            print(f"[Database Seed] Support account ready ({support_user.email}).")
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Initialize DB tables
    print("[Startup] Initializing SQLite database tables...")
    Base.metadata.create_all(bind=engine)

    # 2. Seed initial Support Team account if needed
    init_support_account()

    # 3. Load ML model into memory ONCE
    model_path = os.getenv("MODEL_PATH", "ml/model/sentiment_pipeline.joblib")
    sentiment_service.load_model(model_path)

    yield

    print("[Shutdown] Cleaning up application resources...")

app = FastAPI(
    title="Customer Review Sentiment Analysis API",
    description="Full-Stack Sentiment Analysis System with Automated ML Classification",
    version="1.0.0",
    lifespan=lifespan
)

# Include API routers
app.include_router(auth.router)
app.include_router(feedback.router)
app.include_router(support.router)

# Mount static files directory for frontend
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

@app.get("/")
@app.get("/index.html")
def read_root():
    index_path = os.path.join(frontend_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Customer Review Sentiment Analysis API is running."}

@app.get("/register.html")
def read_register():
    return FileResponse(os.path.join(frontend_dir, "register.html"))

@app.get("/customer-login.html")
def read_customer_login():
    return FileResponse(os.path.join(frontend_dir, "customer-login.html"))

@app.get("/feedback.html")
def read_feedback():
    return FileResponse(os.path.join(frontend_dir, "feedback.html"))

@app.get("/support-login.html")
def read_support_login():
    return FileResponse(os.path.join(frontend_dir, "support-login.html"))

@app.get("/dashboard.html")
def read_dashboard():
    return FileResponse(os.path.join(frontend_dir, "dashboard.html"))


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "model_loaded": sentiment_service._model is not None,
        "database": "connected"
    }
