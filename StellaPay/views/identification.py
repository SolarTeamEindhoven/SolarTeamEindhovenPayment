import json
from json.decoder import JSONDecodeError

from django.contrib.auth import authenticate, login
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseNotFound, JsonResponse, HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt

from StellaPay.models import RegistrationDevice, Customer


def check_identification(request, card_id=None):
    """"Accept requests from /identification/request-user/"""

    # Check if user is authenticated
    if not request.user.is_authenticated:
        return HttpResponse("You need to be authenticated first", status=401)

    matched_device = None

    # Try to find a card with the given id
    try:
        matched_device = RegistrationDevice.objects.get(uuid=card_id)
    except ObjectDoesNotExist:
        return HttpResponseNotFound("No registration device with that id found")

    # Return found card in JSON response (along with the owner of the card)
    return JsonResponse(
        {"card_id": matched_device.uuid,
         "owner": {
             "name": str(matched_device.owner),
             "email": str(matched_device.owner.email)
         }})


@csrf_exempt
def generate_card_mapping(request):
    """Accept requests from /identification/add-card-mapping/"""

    # Check if we have a POST request
    if request.method != "POST":
        return HttpResponseBadRequest("Your method should be POST")  # We expect a POST request

    # Check if user is authenticated
    if not request.user.is_authenticated:
        return HttpResponse("You need to be authenticated first", status=401)

    # Try to grab the JSON data from the body of the POST request
    json_data = None

    try:
        json_data = json.loads(request.body)
    except JSONDecodeError:
        return HttpResponseBadRequest("Your body does not contain JSON.")

    card_id = None
    user_email = None

    # Try to read the card id from JSON
    try:
        card_id = str(json_data["card_id"])
    except KeyError:
        return HttpResponseBadRequest("No card id provided")

    # Try to read email from JSON
    try:
        user_email = str(json_data["email"])
    except KeyError:
        return HttpResponseBadRequest("No user email provided")

    # Check if the card already exists
    if len(RegistrationDevice.objects.filter(uuid=card_id)) > 0:
        # We already found a card with that id
        return HttpResponse("This card id is already registered", status=403)

    matched_user = None

    # Check if email exists
    try:
        matched_user = Customer.objects.get(email=user_email)
    except ObjectDoesNotExist:
        return HttpResponse("There is no user with that e-mail.", status=403)

    # Create new registration device
    new_registration_device = RegistrationDevice(uuid=card_id, owner=matched_user)

    # Save it in database
    new_registration_device.save()

    return HttpResponse("Card mapping is set to " + str(matched_user), status=200)


def get_cards_of_user(request, email: str):
    """Accept requests from /identification/cards-of-user/<email>"""

    # Check if user is authenticated
    if not request.user.is_authenticated:
        return HttpResponse("You need to be authenticated first", status=401)

    # Does a user with this email address exist?
    try:
        matched_user = Customer.objects.get(email=email)
    except ObjectDoesNotExist:
        return HttpResponse("There is no user with that e-mail.", status=403)

    cards = RegistrationDevice.objects.filter(owner__email=email)

    return JsonResponse([{"card_id": card.uuid,
                          "owner": {
                              "name": str(card.owner),
                              "email": str(card.owner.email)
                          }} for card in cards], safe=False)


@csrf_exempt
def authenticate_request(request):
    # Check if we have a POST request
    if request.method != "POST":
        return HttpResponseBadRequest("Your method should be POST")  # We expect a POST request

    # Check if the user is already registered
    if request.user.is_authenticated:
        return HttpResponseBadRequest("You are already logged in!")

    # Try to grab the JSON data from the body of the POST request
    json_data = None

    try:
        json_data = json.loads(request.body)
    except JSONDecodeError:
        return HttpResponseBadRequest("Your body does not contain JSON.")

    username = None
    password = None

    # Try to read the card id from JSON
    try:
        username = str(json_data["username"])
    except KeyError:
        return HttpResponseBadRequest("No username provided")

    # Try to read password from JSON
    try:
        password = str(json_data["password"])
    except KeyError:
        return HttpResponseBadRequest("No password provided")

    # Try to authenticate the user
    user = authenticate(request, username=username, password=password)

    # Check if the credentials were correct
    if user is not None:
        # If so, store the authenticated user as requested
        login(request=request, user=user)
        return HttpResponse("Successfully logged in", status=200)
    else:
        return HttpResponse("Credentials were incorrect", status=406)
