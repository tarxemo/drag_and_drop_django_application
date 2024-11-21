from django.http import JsonResponse, HttpResponse
from django.views import View
from django.views.decorators.http import require_http_methods
from django.middleware.csrf import get_token
import json
from .models import *
from .utils import *
from .form_utils import *
from .templates_utils import *
from django.shortcuts import render, redirect, get_object_or_404
import joblib
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
from .models_utils import *
import os
import tempfile
import shutil
import subprocess
from io import BytesIO
from django.http import FileResponse, HttpResponse
from django.views import View


def template_list(request):
    templates = Template.objects.all()
    return render(request, 'template_list.html', {'templates': templates})

def add_template(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            template = Template.objects.create(name=name)
            Tag.objects.create(template=template, tag_name="div", text_content="Starting a new template")
            return redirect('template_list')
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

def template_detail(request, template_id):
    template = get_object_or_404(Template, id=template_id)
    html_structure = generate_template_by_id(template_id)
    csrf_token = get_token(request)
    return render(request, 'template_detail.html', {
        'template': template,
        'html_structure': html_structure,
        'csrf_token': csrf_token,
        'tag':Tag.objects.filter(template=template).first()
    })

@require_http_methods(["GET"])
def get_tag(request, tag_id):
    tag = get_object_or_404(Tag, id=tag_id)
    attributes = [{'name': attr.attribute_name, 'value': attr.attribute_value} for attr in tag.attributes.all()]
    classes = [cls.class_name for cls in tag.classes.all()]
    response_data = {
        'tag_name': tag.tag_name,
        'attributes': attributes,
        'classes': classes,
        'text_content': tag.text_content,
        'id': tag.id
    }
    return JsonResponse(response_data)

@require_http_methods(["POST"])
def save_tag(request, tag_id):
    tag = get_object_or_404(Tag, id=tag_id)
    data = json.loads(request.body)
    tag.tag_name = data['tag_name']
    tag.text_content = data['text_content']
    tag.position = data['position']
    tag.save()

    tag.attributes.all().delete()
    for attr in data['attributes']:
        tag.attributes.create(attribute_name=attr['name'], attribute_value=attr['value'])

    tag.classes.all().delete()
    for cls in data['classes']:
        tag.classes.create(class_name=cls)

    return JsonResponse({'status': 'success'})

@require_http_methods(["POST"])
def add_tag(request, parent_tag_id):
    parent_tag = get_object_or_404(Tag, id=parent_tag_id)
    data = json.loads(request.body)
    new_tag = Tag.objects.create(
        template=parent_tag.template,
        parent_tag=parent_tag,
        tag_name=data['tag_name'],
        text_content=data.get('text_content', ''),
        position=data.get('position', 0)
    )
    return JsonResponse({'status': 'success', 'tag_id': new_tag.id, 'tag_name': new_tag.tag_name})


def edit_tag(request, template_id):
    if request.method == "POST":
        tag_id = request.POST.get('tag_id')
        tag=Tag.objects.get(id=tag_id)
        tag.tag_name = request.POST.get('tag_name')
        tag.text_content = request.POST.get('text_content')
        tag.position = int(request.POST.get('position'))
        image = request.FILES.get('image')
        if image:
            if(Image.objects.filter(tag=tag)).exists():
                tag_image = Image.objects.get(tag=tag)
                tag_image.image = image
            else:
                tag_image = Image.objects.create(tag=tag, image=image)
            tag_image.save
        tag.save()
    tag_id = request.GET.get('tag_id')
    tag = get_object_or_404(Tag, id=tag_id)
    html_structure = generate_template_by_id(tag.template.id)
    context={
        'tag':tag,
        'template': Template.objects.get(id=template_id),
        'html_structure':html_structure
        }
    return render(request, 'edit_tag.html', context)

@require_http_methods(["POST"])
def add_attribute(request):
    tag_id = request.POST.get("tag_id")
    attribute_name = request.POST.get("attribute_name")
    attribute_value = request.POST.get("attribute_value")
    tag = get_object_or_404(Tag, id=tag_id)
    attribute, created = Attribute.objects.update_or_create(
        tag=tag,
        attribute_name=attribute_name,
        attribute_value=attribute_value
    )
    return JsonResponse({'status': 'success', 'attribute_id': attribute.id})

def add_class(request, template_id):
    if request.method == "POST":
        tag_id = request.GET.get('tag_id')
        tag = get_object_or_404(Tag, id=tag_id)
        try:
            data = json.loads(request.body.decode('utf-8'))
            class_names = data.get("class_name", [])
        except:
            class_names = request.POST.getlist("class_name")            
        html_structure = generate_template_by_id(tag.template.id)
        print(class_names)  # For debugging
        
        for class_name in class_names:
            Class.objects.create(class_name=class_name, tag=tag)
    
    tag_id = request.GET.get('tag_id')
    tag = get_object_or_404(Tag, id=tag_id)
    html_structure = generate_template_by_id(tag.template.id)
    context = {
        'tag': tag,
        'template': get_object_or_404(Template, id=template_id),
        'html_structure': html_structure
    }
    return render(request, 'add_class.html', context)


@require_http_methods(["POST"])
def delete_tag(request, tag_id):
    tag = get_object_or_404(Tag, id=tag_id)
    tag.delete()
    return JsonResponse({'status': 'success'})

@require_http_methods(["POST"])
def delete_attribute(request, tag_id, attribute_name):
    tag = get_object_or_404(Tag, id=tag_id)
    attribute = get_object_or_404(Attribute, tag=tag, attribute_name=attribute_name)
    attribute.delete()
    return JsonResponse({'status': 'success'})

@require_http_methods(["POST"])
def delete_class(request, tag_id, class_name):
    tag = get_object_or_404(Tag, id=tag_id)
    cls = get_object_or_404(Class, tag=tag, class_name=class_name)
    cls.delete()
    return JsonResponse({'status': 'success'})


file_path = 'idd/model_data.joblib'
model_data = joblib.load(file_path)

def get_predictions(input_text):
    return predict_classes(input_text, model_data['model'], model_data['vectorizer'], model_data['class_map'], decode_list)[0]

@csrf_exempt
def predict_view(request):
    if request.method == 'GET':
        input_text = request.GET.get('class_description')
        predictions = get_predictions(input_text)
        class_names = [prediction[0] for prediction in predictions]
        return JsonResponse({'predictions': class_names})


def add_child_tag(request, template_id):
    if request.method == "POST":
        tag_name = request.POST.get("tag_name")
        parent_tag_id = request.POST.get("parent_tag_id")
        template_id = request.POST.get("template_id")
        text_content = request.POST.get("text_content")
        parent_tag = Tag.objects.get(id=parent_tag_id)
        template = Template.objects.get(id = template_id)
        Tag.objects.create(
            tag_name=tag_name, 
            parent_tag=parent_tag, 
            template=template, 
            text_content=text_content
        )
    tag_id = request.GET.get('tag_id')
    tag = get_object_or_404(Tag, id=tag_id)
    html_structure = generate_template_by_id(tag.template.id)
    context = {
        'tag': tag,
        'template': get_object_or_404(Template, id=template_id),
        'html_structure': html_structure
    }
    return render(request, 'add_child_tag.html', context)

@csrf_exempt
def delete_tag(request, template_id):
    tag_id = request.GET.get('tag_id')
    tag = get_object_or_404(Tag, id=tag_id)
    tag.delete()
    url = f"/template/{template_id}/view-all-children/?tag_id={tag.parent_tag.id}"
    return redirect(url)

def view_all_children(request, template_id):
    tag_id = request.GET.get('tag_id')
    template = get_object_or_404(Template, id=template_id)
    parent_tag = get_object_or_404(Tag, id=tag_id)
    children_tags = Tag.objects.filter(parent_tag=parent_tag)
    
    return render(request, 'view_all_children.html', {
        'template': template,
        'tag': parent_tag,
        'children_tags': children_tags,
        'html_structure' : generate_template_by_id(template.id),
    })

def view_all_attributes(request, template_id):
    tag_id = request.GET.get('tag_id')
    template = get_object_or_404(Template, id=template_id)
    tag = get_object_or_404(Tag, id=tag_id)
    attributes = Attribute.objects.filter(tag=tag)
    
    return render(request, 'view_all_attributes.html', {
        'template': template,
        'tag': tag,
        'attributes': attributes,
        'html_structure' : generate_template_by_id(template.id),
    })

def view_all_classes(request, template_id):
    tag_id = request.GET.get('tag_id')
    template = get_object_or_404(Template, id=template_id)
    tag = get_object_or_404(Tag, id=tag_id)
    classes = TagClass.objects.filter(tag=tag)
    
    return render(request, 'view_all_classes.html', {
        'template': template,
        'tag': tag,
        'classes': classes,
        'html_structure' : generate_template_by_id(template.id),
    })

def edit_class(request, template_id):
    class_id = request.GET.get('class_id')
    template = get_object_or_404(Template, id=template_id)
    class_instance = get_object_or_404(TagClass, id=class_id).class_name
    tag = get_object_or_404(TagClass, id=class_id).tag

    if request.method == 'POST':
        class_name = request.POST.get('class_name')
        class_instance.class_name = class_name
        class_instance.save()
        url = f"/template/{template_id}/view-all-classes/?tag_id={tag.id}"
        return redirect(url)
    
    return render(request, 'edit_class.html', {
        'template': template,
        'tag': tag,
        'class_instance': class_instance,
        'html_structure' : generate_template_by_id(template.id),
    })

def delete_class(request, template_id):
    class_id = request.GET.get('class_id')
    template = get_object_or_404(Template, id=template_id)
    class_instance = get_object_or_404(Class, id=class_id)
    tag = class_instance.tag
    class_instance.delete()
    url = f"/template/{template_id}/view-all-classes/?tag_id={tag.id}"
    return redirect(url)


@csrf_exempt
def add_attribute(request, template_id):
    template = get_object_or_404(Template, id=template_id)
    if request.method == 'POST':
        tag_id = request.POST.get('tag_id')
        tag = get_object_or_404(Tag, id=tag_id)
        attribute_name = request.POST.get('attribute_name')
        attribute_value = request.POST.get('attribute_value')
        Attribute.objects.create(attribute_name=attribute_name, attribute_value=attribute_value, tag=tag)
        url = f"/template/{template_id}/view-all-attributes/?tag_id={tag_id}"
        return redirect(url)
    
    tag_id = request.GET.get('tag_id')
    tag = get_object_or_404(Tag, id=tag_id)
    return render(request, 'add_attribute.html', {
        'template': template,
        'tag': tag,
        'html_structure' : generate_template_by_id(template.id),
    })


@csrf_exempt
def edit_attribute(request, template_id):
    attribute_id = request.GET.get('attribute_id')
    template = get_object_or_404(Template, id=template_id)
    attribute = get_object_or_404(Attribute, id=attribute_id)

    if request.method == 'POST':
        attribute.attribute_name = request.POST.get('attribute_name')
        attribute.attribute_value = request.POST.get('attribute_value')
        attribute.save()
        url = f"/template/{template_id}/view-all-attributes/?tag_id={attribute.tag.id}"
        return redirect(url)

    return render(request, 'edit_attribute.html', {
        'template': template,
        'attribute': attribute,
        'tag': attribute.tag,
        'html_structure' : generate_template_by_id(template.id),
    })

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
        html_file = request.FILES.get('file')
        fs = FileSystemStorage()
        filename = fs.save(html_file.name, html_file)
        file_path = fs.path(filename)
        parse_and_save_html(file_path, template_name)
        return redirect('template_list')  # Redirect to a list of templates or any other view
    else:
        return render(request, 'upload_html.html')

@csrf_exempt
def change_parent_tag(request):
    if request.method == 'POST':
        dragged_tag_id = request.POST.get('dragged_tag_id')
        new_parent_tag_id = request.POST.get('new_parent_tag_id')

        try:
            dragged_tag = Tag.objects.get(id=dragged_tag_id)
            new_parent_tag = Tag.objects.get(id=new_parent_tag_id)
            dragged_tag.parent_tag = new_parent_tag
            dragged_tag.save()

            return JsonResponse({'status': 'success'})
        except Tag.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Tag not found'})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

from django.http import JsonResponse
from .models import Tag

@csrf_exempt
def add_new_tag(request):
    if request.method == 'POST':
        tag_name = request.POST.get('tag_name')
        parent_tag_id = request.POST.get('parent_tag_id')
        template_id = request.POST.get('template_id')
        print(parent_tag_id)
        print(template_id)
        print(tag_name)
        # Assuming you have a Tag model with a foreign key to a parent tag and a template
        if parent_tag_id:
            new_tag = Tag.objects.create(
                tag_name=tag_name, 
                text_content="Added content",
                parent_tag=None, 
                template=Template.objects.get(id=template_id)
                )
        else:
            new_tag = Tag.objects.create(
                tag_name=tag_name, 
                text_content="Added content",
                parent_tag=Tag.objects.get(id=parent_tag_id), 
                template=Template.objects.get(id=template_id)
                )
            
        
        return JsonResponse({'success': True, 'tag_id': new_tag.id})
    return JsonResponse({'success': False}, status=400)

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404

@csrf_exempt  # Since this is an AJAX request, exempt CSRF verification (only if necessary)
def update_parent_tag(request):
    if request.method == 'POST':
        element_id = request.POST.get('element_id')
        new_parent_id = request.POST.get('new_parent_id')
        template_id = request.POST.get('template_id')
        
        try:
            # Fetch the HtmlTag instance (the one being moved)
            tag = get_object_or_404(Tag, id=element_id, template_id=template_id)

            if new_parent_id:
                # Fetch the new parent HtmlTag instance
                new_parent = get_object_or_404(Tag, id=new_parent_id, template_id=template_id)
                tag.parent_tag = new_parent  # Update the parent tag
            else:
                tag.parent_tag = None  # No parent tag (if dropped at the root)

            tag.save()

            return JsonResponse({'status': 'success', 'message': 'Parent tag updated successfully'})
        except Tag.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Tag or parent not found'}, status=404)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


@csrf_exempt  # Only if necessary for AJAX requests
def update_tag_position(request):
    if request.method == 'POST':
        element_id = request.POST.get('element_id')
        new_position = int(request.POST.get('new_position'))
        parent_id = request.POST.get('parent_id')
        template_id = request.POST.get('template_id')

        try:
            # Fetch the tag being reordered
            tag = get_object_or_404(Tag, id=element_id, template_id=template_id)

            # Fetch all sibling tags under the same parent
            sibling_tags = Tag.objects.filter(parent_tag_id=parent_id, template_id=template_id).exclude(id=element_id)

            # Adjust the positions of the sibling tags accordingly
            if new_position < tag.position:
                # Moving up
                sibling_tags.filter(position__gte=new_position, position__lt=tag.position).update(position=models.F('position') + 1)
            else:
                # Moving down
                sibling_tags.filter(position__lte=new_position, position__gt=tag.position).update(position=models.F('position') - 1)

            # Update the position of the dragged tag
            tag.position = new_position
            tag.save()

            return JsonResponse({'status': 'success', 'message': 'Tag position updated successfully'})
        except Tag.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Tag not found'}, status=404)

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


from django.shortcuts import render, redirect, get_object_or_404
from django.template import Template as Django_template, Context as Django_context
from django.views.decorators.csrf import csrf_exempt

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
import os
import shutil
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from subprocess import run
from tempfile import NamedTemporaryFile

@csrf_exempt
def generate_django_project(request):
    if request.method == "POST":
        # Get project name and app name from the POST request
        project_name = request.POST.get('project_name')
        app_name = request.POST.get('app_name')

        if not project_name or not app_name:
            return HttpResponse("Missing project_name or app_name", status=400)

        # Step 1: Create a temporary directory with a unique name using NamedTemporaryFile
        with NamedTemporaryFile(dir=settings.MEDIA_ROOT, prefix=f"{project_name}-", delete=False) as tmpfile:
            tmp_dir = tmpfile.name

            # Step 2: Create the Django project structure within the temporary directory
            project_dir = os.path.join(tmp_dir, project_name)
            run(['django-admin', 'startproject', project_name, tmp_dir])

            # Step 3: Correct path to the inner project folder (where manage.py is)
            inner_project_dir = project_dir

            # Step 4: Create the app inside the generated project using the startapp command
            run(['python3', 'manage.py', 'startapp', app_name], cwd=inner_project_dir)

            # Step 5: Zip the entire project folder
            zip_name = f"{project_name}.zip"
            zip_path = os.path.join(tmp_dir, zip_name)

            # Use shutil to create the zip file
            shutil.make_archive(zip_path.replace('.zip', ''), 'zip', tmp_dir)

            # Step 6: Return the zip file in the response
            with open(zip_path, 'rb') as f:
                response = HttpResponse(f.read(), content_type='application/zip')
                response['Content-Disposition'] = f'attachment; filename={zip_name}'

            # Temporary file will be automatically deleted after the response is sent

            return response
    else:
        return render(request, 'project_generator_form.html')