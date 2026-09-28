import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report
import joblib

def train():
    csv_path = os.path.join("data", "sentiment-analysis.csv")
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Dataset not found at {csv_path}")

    print(f"Loading dataset from {csv_path}...")
    df = pd.read_csv(csv_path)

    X = df['feedback'].astype(str)
    y = df['sentiment'].astype(str)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print("Training TF-IDF + Logistic Regression pipeline...")
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True)),
        ('clf', LogisticRegression(max_iter=1000, random_state=42))
    ])

    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    report = classification_report(y_test, y_pred)
    print("\nClassification Report on Test Set:")
    print(report)

    output_dir = os.path.join("ml", "model")
    os.makedirs(output_dir, exist_ok=True)
    model_path = os.path.join(output_dir, "sentiment_pipeline.joblib")

    joblib.dump(pipeline, model_path)
    print(f"\nModel successfully saved to {model_path}")

if __name__ == "__main__":
    train()
