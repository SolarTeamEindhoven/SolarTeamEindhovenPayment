import json
import locale
from datetime import datetime

import pytz
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt

from StellaPay.models import Transaction


@csrf_exempt
def get_transactions(request):
    """"Accept requests from /transactions/user/"""

    locale.setlocale(locale.LC_ALL, 'nl_NL')

    # Check if we have a POST request
    if request.method != "POST":
        return HttpResponseBadRequest("Your method should be POST")  # We expect a POST request

    # Try to grab the JSON data from the body of the POST request
    try:
        json_data = json.loads(request.body)
    except json.JSONDecodeError:
        return HttpResponseBadRequest("The given JSON was not valid")  # Invalid JSON

    begin_date = None
    end_date = None
    user_email = None

    # Try to read email from JSON
    try:
        user_email = str(json_data["email"])
    except KeyError:
        return HttpResponseBadRequest("No user email provided")

    transactions = Transaction.objects.filter(buyer__email=user_email)

    # Return an empty json response
    if len(transactions) < 1:
        return JsonResponse({})

    # Try to read begin date
    try:
        begin_date_string = str(json_data["begin_date"])

        begin_date = pytz.timezone('Europe/Amsterdam').localize(
            datetime.strptime(begin_date_string, "%Y/%m/%d %H:%M:%S")).astimezone(
            pytz.utc)

    except (KeyError, ValueError):
        # Ignore error
        pass

    # Try to read end date
    try:
        end_date_string = str(json_data["end_date"])

        end_date = pytz.timezone('Europe/Amsterdam').localize(
            datetime.strptime(end_date_string, "%Y/%m/%d %H:%M:%S")).astimezone(
            pytz.utc)

    except (KeyError, ValueError):
        # Ignore error
        pass

    # If we have a begin and/or end date, we can use that to filter.
    if begin_date is not None:
        transactions = transactions.filter(date_time__gte=begin_date)

    if end_date is not None:
        transactions = transactions.filter(date_time__lte=end_date)

    # Return list as json response
    return JsonResponse([{
        "email": transaction.buyer.email,
        "purchase_date": str(transaction.get_date_time_in_timezone()),
        "item_bought": str(transaction.item_bought.name),
        "total_price": transaction.price
    }
        for transaction in transactions], safe=False)
