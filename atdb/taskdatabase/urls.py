from django.urls import path

from .views import index, DataProductListView, DataProductDetailsView

urlpatterns = [
    # ex: /atdb/
    path('', index, name='index'),

    # ex: /atdb/dataproducts/
    path('dataproducts/', DataProductListView.as_view()),

    # ex: /atdb/dataproducts/5/
    # path('dataproducts/<int:dataproduct_id>/', DataProductDetailsView.as_view()),
    path('dataproducts/<int:pk>/', DataProductDetailsView.as_view()),
]