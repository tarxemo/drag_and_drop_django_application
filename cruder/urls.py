from django.urls import path
from .views import *

urlpatterns = [
    path('<str:table_name>/', DynamicCRUDView.as_view(), name='dynamic-list-create'),  # List and Create
    path('<str:table_name>/<int:pk>/', DynamicCRUDView.as_view(), name='dynamic-detail'), # List and Create
    path('<str:table_name>/<uuid:pk>/', DynamicCRUDView.as_view(), name='dynamic-detail'),
    path('payload/<str:table_name>/<str:method>/', SamplePayloadAPIView.as_view(), name='sample-payload'),
]