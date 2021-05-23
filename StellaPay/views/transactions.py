import csv
import json
from datetime import datetime

import dateutil.parser
import pytz
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from StellaPay.models import Transaction, Customer, Product


@csrf_exempt
def get_transactions(request):
    """"Accept requests from /transactions/user/"""

    # Check if we have a POST request
    if request.method != "POST":
        return HttpResponseBadRequest("Your method should be POST")  # We expect a POST request

    # Check if user is authenticated
    if not request.user.is_authenticated:
        return HttpResponse("You need to be authenticated first", status=401)

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

    # Check if user is authenticated
    if not request.user.is_authenticated:
        return HttpResponse("You need to be authenticated first", status=401)

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


@csrf_exempt
def get_all_transactions(request):
    """"Accept requests from /transactions/all/"""

    # Check if we have a POST request
    if request.method != "POST":
        return HttpResponseBadRequest("Your method should be POST")  # We expect a POST request

    # Check if user is authenticated
    if not request.user.is_authenticated:
        return HttpResponse("You need to be authenticated first", status=401)

    # Try to grab the JSON data from the body of the POST request
    try:
        json_data = json.loads(request.body)
    except json.JSONDecodeError:
        return HttpResponseBadRequest("The given JSON was not valid")  # Invalid JSON

    begin_date = None
    end_date = None

    transactions = Transaction.objects.all()

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
def generate_transactions_csv(request):
    """"Accept requests from /transactions/generate_csv/"""

    # Check if we have a POST request
    if request.method != "POST":
        return HttpResponseBadRequest("Your method should be POST")  # We expect a POST request

    # Check if user is authenticated
    if not request.user.is_authenticated:
        return HttpResponse("You need to be authenticated first", status=401)

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
        user_email = None
        # No user provided, so find transactions of all users

    transactions = None

    if (user_email is None):
        transactions = Transaction.objects.all()
    else:
        transactions = Transaction.objects.filter(buyer__email=user_email)

    # Return an empty json response
    if len(transactions) < 1:
        return HttpResponse("There is no data.", status=200)

    # Try to read begin date
    try:
        begin_date_string = str(json_data["begin_date"])

        begin_date = dateutil.parser.parse(begin_date_string)  # Use ISO 8601

    except (KeyError, ValueError):
        # Ignore error
        pass

    # Try to read end date
    try:
        end_date_string = str(json_data["end_date"])

        end_date = dateutil.parser.parse(end_date_string)

    except (KeyError, ValueError):
        # Ignore error
        pass

    print(begin_date)
    print(end_date)

    # If we have a begin and/or end date, we can use that to filter.
    if begin_date is not None:
        transactions = transactions.filter(date_time__gte=begin_date)

    if end_date is not None:
        transactions = transactions.filter(date_time__lte=end_date)

    # Generate a response object to use for the CSV writer
    response = HttpResponse(content_type='text/csv', status=200)
    response['Content-Disposition'] = 'attachment; filename="transactions.csv"'

    # Open the CSV writer
    writer = csv.writer(response)

    # Write first row
    writer.writerow(['User', 'Email', 'Date time', 'Item bought', 'Price'])

    # Write transactions into the CSV file
    for transaction in transactions:
        writer.writerow([transaction.buyer.get_full_name(), transaction.buyer.email, transaction.date_time,
                         transaction.item_bought.name, transaction.price])

    return response


@csrf_exempt
def generate_special_transactions_csv(request):
    """"Accept requests from /transactions/generate_special_csv/"""
    # This function differs from the other generate_csv method in the fact that it will always output all data of a user
    # (or all users) in the same format. This means the products will always be present in the same order.

    # User 1:
    #   Consumption 1: 5
    #   Consumption 2: 3
    #   Consumption 3: 10
    # User 2:
    #   Consumption 1: 17
    #   Consumption 2: 1
    #   Consumption 3: 3

    # Check if we have a POST request
    if request.method != "POST":
        return HttpResponseBadRequest("Your method should be POST")  # We expect a POST request

    # Check if user is authenticated
    if not request.user.is_authenticated:
        return HttpResponse("You need to be authenticated first", status=401)

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
        user_email = None
        # No user provided, so find transactions of all users

    transactions = None

    if (user_email is None):
        transactions = Transaction.objects.all()
    else:
        transactions = Transaction.objects.filter(buyer__email=user_email)

    # Return an empty json response
    if len(transactions) < 1:
        return HttpResponse("There is no data.", status=200)

    # Try to read begin date
    try:
        begin_date_string = str(json_data["begin_date"])

        begin_date = dateutil.parser.parse(begin_date_string)  # Use ISO 8601

    except (KeyError, ValueError):
        # Ignore error
        pass

    # Try to read end date
    try:
        end_date_string = str(json_data["end_date"])

        end_date = dateutil.parser.parse(end_date_string)

    except (KeyError, ValueError):
        # Ignore error
        pass

    # If we have a begin and/or end date, we can use that to filter.
    if begin_date is not None:
        transactions = transactions.filter(date_time__gte=begin_date)

    if end_date is not None:
        transactions = transactions.filter(date_time__lte=end_date)

    # Generate a response object to use for the CSV writer
    response = HttpResponse(content_type='text/csv', status=200)
    response['Content-Disposition'] = 'attachment; filename="transactions.csv"'

    # Open the CSV writer
    writer = csv.writer(response)

    # Write first row
    writer.writerow(['User', 'Item bought', 'Total price'])

    # Store the transactions before writing them to the CSV
    # We need to sort the dict keys and values first, so that's why we use an intermediate representation
    # The format of the dict is as follows:
    # The key is the username
    # The value is another (ordered dict), where its key is a product name and the value is the float value
    transformed_transactions = {}

    # Keep track of unique products so we put all products in the csv for all user entries.
    unique_products = [product.name for product in Product.objects.distinct()]

    # Store transactions in intermediate representation
    for transaction in transactions:

        user_name = transaction.buyer.get_full_name()
        product = transaction.item_bought.name

        # If there is no entry for this user, we create one
        if user_name not in transformed_transactions:
            transformed_transactions[user_name] = {}

            # Set all products for this user to zero.
            for unique_product in unique_products:
                transformed_transactions[user_name][unique_product] = 0

        # Now add this transaction to the corresponding product category
        transformed_transactions[user_name][product] += transaction.price

    # Now loop over all users (in sorted order) and write their data into the csv file
    for user_name, transactions in sorted(transformed_transactions.items()):
        for product, total_price in sorted(transactions.items()):
            writer.writerow([user_name, product, total_price])

    return response
