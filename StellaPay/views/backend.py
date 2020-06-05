from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render, redirect

from StellaPay.models import Transaction, Customer


@login_required()
def index(request):
    # Find the 10 recent transactions
    recent_transactions = Transaction.objects.order_by("-date_time")[:10]

    # Find outstanding debts of all individuals
    outstanding_debts = Transaction.objects.values("buyer__email").annotate(total_debt=Sum("price"))

    # Create a dictionary with key = debtor name, value = total debt
    debt_owners = {}

    # Loop through the result of the queryset
    for debt in outstanding_debts:
        # Find the email of the debtor
        debt_owner_email = debt["buyer__email"]
        # Find the total debt of this user
        total_debt = debt["total_debt"]

        # Look up the name of the user by its email
        debt_owner_full_name = str(Customer.objects.get(email=debt_owner_email))

        # Store the full name and their debt
        debt_owners[debt_owner_full_name] = float(total_debt)

    context = {"transactions": recent_transactions,
               "debts": debt_owners}

    return render(request, 'backend/homepage.html', context)


@login_required
def user_activity(request):
    return render(request, 'backend/user-activity.html')


def login(request):
    # If user is already authenticated, move them to the homepage.
    if request.user.is_authenticated:
        return redirect("/backend/")
    return render(request, 'backend/login-page.html')
