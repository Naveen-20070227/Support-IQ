import os
import pandas as pd
import numpy as np
import torch
import joblib
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, classification_report
from transformers import AutoTokenizer, AutoModel

def extract_cls_embeddings(texts, tokenizer, model, batch_size=32, max_length=128):
    """
    Extracts [CLS] token embeddings from bert-base-uncased for a list of texts.
    Uses model.eval() and torch.no_grad() for efficient inference.
    """
    model.eval()
    all_embeddings = []
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i + batch_size]
        encoded = tokenizer(
            batch_texts,
            padding=True,
            truncation=True,
            max_length=max_length,
            return_tensors="pt"
        ).to(device)
        
        with torch.no_grad():
            outputs = model(**encoded)
            # Extract [CLS] token embedding (index 0 of sequence dimension)
            cls_embeddings = outputs.last_hidden_state[:, 0, :].cpu().numpy()
            all_embeddings.append(cls_embeddings)
            
    return np.vstack(all_embeddings)

def train():
    csv_path = os.path.join("data", "sentiment-analysis.csv")
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Dataset not found at {csv_path}")

    print(f"[Training] Loading dataset from '{csv_path}'...")
    df = pd.read_csv(csv_path)

    # Support 'feedback' or 'feedback_text' column naming
    text_col = 'feedback' if 'feedback' in df.columns else 'feedback_text'
    X = df[text_col].astype(str).tolist()
    y = df['sentiment'].astype(str).str.lower().str.strip()

    print(f"[Training] Total dataset samples: {len(X)}")

    # Stratified train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print(f"[Training] Train set size: {len(X_train)}, Test set size: {len(X_test)}")
    print("[Training] Loading bert-base-uncased tokenizer and model...")
    
    tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
    bert_model = AutoModel.from_pretrained("bert-base-uncased")

    print("[Training] Extracting [CLS] embeddings for training set...")
    X_train_cls = extract_cls_embeddings(X_train, tokenizer, bert_model)

    print("[Training] Extracting [CLS] embeddings for test set...")
    X_test_cls = extract_cls_embeddings(X_test, tokenizer, bert_model)

    print("[Training] Fitting Logistic Regression classifier on [CLS] embeddings...")
    classifier = LogisticRegression(max_iter=1000, random_state=42)
    classifier.fit(X_train_cls, y_train)

    print("[Training] Evaluating model on untouched test set...")
    y_pred = classifier.predict(X_test_cls)

    acc = accuracy_score(y_test, y_pred)
    precision, recall, f1, _ = precision_recall_fscore_support(y_test, y_pred, average='weighted')
    report = classification_report(y_test, y_pred)

    print("\n" + "=" * 60)
    print("                 MODEL EVALUATION METRICS                 ")
    print("=" * 60)
    print(f"Accuracy : {acc:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall   : {recall:.4f}")
    print(f"F1-Score : {f1:.4f}")
    print("\nPer-Class Classification Report:\n")
    print(report)
    print("=" * 60 + "\n")

    # Save classifier to ml/model/sentiment_classifier.joblib and models/sentiment_classifier.joblib
    paths_to_save = [
        os.path.join("ml", "model", "sentiment_classifier.joblib"),
        os.path.join("models", "sentiment_classifier.joblib")
    ]

    for p in paths_to_save:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        joblib.dump(classifier, p)
        print(f"[Training] Saved Logistic Regression classifier artifact to '{p}'")

if __name__ == "__main__":
    train()
