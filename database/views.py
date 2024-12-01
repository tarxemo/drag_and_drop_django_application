from django.http import Http404
from authApp.models import DynamicModelLog
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import json
from django.core.management import call_command
from django.apps import apps
from .database_helpers import *
from .utils import *

def makemigrations_and_migrate():
    call_command('makemigrations')
    call_command('migrate')
    
def get_model_and_app_name(model_name):
    """Return the model and the app name where the model belongs."""
    for app_config in apps.get_app_configs():
        try:
            model = apps.get_model(app_config.label, model_name)
            if model:
                return model, app_config.label  
        except LookupError:
            continue  # Continue to the next app if the model is not found in the current app

    raise Http404(f"Model '{model_name}' not found in any registered app.")

class ModelFieldsFileView(APIView):
    def get(self, request, *args, **kwargs):
        table_name = request.query_params.get('model_name', None)

        # Filter for specific model if table_name is provided
        if table_name:
            models_data = parse_models_file(table_name)
        else: 
            models_data = parse_models_file()
        return Response(models_data, status=status.HTTP_200_OK)


class DynamicModelAPIView(APIView):
    def get(self, request, *args, **kwargs):
        model_name = request.query_params.get('model_name', None)

        # Filter for specific model if table_name is provided
        if model_name:
            models_data = parse_models_file(model_name)
        else: 
            models_data = parse_models_file()
        return Response(models_data, status=status.HTTP_200_OK)


    def post(self, request):
        """Create a new model (table)."""
        try:
            print("**********************")
            data = json.loads(request.body.decode('utf-8'))
            print(data)
            model_name = data.get('model_name')
            fields = data.get('fields')

            if not model_name or not fields:
                return Response({"error": "Model name and fields are required."}, status=status.HTTP_400_BAD_REQUEST)

            # Create the model dynamically
            create_model_file(model_name, fields)
            
            DynamicModelLog.objects.create(
                user=request.user if request.user.is_authenticated else None,
                model_name=model_name,
            )
            
            return Response({"status": "success", "message": f"Model {model_name} created and migrations applied!"}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request):
        model_name = request.query_params.get('model_name')
        """Update the structure of an existing model."""
        try:
            data = json.loads(request.body.decode('utf-8'))
            print(data)
            fields = data.get('fields')

            # Check if fields are provided
            if not fields or not isinstance(fields, dict):
                return Response({"error": "Fields are required to update the model."}, status=status.HTTP_400_BAD_REQUEST)
            model, app_name = get_model_and_app_name(model_name)
            # Modify the model's fields dynamically
            modify_model_file(model_name, fields, app_name)

            return Response({"status": "success", "message": f"Model {model_name} updated!"}, status=status.HTTP_200_OK)
        except json.JSONDecodeError:
            return Response({"error": "Invalid JSON format."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def delete(self, request):
        model_name = request.query_params.get('model_name', None)
        """Delete an existing model (table)."""
        try:
            # Read the file and remove the model class
            delete_model_file(model_name)

            return Response({"status": "success", "message": f"Model {model_name} deleted!"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Helper functions to handle the model operations



import requests
from django.shortcuts import render, redirect
from django.urls import reverse
from django.conf import settings
from django.contrib import messages

API_BASE_URL = 'http://127.0.0.1:8000/models/model/'  # Update this to your API's URL

# List all models
def list_models(request):
    response = requests.get(API_BASE_URL)
    models = response.json()
    
    return render(request, 'database/templates/list_models.html', {'models': models})

# View model details
def view_model(request):
    model_name = request.GET.get('model_name', None)  # Use GET instead of query_params
    if model_name:
        response = requests.get(f"{API_BASE_URL}?model_name={model_name}")
        if response.status_code == 200:
            model_details = response.json()
        else:
            details = {}  # Handle case if the request fails

        return render(request, 'database/templates/view_model.html', {'model_name': model_name, 'model_details': model_details})
    else:
        # Handle case if model_name is not provided in the request
        return render(request, 'database/templates/view_model.html', {'error': 'Model name not provided'})

# Create a new model
def create_model(request):
    if request.method == 'POST':
        model_name = request.POST['model_name']
        fields = {}  # You would parse fields from the form, potentially using JavaScript to add more fields
        
        # Prepare and send the POST request
        response = requests.post(API_BASE_URL, json={'model_name': model_name, 'fields': fields})
        
        if response.status_code == 201:
            messages.success(request, f'Model {model_name} created successfully!')
            return redirect('list_models')
        else:
            messages.error(request, 'Error creating model.')
    
    return render(request, 'database/templates/create_model.html')

# Edit a model
def edit_model(request):
    model_name = request.GET.get('model_name', None)
    if request.method == 'POST':
        fields = {}  # Parse fields for modification or deletion
        
        # Prepare and send the PUT request
        response = requests.put(f"{API_BASE_URL}?model_name={model_name}")
        
        if response.status_code == 200:
            messages.success(request, f'Model {model_name} updated successfully!')
            return redirect('view_model', model_name=model_name)
        else:
            messages.error(request, 'Error updating model.')
    
    # Display current fields for editing
    response = requests.get(f"{API_BASE_URL}?model_name={model_name}")
    model_details = response.json()
    return render(request, 'database/templates/edit_model.html', {'model_name': model_name, 'model_details': model_details})

# Delete a model
def delete_model(request):
    if request.method == 'POST':
        model_name = request.POST.get("model_name")
        
        response = requests.delete(f"{API_BASE_URL}?model_name={model_name}")
        
        if response.status_code == 204:
            messages.success(request, f'Model {model_name} deleted successfully!')
            return redirect('list_models')
        else:
            messages.error(request, 'Error deleting model.')
    
    return render(request, 'database/templates/delete_model.html', {'model_name': model_name})
