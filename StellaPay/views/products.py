from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse, HttpResponseNotFound

from StellaPay.models import Product


def get_products(request):
    """"Accept requests from /products/"""

    products = []

    for product in Product.objects.all():
        products.append({"name": product.name,
                         "price": str(product.price),
                         "shown": product.shown,
                         "category": product.category.name})

    # Return list as json response
    return JsonResponse(products, safe=False)


def get_product_info(request, product_name: str):
    """"Accept requests from /products/product/<product_name>"""

    matched_product = None

    # Try to find the product with the given name
    try:
        matched_product = Product.objects.get(name__iexact=product_name)
    except ObjectDoesNotExist:
        return HttpResponseNotFound("No product with that name found")

    return JsonResponse({
        "name": matched_product.name,
        "price": str(matched_product.price),
        "shown": matched_product.shown,
        "category": matched_product.category.name
    })


def get_products_of_category(request, category: str):
    """"Accept requests from /products/<category_name>"""
    products = []

    for product in Product.objects.filter(category__name__iexact=category):
        products.append({"name": product.name,
                         "price": str(product.price),
                         "shown": product.shown,
                         "category": product.category.name})

    # Return list as json response
    return JsonResponse(products, safe=False)
