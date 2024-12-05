# utils.py
import re
import os
from django.conf import settings

def parse_models_file(model_name=None):
    # Define the path to models.py
    models_path = os.path.join(settings.BASE_DIR, 'cruder', 'models.py')
    models_data = []

    # Regex patterns to capture model and field details
    model_pattern = re.compile(r'^class\s+(\w+)\(models\.Model\):')
    field_pattern = re.compile(r'^\s+(\w+)\s*=\s*models\.(\w+)\((.*?)\)')

    current_model = None

    with open(models_path, 'r') as file:
        for line in file:
            # Check if the line defines a model
            model_match = model_pattern.match(line)
            if model_match:
                # If there's an ongoing model, add it to the list before starting a new one
                if current_model:
                    models_data.append(current_model)

                    # If searching for a specific model and it matches, return it immediately
                    if model_name and current_model["model_name"] == model_name:
                        return current_model

                # Start a new model
                model_name_match = model_match.group(1)
                current_model = {
                    "model_name": model_name_match,
                    "fields": {}
                }

            # Check if the line defines a field inside the current model
            elif current_model and (field_match := field_pattern.match(line)):
                field_name = field_match.group(1)
                field_type = field_match.group(2)
                params_str = field_match.group(3)

                # Parse field parameters from params_str
                params = parse_field_params(params_str)

                # Add the field to the current model
                current_model["fields"][field_name] = {
                    "type": field_type,
                    "params": params
                }

    # After finishing the loop, ensure the last model is added
    if current_model:
        models_data.append(current_model)

        # If searching for a specific model and it matches, return it now
        if model_name and current_model["model_name"] == model_name:
            return current_model

    # If a specific model was requested but not found, return None
    if model_name:
        return None

    # Return all models if no specific model was requested
    return models_data

def parse_field_params(params_str):
    # Parse parameters from a string like "max_length=255, unique=True"
    params = {}
    for param in params_str.split(','):
        key_value = param.strip().split('=')
        
        if len(key_value) == 2:
            key, value = key_value
            key = key.strip()
            value = value.strip()

            # Determine the value type and convert accordingly
            if value == "True":
                params[key] = {"value": True, "value_type": "boolean"}
            elif value == "False":
                params[key] = {"value": False, "value_type": "boolean"}
            elif value.isdigit():
                params[key] = {"value": int(value), "value_type": "integer"}
            elif value.startswith("models.") or value == "":
                # Handle Django constants or empty strings for model references
                params[key] = {
                    "value": value if value else "", 
                    "value_type": "django_constant" if value.startswith("models.") else "model_reference"
                }
            else:
                # Assume it's a string and strip any quotes
                params[key] = {"value": value.strip('"\'"'), "value_type": "string"}

    return params
