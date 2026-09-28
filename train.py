import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from transformers import AutoTokenizer , AutoModel
import torch

df = pd.read_csv("data/sentiment-analysis.csv")

X = df['feedback']
y = df['sentiment']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
model = AutoModel.from_pretrained("bert-base-uncased")


model.eval()

with torch.no_grad():
    tokens = tokenizer(
        X_train.tolist(),
        padding=True,
        truncation=True,
        return_tensors="pt"
    )

    op = model(**tokens)

    X_train_embeddings = op.last_hidden_state[:, 0, :]

with torch.no_grad():
    test_tokens = tokenizer(
        X_test.tolist(),
        padding=True,
        truncation=True,
        return_tensors="pt"
    )

    test_op = model(**test_tokens)

    X_test_embeddings = test_op.last_hidden_state[:, 0, :]

classifier = LogisticRegression(max_iter=1000)

classifier.fit(X_train_embeddings.numpy(), y_train)

y_pred = classifier.predict(X_test_embeddings.numpy())

print(classification_report(y_test, y_pred))