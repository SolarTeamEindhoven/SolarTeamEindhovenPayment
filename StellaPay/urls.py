"""StellaPay URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.urls import path

from .views import identification, users, products, transactions, categories, backend

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    path('backend/', backend.index, name="backend-homepage"),
    path('backend/login', backend.login, name="backend-login"),
    path('backend/user-activity/', backend.user_activity, name="backend-user-activity"),
    path('identification/request-user/<str:card_id>', identification.check_identification),
    path('identification/cards-of-user/<str:email>', identification.get_cards_of_user),
    path('identification/add-card-mapping', identification.generate_card_mapping),
    path('identification/remove-card-mapping', identification.remove_card_mapping),
    path('users', users.get_users),
    path('products/<str:category>', products.get_products_of_category),
    path('products', products.get_products),
    path('products/product/<str:product_name>', products.get_product_info),
    path('categories', categories.get_categories),
    path('transactions/user', transactions.get_transactions),
    path('transactions/create', transactions.make_transaction),
    path('transactions/all', transactions.get_all_transactions),
    path('authenticate', identification.authenticate_request),
    path('deauthenticate', identification.deauthenticate),

]
