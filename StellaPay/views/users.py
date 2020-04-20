from django.http import JsonResponse

from StellaPay.models import Customer


def get_users(request):
    """"Accept requests from /users/"""

    users = []

    for user in Customer.objects.all():
        users.append({"name": str(user),
                      "email": str(user.email)})

    # Return list as json response
    return JsonResponse(users, safe=False)
