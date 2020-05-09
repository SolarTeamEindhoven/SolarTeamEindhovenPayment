import json
from datetime import datetime

import pytz
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from StellaPay.models import Transaction, Customer, Product


@csrf_exempt
def get_transactions(request):
    """"Accept requests from /transactions/user/"""

    # locale.setlocale(locale.LC_ALL, 'nl_NL')

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


@csrf_exempt
def make_transaction(request):
    """"Accept requests from /transactions/create/"""

    # Check if we have a POST request
    if request.method != "POST":
        return HttpResponseBadRequest("Your method should be POST")  # We expect a POST request

    # Try to grab the JSON data from the body of the POST request
    try:
        json_data = json.loads(request.body)
    except json.JSONDecodeError:
        return HttpResponseBadRequest("The given JSON was not valid")  # Invalid JSON

    products_bought = []

    # Try to read product list from JSON
    try:
        products_bought = list(json_data["products"])
    except KeyError:
        return HttpResponseBadRequest("No list of products was provided")

    # Return an empty json response
    if len(products_bought) < 1:
        return HttpResponseBadRequest("No list of products was provided")

    # For each product, try to parse it.
    for product_bought in products_bought:
        try:
            email = str(product_bought["email"])
        except KeyError:
            return HttpResponseBadRequest(f"No valid email (of a user) was provided for product {str(product_bought)}")

        try:
            product_name = str(product_bought["product_name"])
        except KeyError:
            return HttpResponseBadRequest(f"No valid product name was provided for product {str(product_bought)}")

        try:
            count = int(product_bought["amount"])
        except KeyError:
            return HttpResponseBadRequest(f"No valid amount was provided for product {str(product_bought)}")

        # Find the matching user
        try:
            matched_user = Customer.objects.get(email=email)
        except ObjectDoesNotExist:
            return HttpResponseBadRequest(f"There is no user with e-mail '{email}'.")

        # Find the matching product
        try:
            matched_product = Product.objects.get(name__iexact=product_name)
        except ObjectDoesNotExist:
            return HttpResponseBadRequest(f"There is no product with name '{product_name}'.")

        # Generate a new transaction
        new_transaction = Transaction(buyer=matched_user, item_bought=matched_product,
                                      price=matched_product.price * count)

        # And save it!
        new_transaction.save()

    # All went well, so now return 200 code.
    return HttpResponse(status=200)
