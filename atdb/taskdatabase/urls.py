from django.urls import path

from . import views

urlpatterns = [
    # ex: /atdb/
    path('', views.index, name='index'),

    # ex: /atdb/dataproducts/
    path('dataproducts/', views.DataProductListView.as_view()),

    # ex: /atdb/dataproducts/5/
    path('dataproducts/<int:pk>/', views.DataProductDetailsView.as_view(),name='dataproduct-detail-view'),

    # ex: /atdb/observations/
    path('observations/', views.ObservationListView.as_view()),

    # ex: /atdb/observations/5/
    path('observations/<int:pk>/', views.ObservationDetailsView.as_view()),

    path('locations/', views.LocationListView.as_view()),
    path('locations/<int:pk>/', views.LocationDetailsView.as_view(),name='location-detail-view'),
    path('status/', views.StatusListView.as_view()),
    path('status/<int:pk>/', views.StatusDetailsView.as_view(), name='status-detail-view'),
]