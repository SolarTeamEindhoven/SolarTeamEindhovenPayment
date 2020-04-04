import json

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseNotFound, JsonResponse, HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt

from StellaPay.models import RegistrationDevice, Customer


def check_identification(request, card_id=None):
    """"Accept requests from /identification/request-user/"""

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
    """Accept requests from /identification/set-card-mapping/"""

    # Check if we have a POST request
    if request.method != "POST":
        return HttpResponseBadRequest("Your method should be POST")  # We expect a POST request

    # Try to grab the JSON data from the body of the POST request
    json_data = json.loads(request.body)

    card_id = None
    user_email = None

    # Try to read the card id from JSON
    try:
        card_id = int(json_data["card_id"])
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
