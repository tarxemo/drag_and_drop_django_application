from django.apps import apps
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import json
import os
from django.core.management import call_command
from django.apps import apps
from django.conf import settings
from rest_framework.permissions import IsAuthenticated


def get_all_models():
    """Helper function to get all models in all registered apps."""
    all_models = []
    
    # Iterate through all registered app configs
    for app_config in apps.get_app_configs():
        models = app_config.get_models()
        all_models.extend(models)  # Extend the list with models from each app

    return all_models

import os
import json
from django.conf import settings

def format_param(value, value_type):
    """Format parameter based on its type."""
    if value_type == 'integer' or value_type == 'boolean':
        return str(value)
    elif value_type == 'special':
        return value  # Directly use special values like models.CASCADE
    elif value_type == 'reference':
        return f'{value}'  # For referenced tables (e.g., ForeignKey)
    else:
        return f'"{value}"'  # Default to quoted string

def create_model_file(model_name, fields):
    """Helper function to create a model file dynamically."""
    app_name = 'cruder'  # Specify your app name
    models_file_path = os.path.join(settings.BASE_DIR, app_name, 'models.py')

    # Generate field definitions with correct indentation
    field_definitions = ''
    for field_name, field_info in fields.items():
        field_type = field_info.get('type')
        field_params = field_info.get('params', {})

        # Convert params dictionary to string representation of the arguments
        params_str_list = []
        for key, value in field_params.items():
            value_type = value.get('value_type')
            value = value.get('value')
            
            # Use format_param to correctly process each parameter
            param_str = f"{key}={format_param(value, value_type)}"
            params_str_list.append(param_str)

        params_str = ', '.join(params_str_list)

        # Generate the field line for the model class with proper indentation
        field_definitions += f'    {field_name} = models.{field_type}({params_str})\n'

    # Create the model class dynamically
    model_definition = f"""
class {model_name}(models.Model):
{field_definitions}
def __str__(self):
    return self.title
    """

    # Append the model definition to the models.py file
    with open(models_file_path, 'a') as models_file:
        models_file.write(model_definition)

    print(f'Model {model_name} added to {models_file_path}')


def generate_field_definition(field_name, field_info):
    """Helper function to generate a field definition string."""
    field_type = field_info.get('type')
    field_params = field_info.get('params', {})
    params_str = ', '.join([f'{key}={json.dumps(value)}' for key, value in field_params.items()])

    return f'    {field_name} = models.{field_type}({params_str})'
import os
import json
from django.conf import settings
from django.apps import apps

def modify_model_file(model_name, fields, app_name):
    """Helper function to modify an existing model with automated detection for add, modify, and delete actions."""
    models_file_path = os.path.join(settings.BASE_DIR, app_name, 'models.py')

    # Fetch the current fields from the existing model class
    current_model = apps.get_model(app_name, model_name)
    current_fields = {f.name: f for f in current_model._meta.get_fields() if f.concrete}

    # Classify fields as add, modify, or delete
    fields_to_add = {}
    fields_to_modify = {}
    fields_to_delete = {field_name: current_fields[field_name] for field_name in current_fields if field_name not in fields}

    for field_name, field_info in fields.items():
        if field_name in current_fields:
            fields_to_modify[field_name] = field_info
        else:
            fields_to_add[field_name] = field_info

    # Read the models.py file content
    with open(models_file_path, 'r') as models_file:
        lines = models_file.readlines()

    new_lines = []
    in_model_class = False

    def format_param(value, value_type):
        """Format parameter based on its type."""
        if value_type == 'integer' or value_type == 'boolean':
            return str(value)
        elif value_type == 'special':
            return value  # Directly use special values like `models.CASCADE`
        elif value_type == 'reference':
            return f'{value}'  # For referenced tables (e.g., ForeignKey)
        else:
            return f'"{value}"'  # Default to quoted string

    # Process each line and update based on field classification
    for line in lines:
        if f'class {model_name}' in line:
            in_model_class = True
            new_lines.append(line)

            # Add fields
            for field_name, field_info in fields_to_add.items():
                field_type = field_info.get('type')
                field_params = field_info.get('params', {})

                params_str_list = [
                    f"{key}={format_param(value['value'], value['value_type'])}" if value['value_type'] != 'reference'
                    else f"{format_param(value['value'], value['value_type'])}"
                    for key, value in field_params.items()
                ]
                params_str = ', '.join(params_str_list)

                new_lines.append(f'    {field_name} = models.{field_type}({params_str})\n')
            continue

        if in_model_class:
            if line.strip().startswith('class ') or line.strip() == "":
                in_model_class = False
                new_lines.append(line)
                continue

            if '=' in line and line.startswith('    '):
                field_name = line.split('=')[0].strip()

                if field_name in fields_to_delete:
                    # Field to delete, skip this line
                    continue

                elif field_name in fields_to_modify:
                    # Field to modify
                    field_info = fields_to_modify[field_name]
                    field_type = field_info.get('type')
                    field_params = field_info.get('params', {})

                    params_str_list = [
                        f"{key}={format_param(value['value'], value['value_type'])}" if value['value_type'] != 'reference'
                        else f"{format_param(value['value'], value['value_type'])}"
                        for key, value in field_params.items()
                    ]
                    params_str = ', '.join(params_str_list)

                    new_lines.append(f'    {field_name} = models.{field_type}({params_str})\n')
                else:
                    # Field remains unchanged
                    new_lines.append(line)

        else:
            new_lines.append(line)

    # Write modified lines back to models.py
    with open(models_file_path, 'w') as models_file:
        models_file.writelines(new_lines)

    print(f'Model {model_name} modified in {models_file_path}')

def delete_model_file(model_name):
    """Helper function to delete an existing model."""
    app_name = 'cruder'  # Specify your app name
    models_file_path = os.path.join(settings.BASE_DIR, app_name, 'models.py')

    # Read the file and remove the model class
    with open(models_file_path, 'r') as models_file:
        lines = models_file.readlines()

    new_lines = []
    in_model_class = False
    for line in lines:
        if f'class {model_name}' in line:
            print("*********************")
            in_model_class = True
        elif in_model_class and line.strip().startswith('class '):
            print("##################################")
            in_model_class = False
        if in_model_class:
            pass  # Skip lines of the model class to delete
        else:
            print(line)
            new_lines.append(line)

    with open(models_file_path, 'w') as models_file:
        models_file.writelines(new_lines)

    print(f'Model {model_name} deleted from {models_file_path}')


