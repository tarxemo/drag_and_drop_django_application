from django.apps import apps
from rest_framework import serializers
from django.http import Http404

class DynamicModelHelper:
    
    def get_model_and_serializer(table_name):
        """
        Helper method to get the model and its corresponding serializer dynamically 
        across all registered apps.
        """
        # Get the model dynamically across all apps
        model = get_model_from_any_app(table_name)
        if not model:
            raise Http404(f"Table '{table_name}' not found")

        # Get or create the serializer class dynamically for the model
        serializer_class = get_dynamic_serializer_for_model(model)
        if not serializer_class:
            raise Http404(f"Serializer for table '{table_name}' not found")

        return model, serializer_class

def get_model_from_any_app(table_name):
    """
    Helper method to find the model by table_name from any registered app.
    """
    for app_config in apps.get_app_configs():
        try:
            model = app_config.get_model(table_name)
            return model
        except LookupError:
            continue  # If model is not found in this app, continue to the next
    return None

def get_dynamic_serializer_for_model(model):
    """
    Helper method to create a dynamic serializer for the given model.
    """
    # Create a dynamic Meta class for the serializer
    class MetaFactory:
        def __init__(self, model):
            self.model = model
            self.fields = '__all__'

    # Define the Meta class dynamically
    meta_class = MetaFactory(model)

    # Define the serializer class dynamically
    class DynamicModelSerializer(serializers.ModelSerializer):
        class Meta:
            model = meta_class.model
            fields = meta_class.fields

        def __init__(self, *args, **kwargs):
            fields = kwargs.pop('fields', None)
            super().__init__(*args, **kwargs)
            if fields is not None:
                allowed = set(fields)
                existing = set(self.fields.keys())
                for field in existing - allowed:
                    self.fields.pop(field)

    # Return the dynamically created serializer class
    return DynamicModelSerializer
