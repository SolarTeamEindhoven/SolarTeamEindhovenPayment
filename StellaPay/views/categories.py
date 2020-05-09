from django.http import JsonResponse

from StellaPay.models import Category


def get_categories(request):
    """"Accept requests from /categories"""
    categories = []

    for category in Category.objects.all():
        categories.append({"name": category.name})

    # Return list as json response
    return JsonResponse(categories, safe=False)
