from .views import *
from django.urls import path

urlpatterns = [
    path('model/', DynamicModelAPIView.as_view(), name='dynamic-model-list-create'),
    path('model/<str:model_name>/', DynamicModelAPIView.as_view(), name='dynamic-model-detail'),
    
    path('', list_models, name='list_models'),
    path('view/', view_model, name='view_model'),
    path('create/', create_model, name='create_model'),
    path('edit/', edit_model, name='edit_model'),
    path('delete/', delete_model, name='delete_model'),
]