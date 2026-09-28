import os
import unittest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, SessionLocal
from app.models.user import User
from app.models.feedback import Feedback

class TestSentimentAnalysisApp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client_cm = TestClient(app)
        cls.client = cls.client_cm.__enter__()
        db = SessionLocal()
        try:
            db.query(Feedback).delete()
            db.query(User).filter(User.role != "support").delete()
            db.commit()
        finally:
            db.close()

    @classmethod
    def tearDownClass(cls):
        cls.client_cm.__exit__(None, None, None)



    def test_01_health_check(self):
        res = self.client.get("/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "healthy")
        self.assertTrue(data["model_loaded"])

    def test_02_support_account_seeded(self):
        res = self.client.post("/auth/support-login", json={
            "email": "support@company.com",
            "password": "SupportPassword123!"
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["role"], "support")
        self.assertIn("access_token", data)
        TestSentimentAnalysisApp.support_token = data["access_token"]

    def test_03_customer_registration_and_duplicate(self):
        # Register Customer 1
        res = self.client.post("/auth/register", json={
            "name": "Alice Green",
            "email": "alice@test.com",
            "password": "password123",
            "confirm_password": "password123"
        })
        self.assertEqual(res.status_code, 201)
        data = res.json()
        self.assertEqual(data["email"], "alice@test.com")
        self.assertEqual(data["role"], "customer")

        # Duplicate email registration test
        res_dup = self.client.post("/auth/register", json={
            "name": "Alice Duplicate",
            "email": "alice@test.com",
            "password": "password123",
            "confirm_password": "password123"
        })
        self.assertEqual(res_dup.status_code, 409)

        # Mismatched password test
        res_mismatch = self.client.post("/auth/register", json={
            "name": "Bob Mismatch",
            "email": "bob@test.com",
            "password": "password123",
            "confirm_password": "differentpassword"
        })
        self.assertEqual(res_mismatch.status_code, 400)

    def test_04_customer_login(self):
        # Valid login
        res = self.client.post("/auth/login", json={
            "email": "alice@test.com",
            "password": "password123"
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["role"], "customer")
        TestSentimentAnalysisApp.customer_token = data["access_token"]

        # Invalid password
        res_invalid = self.client.post("/auth/login", json={
            "email": "alice@test.com",
            "password": "wrongpassword"
        })
        self.assertEqual(res_invalid.status_code, 401)

    def test_05_customer_feedback_submission_and_ml_prediction(self):
        headers = {"Authorization": f"Bearer {TestSentimentAnalysisApp.customer_token}"}

        # 1. Positive feedback submission
        pos_text = "I am extremely satisfied with the product! The user interface is super clean, fast, and very helpful."
        res1 = self.client.post("/feedback", json={"feedback_text": pos_text}, headers=headers)
        self.assertEqual(res1.status_code, 201)
        data1 = res1.json()
        self.assertEqual(data1["sentiment"], "positive")

        # 2. Neutral feedback submission
        neu_text = "The installation process continues to be adequate and standard as expected."
        res2 = self.client.post("/feedback", json={"feedback_text": neu_text}, headers=headers)
        self.assertEqual(res2.status_code, 201)
        data2 = res2.json()
        self.assertEqual(data2["sentiment"], "neutral")

        # 3. Negative feedback submission
        neg_text = "My experience is awful. The application keeps crashing, constantly slow, and frustrating."
        res3 = self.client.post("/feedback", json={"feedback_text": neg_text}, headers=headers)
        self.assertEqual(res3.status_code, 201)
        data3 = res3.json()
        self.assertEqual(data3["sentiment"], "negative")

    def test_06_customer_my_feedback(self):
        headers = {"Authorization": f"Bearer {TestSentimentAnalysisApp.customer_token}"}
        res = self.client.get("/feedback/my", headers=headers)
        self.assertEqual(res.status_code, 200)
        items = res.json()
        self.assertGreaterEqual(len(items), 3)

    def test_07_security_role_authorization_enforcement(self):
        customer_headers = {"Authorization": f"Bearer {TestSentimentAnalysisApp.customer_token}"}
        
        # Customer trying to access support endpoints -> expect 403 Forbidden
        res_stats = self.client.get("/support/stats", headers=customer_headers)
        self.assertEqual(res_stats.status_code, 403)

        res_list = self.client.get("/support/feedback", headers=customer_headers)
        self.assertEqual(res_list.status_code, 403)

    def test_08_support_dashboard_endpoints(self):
        support_headers = {"Authorization": f"Bearer {TestSentimentAnalysisApp.support_token}"}

        # Stats
        res_stats = self.client.get("/support/stats", headers=support_headers)
        self.assertEqual(res_stats.status_code, 200)
        stats = res_stats.json()
        self.assertGreaterEqual(stats["total"], 3)
        self.assertGreaterEqual(stats["positive"], 1)
        self.assertGreaterEqual(stats["neutral"], 1)
        self.assertGreaterEqual(stats["negative"], 1)

        # Categorized endpoint checks
        res_pos = self.client.get("/support/feedback/positive", headers=support_headers)
        self.assertEqual(res_pos.status_code, 200)
        for item in res_pos.json():
            self.assertEqual(item["sentiment"], "positive")

        res_neu = self.client.get("/support/feedback/neutral", headers=support_headers)
        self.assertEqual(res_neu.status_code, 200)
        for item in res_neu.json():
            self.assertEqual(item["sentiment"], "neutral")

        res_neg = self.client.get("/support/feedback/negative", headers=support_headers)
        self.assertEqual(res_neg.status_code, 200)
        for item in res_neg.json():
            self.assertEqual(item["sentiment"], "negative")

    def test_09_empty_feedback_rejection(self):
        headers = {"Authorization": f"Bearer {TestSentimentAnalysisApp.customer_token}"}
        res = self.client.post("/feedback", json={"feedback_text": "   "}, headers=headers)
        self.assertEqual(res.status_code, 400)

if __name__ == "__main__":
    unittest.main()
