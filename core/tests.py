from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Category, Transaction


class FinanceFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="demo-pass-123")
        self.income_cat = Category.objects.create(
            user=self.user,
            name="Salary",
            category_type=Category.CategoryType.INCOME,
        )

    def test_dashboard_requires_authentication(self):
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 302)

    def test_add_transaction(self):
        self.client.login(username="alice", password="demo-pass-123")
        response = self.client.post(
            reverse("add_transaction"),
            {
                "transaction_type": Transaction.TransactionType.INCOME,
                "category": self.income_cat.id,
                "amount": "100.00",
                "description": "Monthly salary",
                "transaction_date": "2026-04-13",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Transaction.objects.filter(user=self.user).count(), 1)
