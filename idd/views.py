from django.http import JsonResponse, HttpResponse
from django.middleware.csrf import get_token
import json
from .models import *
from TB.utils import *
from django.shortcuts import render, redirect, get_object_or_404
import joblib
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
from django.template import Template as Django_template, Context as Django_context
from django.contrib import messages
from .forms import *
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Template, Like
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count

def homepage(request):
    if request.user.is_authenticated:
        user = request.user  
        context = {
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
        }
    else:
        context = {
            'error': 'User is not authenticated.',
        }
    
    return render(request, 'homepage.html', context)

def project_register(request):
    if request.method == "POST":
        
        title = request.POST.get('title')
        description = request.POST.get('description')
        start_date = request.POST.get('start_date')
        expected_completion_date = request.POST.get('expected_completion_date')
        status = request.POST.get('status')
        priority = request.POST.get('priority')
        category = request.POST.get('category')

        
        if not title or not description:
            return HttpResponse("Title and Description are required.", status=400)

        
        project = Project(
            title=title,
            description=description,
            start_date=start_date,
            expected_completion_date=expected_completion_date,
            status=status,
            priority=priority,
            category=category,
            owner=request.user  
        )
        project.save()
        return redirect('my_projects_list')

    return render(request, 'projects_list.html')


def details_for_project(request, project_id):
    project = get_object_or_404(Project, id=project_id, owner=request.user)
    
    
    return render(request, 'edit_Project.html', {'project': project})

def update_project_details(request,project_id):
     if request.method == "POST":
        project = get_object_or_404(Project, id=project_id, owner=request.user)
        title = request.POST.get('title')
        description = request.POST.get('description')
        start_date = request.POST.get('start_date')
        expected_completion_date = request.POST.get('expected_completion_date')
        status = request.POST.get('status')
        priority = request.POST.get('priority')
        category = request.POST.get('category')

        # Perform basic validation (example: check if required fields are filled)
        if not title or not description:
            return HttpResponse("Title and Description are required.", status=400)

        # Update the project instance with new data
        project.title = title
        project.description = description
        project.start_date = start_date
        project.expected_completion_date = expected_completion_date
        project.status = status
        project.priority = priority
        project.category = category
        project.save()

        return redirect('my_projects_list')
     return render(request, 'edit_Project.html', {'project': project})
 

def project_list(request):
    projects = Project.objects.filter(owner=request.user)  

    # Pass the projects to the template for rendering
    return render(request, 'projects_list.html', {'projects': projects})



    
def delete_project(request, project_id):
   
    project = get_object_or_404(Project, id=project_id, owner=request.user)
    
    if request.method == "POST":
        project.delete()  
        return redirect('my_projects_list')  
    
    return render(request, 'delete_project.html', {'project': project})

  
  
def project_details(request, projectId):
    detail = get_object_or_404(Project, id=projectId)
      
    return render(request,"details.html", {'detail': detail})


def register_app(request):
    
    if request.method == "POST":
        app_name = request.POST.get("app_name")
        description = request.POST.get("description")
        project_id = request.POST.get("project")  
        
        
        if not app_name or not project_id:
            messages.error(request, "Please fill in all required fields.")
            return redirect("registerApp")  
        
        project = get_object_or_404(Project, id=project_id)
        
        with transaction.atomic():
            new_app = Application.objects.create(
                name=app_name,
                description=description,
                owner=request.user  
            )
            project.applications.add(new_app)
        
        messages.success(request, "Application registered successfully!")
        return redirect("apps_list")  
    
    projects = Project.objects.filter(owner=request.user)  
    return render(request, "app_register.html", {"projects": projects})
    
    
    
def project_apps_list(request):
    projects=Project.objects.filter(owner=request.user)
    return render(request,"apps_list.html", {"projects":projects})
    
    
def template_list(request):
    parent_id = request.GET.get('parent_id')
    if parent_id != None:
        templates = Template.objects.filter(application__id = parent_id) 
    else:
        templates = Template.objects.all()   
        
    category_names = [display for value, display in Template.CATEGORY_CHOICES]
    applications = Application.objects.filter(owner=request.user)
    return render(request, 'template_list.html', {'templates': templates , 'categories': category_names, 'applications':applications })

