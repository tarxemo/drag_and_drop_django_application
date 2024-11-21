from django.apps import apps
from rest_framework import serializers
from django.conf import settings

def create_dynamic_serializers(app_names=None):
    """
    This function dynamically creates serializers for all models in the specified apps.
    If no app_names are provided, it creates serializers for all installed apps in settings.
    """
    serializers_dict = {}

    # If app_names are not provided, get all installed apps
    if app_names is None:
        app_names = [app.name for app in apps.get_app_configs() if app.name in settings.INSTALLED_APPS]

    for app_name in app_names:
        try:
            # Get the app configuration
            app_config = apps.get_app_config(app_name)
        except LookupError:
            # If the app is not found, skip it
            continue

        models = app_config.get_models()

        for model in models:
            # Create a dynamic Meta class for the serializer
            class MetaFactory:
                def __init__(self, model):
                    self.model = model
                    self.fields = '__all__'

            def create_serializer(model):
                # Define the Meta class dynamically
                meta_class = MetaFactory(model)

                # Define the serializer class
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

                return DynamicModelSerializer

            # Store the serializer class in the dictionary
            serializers_dict[model.__name__] = create_serializer(model)

    return serializers_dict
