import json
from datetime import timedelta
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Case, DecimalField, F, Sum, Value, When
from django.db.models.functions import TruncDay, TruncMonth, TruncWeek
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import CategoryForm, TransactionForm
from .models import Category, Transaction


PERIOD_TO_DAYS = {
    "daily": 1,
    "weekly": 7,
    "monthly": 30,
    "yearly": 365,
}


@login_required
def dashboard(request):
    period = request.GET.get("period", "monthly")
    days = PERIOD_TO_DAYS.get(period, 30)
    end_date = timezone.localdate()
    start_date = end_date - timedelta(days=days - 1)

    transactions = Transaction.objects.filter(
        user=request.user,
        transaction_date__range=(start_date, end_date),
    ).select_related("category")

    income = transactions.filter(transaction_type=Transaction.TransactionType.INCOME).aggregate(
        total=Sum("amount")
    )["total"] or Decimal("0")
    expense = transactions.filter(transaction_type=Transaction.TransactionType.EXPENSE).aggregate(
        total=Sum("amount")
    )["total"] or Decimal("0")

    lifetime = Transaction.objects.filter(user=request.user).aggregate(
        total_income=Sum(
            Case(
                When(transaction_type=Transaction.TransactionType.INCOME, then=F("amount")),
                default=Value(0),
                output_field=DecimalField(max_digits=12, decimal_places=2),
            )
        ),
        total_expense=Sum(
            Case(
                When(transaction_type=Transaction.TransactionType.EXPENSE, then=F("amount")),
                default=Value(0),
                output_field=DecimalField(max_digits=12, decimal_places=2),
            )
        ),
    )

    lifetime_income = lifetime["total_income"] or Decimal("0")
    lifetime_expense = lifetime["total_expense"] or Decimal("0")
    balance = lifetime_income - lifetime_expense

    trends = _trend_data(transactions, period)
    category_breakdown = (
        transactions.values("category__name", "category__color", "transaction_type")
        .annotate(total=Sum("amount"))
        .order_by("-total")
    )

    context = {
        "transaction_form": TransactionForm(user=request.user),
        "category_form": CategoryForm(),
        "transactions": transactions[:20],
        "balance": balance,
        "income": income,
        "expense": expense,
        "net": income - expense,
        "period": period,
        "period_options": PERIOD_TO_DAYS.keys(),
        "trend_labels": json.dumps([point["label"] for point in trends]),
        "trend_income": json.dumps([float(point["income"]) for point in trends]),
        "trend_expense": json.dumps([float(point["expense"]) for point in trends]),
        "category_breakdown": category_breakdown,
        "savings_rate": round(((income - expense) / income * 100), 2) if income else 0,
    }
    return render(request, "core/dashboard.html", context)


def _trend_data(queryset, period):
    truncator = {
        "daily": TruncDay("transaction_date"),
        "weekly": TruncWeek("transaction_date"),
        "monthly": TruncDay("transaction_date"),
        "yearly": TruncMonth("transaction_date"),
    }.get(period, TruncDay("transaction_date"))

    grouped = (
        queryset.annotate(window=truncator)
        .values("window")
        .annotate(
            income=Sum(
                Case(
                    When(transaction_type=Transaction.TransactionType.INCOME, then=F("amount")),
                    default=Value(0),
                    output_field=DecimalField(max_digits=12, decimal_places=2),
                )
            ),
            expense=Sum(
                Case(
                    When(transaction_type=Transaction.TransactionType.EXPENSE, then=F("amount")),
                    default=Value(0),
                    output_field=DecimalField(max_digits=12, decimal_places=2),
                )
            ),
        )
        .order_by("window")
    )

    return [
        {
            "label": item["window"].strftime("%b %d" if period != "yearly" else "%b %Y"),
            "income": item["income"] or 0,
            "expense": item["expense"] or 0,
        }
        for item in grouped
        if item["window"]
    ]


@login_required
def add_transaction(request):
    if request.method != "POST":
        return redirect("dashboard")

    form = TransactionForm(request.POST, user=request.user)
    if form.is_valid():
        transaction = form.save(commit=False)
        transaction.user = request.user
        transaction.save()
        messages.success(request, "Transaction added successfully.")
    else:
        messages.error(request, "Please correct the transaction form errors.")
    return redirect("dashboard")


@login_required
def add_category(request):
    if request.method != "POST":
        return redirect("dashboard")

    form = CategoryForm(request.POST)
    if form.is_valid():
        category = form.save(commit=False)
        category.user = request.user
        category.save()
        messages.success(request, "Category created.")
    else:
        messages.error(request, "Please correct the category form errors.")
    return redirect("dashboard")


@login_required
def delete_transaction(request, transaction_id):
    if request.method == "POST":
        transaction = get_object_or_404(Transaction, pk=transaction_id, user=request.user)
        transaction.delete()
        messages.info(request, "Transaction deleted.")
    return redirect("dashboard")
