from django.shortcuts import render

from StellaPay.models import Transaction


def index(request):
    transactions = Transaction.objects.order_by("-date_time")[:10]

    context = {"transactions": transactions}

    return render(request, 'backend/homepage.html', context)


def user_activity(request):
    return render(request, 'backend/user-activity.html')
