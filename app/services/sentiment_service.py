import os
import joblib
import torch
from dotenv import load_dotenv
from transformers import AutoTokenizer, AutoModel

load_dotenv()

class SentimentService:
    _instance = None
    _classifier = None
    _tokenizer = None
    _bert_model = None
    _device = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SentimentService, cls).__new__(cls)
        return cls._instance

    def load_model(self, classifier_path: str = None):
        """
        Loads the BERT tokenizer, BERT model, and trained Logistic Regression classifier.
        Called ONCE during FastAPI application startup lifespan.
        """
        if classifier_path is None:
            classifier_path = os.getenv("MODEL_PATH", "models/sentiment_classifier.joblib")
            if not os.path.exists(classifier_path):
                # Fallback to ml/model path if models directory is not used
                classifier_path = os.path.join("ml", "model", "sentiment_classifier.joblib")

        if not os.path.exists(classifier_path):
            raise FileNotFoundError(
                f"Logistic Regression classifier artifact not found at '{classifier_path}'. "
                f"Please run 'python train_model.py' to generate the model artifact."
            )

        print(f"[ML Startup] Loading Logistic Regression classifier from '{classifier_path}'...")
        self._classifier = joblib.load(classifier_path)

        print("[ML Startup] Loading bert-base-uncased tokenizer & PyTorch model...")
        self._tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
        self._bert_model = AutoModel.from_pretrained("bert-base-uncased")
        
        self._device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self._bert_model.to(self._device)
        self._bert_model.eval()

        print("[ML Startup] BERT [CLS] Sentiment Service initialized successfully.")

    @property
    def _model(self):
        return self._classifier

    def predict(self, text: str) -> str:
        """
        Predicts sentiment for a given input text using BERT [CLS] embedding + Logistic Regression.
        """
        if self._classifier is None or self._tokenizer is None or self._bert_model is None:
            raise RuntimeError("Sentiment model is not loaded. Ensure load_model() was called on startup.")

        cleaned_text = text.strip() if text else ""
        if not cleaned_text:
            return "neutral"

        try:
            encoded = self._tokenizer(
                [cleaned_text],
                padding=True,
                truncation=True,
                max_length=128,
                return_tensors="pt"
            ).to(self._device)

            with torch.no_grad():
                outputs = self._bert_model(**encoded)
                # Extract 768-dimensional [CLS] embedding (index 0 of sequence dimension)
                cls_embedding = outputs.last_hidden_state[:, 0, :].cpu().numpy()

            prediction = self._classifier.predict(cls_embedding)[0]
            pred_str = str(prediction.item()) if hasattr(prediction, "item") else str(prediction)
            return pred_str.lower().strip()
        except Exception as e:
            print(f"[Prediction Error] Failed to generate sentiment: {e}")
            return "neutral"

sentiment_service = SentimentService()
