from django import forms

from .models import Category, Transaction


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = [
            "transaction_type",
            "category",
            "amount",
            "description",
            "transaction_date",
        ]
        widgets = {
            "transaction_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = Category.objects.none()
        if user is not None:
            self.fields["category"].queryset = Category.objects.filter(user=user, is_active=True)
            self.fields["transaction_type"].initial = Transaction.TransactionType.EXPENSE


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "category_type", "color", "is_active"]
        widgets = {"color": forms.TextInput(attrs={"type": "color"})}
