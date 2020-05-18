from django.http import JsonResponse, HttpResponse

from StellaPay.models import Category


def get_categories(request):
    """"Accept requests from /categories"""

    # Check if user is authenticated
    if not request.user.is_authenticated:
        return HttpResponse("You need to be authenticated first", status=401)

    categories = []

    for category in Category.objects.all():
        categories.append({"name": category.name})

    # Return list as json response
    return JsonResponse(categories, safe=False)
