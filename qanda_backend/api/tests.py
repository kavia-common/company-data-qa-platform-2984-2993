from rest_framework.test import APITestCase
from django.urls import reverse

class HealthTests(APITestCase):
    def test_health(self):
        url = reverse('Health')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"message": "Server is up!"})

class QATests(APITestCase):
    def test_embedding_endpoint(self):
        url = reverse('embeddings')
        response = self.client.post(url, {"texts": ["hello world", "how are you"]}, format="json")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIn("vectors", body)
        self.assertEqual(len(body["vectors"]), 2)

    def test_qa_endpoint(self):
        # question before seeding should still respond (no references)
        url = reverse('qa')
        response = self.client.post(url, {"question": "What is our mission?"}, format="json")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIn("answer", body)
