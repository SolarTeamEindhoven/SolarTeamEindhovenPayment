from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum
from django.forms import model_to_dict
from django.shortcuts import render, redirect

from StellaPay.models import Transaction, Customer, RegistrationDevice


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
    context = {}

    if 'user' in request.GET:
        print("Looking for user", request.GET['user'])
        search_user_email = request.GET['user']
        try:
            # Look for a matching user
            matched_user = Customer.objects.get(email__icontains=search_user_email)

            # Save the user in the context so it's available to the template
            context["requested_user"] = matched_user
            # Also provide a dict-like object so we can serialize it to JSON and use in JS scripts
            context["js_requested_user"] = model_to_dict(matched_user)

            # Find recent transactions and save those in the context
            recent_transactions = Transaction.objects.filter(buyer=matched_user).order_by('-date_time')[:10]

            # Save recent transcations in the context
            context["recent_transactions"] = recent_transactions

            # Find registered devices of user
            registered_devices = RegistrationDevice.objects.filter(owner=matched_user)

            # Save to context
            context["registered_devices"] = registered_devices

        except ObjectDoesNotExist:
            # Do nothing
            pass

    # Put registered users in dropdown box
    context["all_members"] = Customer.objects.all()

    return render(request, 'backend/user-activity.html', context=context)


def login(request):
    # If user is already authenticated, move them to the homepage.
    if request.user.is_authenticated:
        return redirect("/backend/")
    return render(request, 'backend/login-page.html')
