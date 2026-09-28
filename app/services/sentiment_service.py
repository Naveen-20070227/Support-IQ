import os
import joblib
from dotenv import load_dotenv

load_dotenv()

class SentimentService:
    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SentimentService, cls).__new__(cls)
        return cls._instance

    def load_model(self, model_path: str = None):
        if model_path is None:
            model_path = os.getenv("MODEL_PATH", "ml/model/sentiment_pipeline.joblib")

        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"ML model file not found at '{model_path}'. "
                f"Please run 'python train_model.py' to generate the model artifact."
            )

        print(f"[ML Startup] Loading sentiment analysis model from '{model_path}'...")
        self._model = joblib.load(model_path)
        print("[ML Startup] Model loaded into memory successfully.")

    def predict(self, text: str) -> str:
        if self._model is None:
            raise RuntimeError("Sentiment model is not loaded. Ensure load_model() was called on startup.")
        
        cleaned_text = text.strip()
        if not cleaned_text:
            return "neutral"

        prediction = self._model.predict([cleaned_text])[0]
        return str(prediction).lower()

sentiment_service = SentimentService()
