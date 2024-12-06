from django.apps import apps
from django.contrib import admin
from .models import *

app_config = apps.get_app_config('database')

models = app_config.get_models()

for model in models:
    field_names = [field.name for field in model._meta.fields]
    search_field_names = [field.name for field in model._meta.fields]

    for field in model._meta.fields:
        if field.related_model:
            related_field_name = f'{field.name}'
            if related_field_name in search_field_names:
                search_field_names.remove(related_field_name)

    admin.site.register(model, list_display=field_names, list_filter=field_names, search_fields=search_field_names)