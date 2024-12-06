from django.apps import apps
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.apps import apps

from TB.utils import *
from datetime import datetime
from django.core.files.uploadedfile import SimpleUploadedFile
import json


class DynamicCRUDView(APIView):
    """
    View to dynamically handle CRUD operations on any model based on the table name received from the frontend.
    """
    
    
    def get(self, request, table_name, pk=None):
        """
        GET method to retrieve data from the specified table.
        If `pk` is provided, retrieve a specific record; otherwise, retrieve all records.
        """
        model, serializer_class = DynamicModelHelper.get_model_and_serializer(table_name)

        # Get the fields parameter from query parameters
        fields = request.query_params.get('fields', None)
        if fields:
            fields = fields.split(',')

        if pk:
            # Fetch a single record by primary key (id)
            try:
                instance = model.objects.get(pk=pk)
            except model.DoesNotExist:
                return Response({"error": "Object not found"}, status=status.HTTP_404_NOT_FOUND)
            
            serializer = serializer_class(instance, fields=fields)
        else:
            # Fetch all records
            queryset = model.objects.all()
            serializer = serializer_class(queryset, many=True, fields=fields)

        return Response(serializer.data)

    def post(self, request, table_name):
        """
        POST method to create a new record in the specified table.
        """
        model, serializer_class = DynamicModelHelper.get_model_and_serializer(table_name)
        serializer = serializer_class(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, table_name, pk):
        """
        PUT method to update an existing record in the specified table.
        """
        model, serializer_class = DynamicModelHelper.get_model_and_serializer(table_name)

        try:
            instance = model.objects.get(pk=pk)
        except model.DoesNotExist:
            return Response({"error": "Object not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = serializer_class(instance, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, table_name, pk):
        """
        DELETE method to delete a record from the specified table.
        """
        model, serializer_class = DynamicModelHelper.get_model_and_serializer(table_name)
        
        try:
            instance = model.objects.get(pk=pk)
        except model.DoesNotExist:
            return Response({"error": "Object not found"}, status=status.HTTP_404_NOT_FOUND)

        instance.delete()
        return Response({"message": "Deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


class SamplePayloadAPIView(APIView):
    def get(self, request, table_name=None, method=None):
        """Return a sample JSON payload for a given table and HTTP method."""
        if not table_name or not method:
            return Response({"error": "Table name and HTTP method are required."}, status=status.HTTP_400_BAD_REQUEST)

        model = self.get_model_from_any_app(table_name)
        if not model:
            return Response({"error": f"Model '{table_name}' not found."}, status=status.HTTP_404_NOT_FOUND)

        if method.lower() == 'post':
            sample_payload = self.generate_sample_payload(model)
        elif method.lower() == 'put':
            sample_payload = self.generate_sample_payload(model, update=True)
        elif method.lower() == 'get':
            sample_payload = {"detail": f"Use the URL `table_crud/{table_name}/<id>/` to retrieve a specific record."}
        elif method.lower() == 'delete':
            sample_payload = {"detail": f"Use the URL `table_crud/{table_name}/<id>/` to delete a specific record."}
        else:
            return Response({"error": "Unsupported HTTP method."}, status=status.HTTP_400_BAD_REQUEST)

        return Response(sample_payload, status=status.HTTP_200_OK)

    def get_model_from_any_app(self, table_name):
        """Attempt to retrieve the model from any registered app."""
        for app_config in apps.get_app_configs():
            try:
                model = app_config.get_model(table_name)
                return model
            except LookupError:
                continue  # If the model isn't found in this app, try the next one
        return None

    def generate_sample_payload(self, model, update=False):
        """Generate a sample payload based on the model fields, listing required fields first."""
        fields = model._meta.fields
        required_payload = {}
        optional_payload = {}

        for field in fields:
            if field.name == 'id':  # Skip 'id' field for POST requests
                continue

            # Check if the field is required
            if self.is_field_required(field):
                # Add "<required>" marker to required fields
                required_payload[field.name] = str(self.get_sample_value(field)) + " <required>"
            else:
                if update and not field.null:
                    continue  # Skip optional fields for updates unless updating
                optional_payload[field.name] = self.get_sample_value(field)

        # Combine required and optional fields with required fields listed first
        sample_payload = {**required_payload, **optional_payload}
        return sample_payload

    def is_field_required(self, field):
        """Check if the field is required (not nullable, not blank, and no default value)."""
        # Field is required if:
        # - It is not nullable (null=False)
        # - It is not blank (blank=False)
        # - It does not have a default value (default is not set)
        # - It is not auto-generated (e.g., AutoField, DateTimeField with auto_now_add)
        if field.null or field.blank or field.has_default() or field.auto_created:
            return False
        return True


    def get_sample_value(self, field):
        """Generate a sample value based on the field type."""
        field_type = type(field).__name__

        if field_type == 'CharField':
            return 'Sample Text'
        elif field_type == 'TextField':
            return 'Sample Text Body'
        elif field_type == 'IntegerField':
            return 123
        elif field_type == 'FloatField':
            return 12.34
        elif field_type == 'BooleanField':
            return True
        elif field_type == 'DateField':
            return '2023-01-01'
        elif field_type == 'DateTimeField':
            return '2023-01-01T12:00:00Z'
        elif field_type == 'TimeField':
            return '12:00:00'
        elif field_type == 'EmailField':
            return 'sample@example.com'
        elif field_type == 'URLField':
            return 'https://example.com'
        elif field_type == 'SlugField':
            return 'sample-slug'
        elif field_type == 'UUIDField':
            return '123e4567-e89b-12d3-a456-426614174000'
        elif field_type == 'JSONField':
            return json.dumps({"key": "value"})
        elif field_type == 'ImageField':
            return SimpleUploadedFile("sample_image.jpg", b"sample image content", content_type="image/jpeg")
        elif field_type == 'FileField':
            return SimpleUploadedFile("sample_file.txt", b"sample file content", content_type="text/plain")
        elif field_type == 'ForeignKey':
            return 1  # Return a sample primary key for foreign key relations
        elif field_type == 'ManyToManyField':
            return [1, 2, 3]  # Return a list of primary keys for ManyToMany fields
        elif field_type == 'DecimalField':
            return '123.45'
        elif field_type == 'BigIntegerField':
            return 1234567890
        elif field_type == 'SmallIntegerField':
            return 12
        elif field_type == 'PositiveIntegerField':
            return 10
        elif field_type == 'PositiveSmallIntegerField':
            return 5
        elif field_type == 'DurationField':
            return '01:30:00'  # Example of 1 hour, 30 minutes duration
        elif field_type == 'IPAddressField':
            return '192.168.1.1'
        elif field_type == 'BinaryField':
            return b'Sample Binary Data'
        elif field_type == 'GenericIPAddressField':
            return '2001:0db8:85a3:0000:0000:8a2e:0370:7334'  # IPv6
        elif field_type == 'AutoField':
            return None  # Usually handled automatically by Django as an auto-increment field
        elif field_type == 'BigAutoField':
            return None
        elif field_type == 'NullBooleanField':
            return None  # Deprecated, but may still be found in some cases
        elif field_type == 'ArrayField':
            return [1, 2, 3]  # Sample array, adjust based on base field type
        elif field_type == 'HStoreField':
            return {'key1': 'value1', 'key2': 'value2'}  # Sample HStore (key-value pair) data
        elif field_type == 'CITextField':
            return 'Sample Case-Insensitive Text'
        elif field_type == 'JSONField':
            return {"key": "value"}
        else:
            return 'Sample Value'  # Default for any unsupported field type
