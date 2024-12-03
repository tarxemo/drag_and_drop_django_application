from django.http import JsonResponse, HttpResponse
from django.views import View
from django.views.decorators.http import require_http_methods
from django.middleware.csrf import get_token
import json
from .models import *
from .utils import *
from utils.form_utils import *
from utils.templates_utils import *
from utils.models_utils import *
from django.shortcuts import render, redirect, get_object_or_404
import joblib
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
import os
import tempfile
import shutil
import subprocess
from io import BytesIO
from django.http import FileResponse, HttpResponse
from django.views import View



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

@require_http_methods(["POST"])
def add_attribute_json(request):
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


@csrf_exempt  # Since this is an AJAX request, exempt CSRF verification (only if necessary)
def update_parent_tag(request):
    if request.method == 'POST':
        element_id = request.POST.get('element_id')
        new_parent_id = request.POST.get('new_parent_id')
        template_id = request.POST.get('template_id')
        print(f"Element {element_id}")
        print(f"New parent {new_parent_id}")
        print(f"Template {template_id}")
        try:
            # Fetch the HtmlTag instance (the one being moved)
            tag = get_object_or_404(Tag, id=element_id, template_id=template_id)

            if new_parent_id:
                # Fetch the new parent HtmlTag instance
                new_parent = get_object_or_404(Tag, id=new_parent_id, template__id=template_id)
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