def add_template(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        category = request.POST.get('category')
        app_id = request.POST.get('app_id')
        application = Application.objects.get(id=app_id)
        if name and category:
            template = Template.objects.create(name=name , category=category, application=application, owner=request.user)
            Tag.objects.create(template=template, tag_name="div", text_content="Starting a new template")
            return redirect('template_list')
    applications = Application.objects.filter(owner=request.user)
    return render(request, 'add_template.html')


def download_html(request, template_id):
    zip_path = create_zipped_template(template_id)
    with open(zip_path, 'rb') as f:
        response = HttpResponse(f.read(), content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="template_{template_id}.zip"'
    return response

def delete_template(request, template_id):
    template = get_object_or_404(Template, id=template_id)
    if request.method == 'POST':
        template.delete()
        return redirect('template_list')
    return render(request, 'confirm_delete.html', {'template': template})


# Utility function for rendering templates
def render_with_context(request, template_name, context=None, additional_data=None):
    if context is None:
        context = {}
    if additional_data:
        context.update(additional_data)
    return render(request, template_name, context)

# Fetch common data utility
def get_common_data(template_id, tag_id=None):
    template = get_object_or_404(Template, id=template_id)
    tag = get_object_or_404(Tag, id=tag_id) if tag_id else None
    html_structure = generate_template_by_id(template_id)
    return {
        'template': template,
        'tag': tag,
        'html_structure': html_structure
    }

# Refactored Views
def template_detail(request, template_id):
    data = get_common_data(template_id)
    data['csrf_token'] = get_token(request)
    data['tag'] = Tag.objects.filter(template=data['template']).first()
    return render_with_context(request, 'template_detail.html', data)

@csrf_exempt
def edit_tag(request, template_id):
    if request.method == "POST":
        tag = get_object_or_404(Tag, id=request.POST.get('tag_id'))
        tag.tag_name = request.POST.get('tag_name')
        tag.text_content = request.POST.get('text_content')
        tag.position = int(request.POST.get('position'))
        
        image = request.FILES.get('image')
        if image:
            tag_image, created = Image.objects.get_or_create(tag=tag)
            tag_image.image = image
            tag_image.save()
        tag.save()
    
    data = get_common_data(template_id, request.GET.get('tag_id'))
    return render_with_context(request, 'edit_tag.html', data)

@csrf_exempt
def add_class(request, template_id):
    if request.method == "POST":
        tag = get_object_or_404(Tag, id=request.GET.get('tag_id'))
        class_names = request.POST.getlist("class_name") or json.loads(request.body.decode('utf-8')).get("class_name", [])
        
        for class_name in class_names:
            class_named, created = Class.objects.get_or_create(class_name=class_name)
            TagClass.objects.create(tag=tag, class_name=class_named)
    
    data = get_common_data(template_id, request.GET.get('tag_id'))
    return render_with_context(request, 'add_class.html', data)

@csrf_exempt
def add_attribute(request, template_id):
    if request.method == 'POST':
        tag = get_object_or_404(Tag, id=request.POST.get('tag_id'))
        Attribute.objects.create(
            tag=tag,
            attribute_name=request.POST.get('attribute_name'),
            attribute_value=request.POST.get('attribute_value')
        )
        return redirect(f"/template/{template_id}/view-all-attributes/?tag_id={tag.id}")
    
    data = get_common_data(template_id, request.GET.get('tag_id'))
    return render_with_context(request, 'add_attribute.html', data)

def view_all_attributes(request, template_id):
    data = get_common_data(template_id, request.GET.get('tag_id'))
    data['attributes'] = Attribute.objects.filter(tag=data['tag'])
    return render_with_context(request, 'view_all_attributes.html', data)

def view_all_classes(request, template_id):
    data = get_common_data(template_id, request.GET.get('tag_id'))
    data['classes'] = TagClass.objects.filter(tag=data['tag'])
    return render_with_context(request, 'view_all_classes.html', data)

@csrf_exempt
def edit_class(request, template_id):
    class_instance = get_object_or_404(TagClass, id=request.GET.get('class_id'))
    if request.method == 'POST':
        class_instance.class_name = request.POST.get('class_name')
        class_instance.save()
        return redirect(f"/template/{template_id}/view-all-classes/?tag_id={class_instance.tag.id}")
    
    data = get_common_data(template_id, class_instance.tag.id)
    data['class_instance'] = class_instance
    return render_with_context(request, 'edit_class.html', data)


@csrf_exempt
def add_child_tag(request, template_id):
    """
    Adds a child tag under a specified parent tag.
    """
    if request.method == "POST":
        parent_tag_id = request.POST.get("parent_tag_id")
        template = get_object_or_404(Template, id=template_id)
        parent_tag = get_object_or_404(Tag, id=parent_tag_id)

        tag = Tag.objects.create(
            template=template,
            parent_tag=parent_tag,
            tag_name=request.POST.get("tag_name"),
            text_content=request.POST.get("text_content"),
            position=len(parent_tag.children.all())
        )

    data = get_common_data(template_id, request.GET.get('tag_id'))
    return render_with_context(request, 'add_child_tag.html', data)


@csrf_exempt
def edit_attribute(request, template_id):
    """
    Edits an attribute of a tag.
    """
    attribute_id = request.GET.get('attribute_id')
    attribute = get_object_or_404(Attribute, id=attribute_id)

    if request.method == 'POST':
        attribute.attribute_name = request.POST.get('attribute_name')
        attribute.attribute_value = request.POST.get('attribute_value')
        attribute.save()
        return redirect(f"/template/{template_id}/view-all-attributes/?tag_id={attribute.tag.id}")

    data = get_common_data(template_id, attribute.tag.id)
    data.update({
        'attribute': attribute
    })
    return render_with_context(request, 'edit_attribute.html', data)


def view_all_children(request, template_id):
    tag_id = request.GET.get('tag_id')
    parent_tag = get_object_or_404(Tag, id=tag_id)
    children_tags = Tag.objects.filter(parent_tag=parent_tag)

    data = get_common_data(template_id, tag_id)
    data.update({
        'children_tags': children_tags
    })
    return render_with_context(request, 'view_all_children.html', data)

def view_all_siblings(request, template_id):
    """
    Lists all sibling tags of a given tag.
    """
    tag_id = request.GET.get('tag_id')
    current_tag = get_object_or_404(Tag, id=tag_id)

    if current_tag.parent_tag:
        siblings = Tag.objects.filter(
            parent_tag=current_tag.parent_tag
        ).exclude(id=current_tag.id)
    else:
        # If the tag has no parent, its siblings are tags with no parent in the same template.
        siblings = Tag.objects.filter(
            parent_tag=None,
            template=current_tag.template
        ).exclude(id=current_tag.id)

    data = get_common_data(template_id, tag_id)
    data.update({
        'current_tag': current_tag,
        'siblings': siblings
    })
    return render_with_context(request, 'view_all_siblings.html', data)

@csrf_exempt
def delete_tag(request, template_id):
    tag = get_object_or_404(Tag, id=request.GET.get('tag_id'))
    tag.delete()
    return redirect(f"/template/{template_id}/view-all-children/?tag_id={tag.parent_tag.id}")

@csrf_exempt
def delete_attribute(request, template_id):
    attribute_id = request.GET.get('attribute_id')
    template = get_object_or_404(Template, id=template_id)
    attribute = get_object_or_404(Attribute, id=attribute_id)
    tag_id = attribute.tag.id
    attribute.delete()
    url = f"/template/{template_id}/view-all-attributes/?tag_id={tag_id}"
    return redirect(url)

def upload_html(request):
    if request.method == 'POST':
        template_name = request.POST.get("template_name")
        category =request.POST.get("category")
        app_id=request.POST.get("app_id")
        application = Application.objects.get(id=app_id)
        html_file = request.FILES.get('file')
        fs = FileSystemStorage()
        filename = fs.save(html_file.name, html_file)
        file_path = fs.path(filename)
        parse_and_save_html(file_path, template_name, app_id, category, is_file_path=True)
        return redirect('template_list') 
    else:
        return render(request, 'upload_html.html')

def render_dynamic_template(request, table_name, view_type, context_data=None):
    """
    Helper function to generate and render templates dynamically.
    """
    context_data = context_data or {}
    template_html = generate_template(request.user.username, table_name, view_type)
    template = Django_template(template_html)
    template_context = Django_context(context_data)
    rendered_html = template.render(template_context)
    print(rendered_html)
    context = {
        'content': rendered_html,
        'table_name': table_name,
    }
    return context

def list_view(request, table_name):
    model, _ = DynamicModelHelper.get_model_and_serializer(table_name)
    queryset = model.objects.all()
    
    context = render_dynamic_template(request, table_name, "list", {
        f'{table_name.lower()}s': queryset
    })
    return render(request, 'idd/templates/template.html', context)

def detail_view(request, table_name, pk):
    model, _ = DynamicModelHelper.get_model_and_serializer(table_name)
    instance = get_object_or_404(model, pk=pk)
    
    context = render_dynamic_template(request, table_name, "details", {
        f'{table_name.lower()}': instance
    })
    return render(request, 'idd/templates/template.html', context)

@csrf_exempt
def create_view(request, table_name):
    if request.method == 'POST':
        model, _ = DynamicModelHelper.get_model_and_serializer(table_name)
        data = {key: value for key, value in request.POST.items()}
        instance = model(**data)
        instance.owner = request.user
        instance.save()
        return redirect('list_view', table_name=table_name)
    context = render_dynamic_template(request, table_name, "add")
    return render(request, 'idd/templates/template.html', context)

@csrf_exempt
def edit_view(request, table_name, pk):
    model, _ = DynamicModelHelper.get_model_and_serializer(table_name)
    instance = get_object_or_404(model, pk=pk)
    if request.method == 'POST':
        for attr, value in request.POST.items():
            # if attr != 'id':
                setattr(instance, attr, value)
        instance.save()
        return redirect('detail_view', table_name=table_name, pk=pk)
    
    context = render_dynamic_template(request, table_name, "edit", {
        f'{table_name.lower()}': instance
    })
    return render(request, 'idd/templates/template.html', context)

def delete_view(request, table_name, pk):
    model, _ = DynamicModelHelper.get_model_and_serializer(table_name)
    instance = get_object_or_404(model, pk=pk)

    if request.method == 'POST':
        instance.delete()
        return redirect('list_view', table_name=table_name)
    
    context = render_dynamic_template(request, table_name, "confirm_delete", {
        f'{table_name.lower()}': instance
    })
    return render(request, 'idd/templates/template.html', context)

from django.db.models import Count, Exists, OuterRef
from django.shortcuts import render, redirect

def templates_gallery(request):
    user = request.user  # Get the current logged-in user

    # Annotate templates with like count and a boolean for whether the user liked the template
    templates = Template.objects.annotate(
        like_count=Count('likes'),
        user_liked=Exists(
            Like.objects.filter(template=OuterRef('pk'), user=user)
        )
    )

    parent_id = request.GET.get('parent_id')
    destination_id = request.GET.get('destination_id')
    source_id = request.GET.get('source_id')
    if source_id is not None and destination_id is not None:
        print("**************************************")
        copy_template(source_id, destination_id)
        return redirect("template_detail", destination_id)

    templates_with_html = [
        {
            'id': template.id,
            'name': template.name,
            'like_count': template.like_count,
            'user_liked': template.user_liked,
            'html': generate_template_by_id(template.id),
        }
        for template in templates
    ]

    return render(request, 'templates_gallery.html', {'templates': templates_with_html})

 

@login_required
@csrf_exempt
def like_template(request, template_id):
    if request.method == 'POST':
        try:
            template = get_object_or_404(Template, id=template_id)
            user = request.user

            # Check if the user has already liked the template
            liked = Like.objects.filter(user=user, template=template)
            if liked.exists():
                # If liked already, unlike it by deleting the like entry
                liked.delete()
                action = 'unliked'  # Set action to 'unliked'
            else:
                # If not liked, create a new like entry
                Like.objects.create(user=user, template=template)
                action = 'liked'  # Set action to 'liked'

            # Get the updated like count
            like_count = template.likes.count()

            # Return the action and the updated like count
            return JsonResponse({
                'status': action,
                'like_count': like_count
            })
        except Exception as e:
            # Return an error message in case of exception
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    # Return an error message if the request method is not POST
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)
def one_template_detail(request, template_id):
    template = get_object_or_404(Template, id=template_id)
    html_code = generate_template_by_id(template_id)
    return render(request, 'one_template_detail.html', {'template': template, 'html_code': html_code})


#edit app_list
def edit_application(request, app_id):
    application = get_object_or_404(Application, id=app_id)
    projects = Project.objects.all()
    
    if request.method == 'POST':
        # Get the selected project and other form data
        project_id = request.POST['project']  # Get selected project ID
        app_name = request.POST['app_name']
        description = request.POST.get('description', "")

        # Get the project object by ID
        project = Project.objects.get(id=project_id)

        # Update the application fields
        application.name = app_name
        application.description = description
        application.project = project  # Update the project
        application.save()

        # Redirect to the app list page after updating
        return redirect('apps_list')  # Assuming 'app_list' is the correct URL name

    return render(request, 'edit_application.html', {
        'application': application,
        'projects': projects
    })