from django.http import JsonResponse, HttpResponse

from StellaPay.models import Customer


def get_users(request):
    """"Accept requests from /users/"""

    # Check if user is authenticated
    if not request.user.is_authenticated:
        return HttpResponse("You need to be authenticated first", status=401)

    users = []

    for user in Customer.objects.all():
        users.append({"name": str(user),
                      "email": str(user.email)})

    # Return list as json response
    return JsonResponse(users, safe=False)
