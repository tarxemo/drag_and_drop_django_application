import os
import subprocess
import tempfile
import zipfile
from io import BytesIO
from django.utils.text import slugify
from django.http import HttpResponse
from django.conf import settings
from TB.utils import *
from authApp.models import DynamicModelLog
from idd.models import *


# Function to add content to views.py
def add_views_content(app_dir, models, user):
    views_path = os.path.join(app_dir, "views.py")
    with open(views_path, "a") as views_file:
        for model in models:
            model_name = model.model_name

            # Generate CRUD view functions
            list_view = generate_table_list_view_code(model_name, user)
            create_view = generate_table_create_view_code(model_name, user)
            detail_view = generate_table_detail_view_code(model_name, user)
            update_view = generate_table_update_view_code(model_name, user)
            delete_view = generate_table_delete_view_code(model_name, user)

            # Write the generated view functions to views.py
            views_file.write("\n\n" + list_view)
            views_file.write("\n\n" + create_view)
            views_file.write("\n\n" + detail_view)
            views_file.write("\n\n" + update_view)
            views_file.write("\n\n" + delete_view)


# Function to add content to urls.py
def add_urls_content(app_dir, models):
    urls_path = os.path.join(app_dir, "urls.py")
    with open(urls_path, "w") as urls_file:
        # Write the initial imports and urlpatterns declaration
        urls_file.write("from django.urls import path\n")
        urls_file.write("from . import views\n\n")
        urls_file.write("urlpatterns = [\n")

        for model in models:
            model_name = model.model_name.lower()

            # Add URL patterns for each view
            urls_file.write(
                f"    path('{model_name}/list/', views.{model_name}_list, name='{model_name}_list'),\n"
            )
            urls_file.write(
                f"    path('{model_name}/create/', views.{model_name}_create, name='{model_name}_create'),\n"
            )
            urls_file.write(
                f"    path('{model_name}/<int:id>/', views.{model_name}_detail, name='{model_name}_detail'),\n"
            )
            urls_file.write(
                f"    path('{model_name}/<int:id>/update/', views.{model_name}_update, name='{model_name}_update'),\n"
            )
            urls_file.write(
                f"    path('{model_name}/<int:id>/delete/', views.{model_name}_delete, name='{model_name}_delete'),\n"
            )

        urls_file.write("]\n")


# Function to add content to models.py
def add_models_content(app_dir, models):
    models_path = os.path.join(app_dir, "models.py")
    with open(models_path, "a") as models_file:
        for model in models:
            # Generate model definition based on the model_name (customize as needed)
            model_definition = f"""
class {model.model_name}(models.Model):
    # Add your fields here
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
"""
            models_file.write(model_definition)


# Main function to create Django project
def create_django_project(request, project_name="my_project", app_name="new_app"):
    user = request.user  # Get the current user

    # Use a temporary directory for the project folder
    with tempfile.TemporaryDirectory() as project_dir:
        # Create Django project using subprocess
        subprocess.run(
            ["django-admin", "startproject", project_name, project_dir],
            check=True,
        )

        # Path to the newly created project directory
        created_project_dir = os.path.join(project_dir, project_name)

        # Navigate to the project directory and create the app
        subprocess.run(
            ["python3", "manage.py", "startapp", app_name],
            cwd=project_dir,
            check=True,
        )

        # Path to the app directory
        app_dir = os.path.join(project_dir, app_name)

        # Ensure the app is added to INSTALLED_APPS in settings.py
        settings_path = os.path.join(created_project_dir, "settings.py")
        with open(settings_path, "a") as settings_file:
            settings_file.write(f"\nINSTALLED_APPS.append('{app_name}')\n")

        # Create templates directory for the app
        templates_dir = os.path.join(app_dir, "templates", app_name)
        os.makedirs(templates_dir, exist_ok=True)

        # Generate templates for the app
        templates = Template.objects.all()
        for template in templates:
            template_html = generate_template_by_id(template.id)
            template_path = os.path.join(templates_dir, f"{template.name}.html")
            with open(template_path, "w") as file:
                file.write(template_html)

        # Retrieve all models from DynamicModelLog
        models = DynamicModelLog.objects.filter(user=user)

        # Add content to views.py, urls.py, and models.py
        add_views_content(app_dir, models, user)
        add_urls_content(app_dir, models)
        # add_models_content(app_dir, models)

        # Zip the project folder
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for root, dirs, files in os.walk(project_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    zip_file.write(file_path, os.path.relpath(file_path, project_dir))

        # Finalize the ZIP file
        zip_buffer.seek(0)

        # Serve the ZIP file as a download
        response = HttpResponse(zip_buffer, content_type="application/zip")
        response["Content-Disposition"] = f'attachment; filename="{project_name}.zip"'

        # The temporary directory and its contents are automatically cleaned up here
        return response




def list_view(request):
    generate_table_list_view_code('Tag', request.user)