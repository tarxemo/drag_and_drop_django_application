from django.urls import path
from .views import  *

urlpatterns = [
    path('create_django_project/', create_django_project, name='create_django_project'),
    path('your_table_name/', list_view, name='your_table_list'),

]
