from django.urls import path
from .views import *
from .ajaxViews import *

urlpatterns = [
    path('homepage/', homepage , name='home'),
    path('', template_list, name='template_list'),
    path('add/', add_template, name='add_template'),
    path('delete/<int:template_id>/', delete_template, name='delete_template'),
    path('template/<int:template_id>/', template_detail, name='template_detail'),
    path('get_tag/<int:tag_id>/', get_tag, name='get_tag'),
    path('save-tag/<int:tag_id>/', save_tag, name='save_tag'),
    path('add-tag/<int:parent_tag_id>/', add_tag, name='add_tag'),
    path('save-attribute/', add_attribute, name='add_attribute'),
    path('add-class/<int:tag_id>/', add_class, name='add_class'),
    path('delete-attribute/<int:tag_id>/<str:attribute_name>/', delete_attribute, name='delete_attribute'),
    path('delete-class/<int:tag_id>/<str:class_name>/', delete_class, name='delete_class'),
    path('template/<int:template_id>/download/', download_html, name='download_html'),
    path('predict/', predict_view, name='predict'),
    path('template/<int:template_id>/edit/', edit_tag, name='edit_tag'),
    path('template/<int:template_id>/add-class/', add_class, name='add_class'),
    path('template/<int:template_id>/add-attribute/', add_attribute, name='add_attribute'),
    path('template/<int:template_id>/add-child-tag/', add_child_tag, name='add_child_tag'),
    path('template/<int:template_id>/view-all-children/', view_all_children, name='view_all_children'),
    path('template/<int:template_id>/view-all-siblings/', view_all_siblings, name='view_all_siblings'),
    path('template/<int:template_id>/view-all-classes/', view_all_classes, name='view_all_classes'),
    path('template/<int:template_id>/view-all-attributes/', view_all_attributes, name='view_all_attributes'),
    path('template/<int:template_id>/edit_class/', edit_class, name='edit_class'),
    path('template/<int:template_id>/delete_class/', delete_class, name='delete_class'),
    path('template/<int:template_id>/add_attribute/', add_attribute, name='add_attribute'),
    path('template/<int:template_id>/edit_attribute/', edit_attribute, name='edit_attribute'),
    path('template/<int:template_id>/delete_attribute/', delete_attribute, name='delete_attribute'),
    path('template/<int:template_id>/delete_tag/', delete_tag, name='delete_tag'),
    path('upload_html/', upload_html, name='upload_html'),
    
    path('predict/', predict_view, name="predict"),
    
    path('change_parent_tag/', change_parent_tag, name='save_tag_position'),
    path('add_new_tag/', add_new_tag, name="add_new_tag"),
    path('update_parent_tag/', update_parent_tag, name='update_parent_tag'),
    path('update_positions/', update_tag_position, name='update_positions'),
    path('crud/<str:table_name>/', list_view, name='list_view'),  # List all records for the specified table
    path('crud/<str:table_name>/<int:pk>/', detail_view, name='detail_view'),  # View a specific record
    path('crud/<str:table_name>/create/', create_view, name='create_view'),  # Create a new record
    path('crud/<str:table_name>/<int:pk>/edit/', edit_view, name='edit_view'),  # Edit an existing record
    path('crud/<str:table_name>/<int:pk>/delete/', delete_view, name='delete_view'),
    
<<<<<<< HEAD
    path('generate-project/', generate_django_project, name='generate_project'),
    path('projects_listing/', project_list, name='my_projects_list'),
    path('projects_listing/register', project_register, name='register_project'),
    path('projects_listing/edit/<int:project_id>/', details_for_project, name='edit_project'), 
    path('projects_listing/delete/<int:project_id>/', delete_project, name='project_deletion'),    
=======
>>>>>>> origin/dev
    path('templates/', templates_gallery, name='templates_gallery'),
    path('templates/<int:template_id>/', one_template_detail, name='one_template_detail'),
    
]
