from django.apps import apps
from django.contrib import admin

# Loop through all registered apps
for app_config in apps.get_app_configs():
    models = app_config.get_models()

    # Register each model in the app
    for model in models:
        # Collect field names for list_display and list_filter
        field_names = [field.name for field in model._meta.fields]
        
        # Collect field names for search_fields, excluding related fields
        search_field_names = [field.name for field in model._meta.fields if not field.related_model]

        # Register the model with the admin site, with dynamic list_display, list_filter, and search_fields
        admin.site.register(
            model,
            list_display=field_names,
            list_filter=field_names,
            search_fields=search_field_names
        )
