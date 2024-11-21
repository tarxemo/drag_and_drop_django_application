from django.shortcuts import get_object_or_404
from .models import *
from bs4 import BeautifulSoup
import numpy as np
import re
import os
import zipfile
import shutil
from django.conf import settings
from django.core.files.storage import default_storage

download = False

def create_zipped_template(template_id):
    html_content = generate_download_template(template_id)
    template = get_object_or_404(Template, id=template_id)
    temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp', f'template_{template_id}')
    images_dir = os.path.join(temp_dir, 'images')
    os.makedirs(images_dir, exist_ok=True)

    # Collect images and copy them to the images directory
    for tag in Tag.objects.filter(template=template):
        try:
            if tag.tag_name == 'img' and tag.image:
                src_path = tag.image.image.path
                dst_path = os.path.join(images_dir, os.path.basename(tag.image.image.name))
                shutil.copy2(src_path, dst_path)
        except:
            pass
    
    # Save HTML content to a file
    html_path = os.path.join(temp_dir, 'template.html')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    # Create a zip file
    zip_path = os.path.join(settings.MEDIA_ROOT, f'template_{template_id}.zip')
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        # Add HTML file to the zip
        zipf.write(html_path, os.path.relpath(html_path, temp_dir))
        # Add images to the zip
        for root, _, files in os.walk(images_dir):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, temp_dir))
    
    return zip_path

# def generate_template(template_id):
#     template = get_object_or_404(Template, id=template_id)

#     def build_tag_tree(tag, indent_level=0):
#         indent = '    ' * indent_level
#         inner_indent = '    ' * (indent_level + 1)
#         attributes = ' '.join(
#             [f'{attr.attribute_name}="{attr.attribute_value}"' for attr in tag.attributes.all()] + 
#             [f'class="{" ".join(cls.class_name for cls in tag.tageds.all())}"'] +
#             [f'id="{tag.id}"']
#         )
#         children = ''.join(build_tag_tree(child, indent_level + 1) for child in tag.children.all().order_by('position'))
#         content = (tag.text_content or '') + children
        
#         if content.strip():  # if there is content or children
#             if len(content) < 50 and not '\n' in content:  # Short content and no children tags
#                 return f'{indent}<{tag.tag_name} {attributes}>{content}</{tag.tag_name}>\n'
#             else:
#                 return f'{indent}<{tag.tag_name} {attributes}>\n{inner_indent}{content}\n{indent}</{tag.tag_name}>\n'
#         else:
#             if(tag.tag_name == "img"):
#                 try:
#                     return f'{indent}<{tag.tag_name} {attributes} src="{tag.image.image.url}" />\n'
#                 except:
#                     return f'{indent}<{tag.tag_name} {attributes} />\n'
#             return f'{indent}<{tag.tag_name} {attributes} />\n'

#     root_tags = Tag.objects.filter(template=template, parent_tag__isnull=True).order_by('position')
#     html_structure = ''.join(build_tag_tree(tag, 1) for tag in root_tags)

#     complete_html = f"""
#     <!DOCTYPE html>
#     <html lang="en">
#     <head>
#         <meta charset="UTF-8">
#         <meta name="viewport" content="width=device-width, initial-scale=1.0">
#         <title>{template.name}</title>
#          <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.0.0/dist/tailwind.min.css" rel="stylesheet">
#          <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css" rel="stylesheet">
#     </head>
#     <body>
#         <div class="container mx-auto" id="-1">
#     {html_structure}
#         </div>
#     </body>
#     </html>
#     """

#     # Parse the HTML using BeautifulSoup and then prettify it
#     soup = BeautifulSoup(complete_html, 'html5lib')
#     prettified_html = soup.prettify()
#     # print(prettified_html)
#     return prettified_html



def increment_positions(parent_tag, start_position):
    """
    Increment positions of all tags with the given parent_tag starting from start_position.
    """
    children = Tag.objects.filter(parent_tag=parent_tag, position__gte=start_position).order_by('position')
    for child in children:
        child.position += 1
        child.save()

def set_position(tag, new_position):
    """
    Set the position of a tag, handling conflicts by incrementing positions of other tags if necessary.
    """
    while Tag.objects.filter(parent_tag=tag.parent_tag, position=new_position).exists():
        increment_positions(tag.parent_tag, new_position)
    tag.position = new_position
    tag.save()

def decode_list(encoded_data, class_map):
    if isinstance(encoded_data[0], np.ndarray):
        encoded_data = [tuple(x)[0] for x in encoded_data]
    reverse_map = {v: k for k, v in class_map.items()}
    decoded_data = [reverse_map[x] for x in encoded_data]
    return decoded_data

def preprocess_text(text):
    remove_words = ['set', 'the', 'a', 'and', 'or', 'with', 'to', 'of', 'in', 'for', 'on', 'from', 'is', 'are', 'be']
    text = text.lower()
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'[-]', ' ', text)
    text_tokens = text.split()
    filtered_tokens = [word for word in text_tokens if word not in remove_words]
    text = ' '.join(filtered_tokens)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def predict_classes(input_text, model, vectorizer, class_map, decode_list):
    input_text = preprocess_text(input_text)
    predict = vectorizer.transform([input_text])
    predicted_probabilities = model.predict_proba(predict)
    top_indices = np.argsort(predicted_probabilities, axis=1)[:, ::-1][:, :10]
    top_probabilities = np.take_along_axis(predicted_probabilities, top_indices, axis=1)
    top_classes = model.classes_[top_indices]

    decoded_predictions = [decode_list(classes, class_map) for classes in top_classes]
    top_predictions = []
    for i in range(predicted_probabilities.shape[0]):
        top_predictions.append([(decoded_predictions[i][j], top_probabilities[i, j]) for j in range(10)])

    return top_predictions

def generate_download_template(template_id):
    template = get_object_or_404(Template, id=template_id)

    def build_tag_tree(tag, indent_level=0):
        indent = '    ' * indent_level
        inner_indent = '    ' * (indent_level + 1)
        attributes = ' '.join(
            [f'{attr.attribute_name}="{attr.attribute_value}"' for attr in tag.attributes.all()] + 
            [f'class="{" ".join(cls.class_name for cls in tag.tageds.all())}"']
        )
        children = ''.join(build_tag_tree(child, indent_level + 1) for child in tag.children.all().order_by('position'))
        content = (tag.text_content or '') + children
        
        if content.strip():  # if there is content or children
            if len(content) < 50 and not '\n' in content:  # Short content and no children tags
                return f'{indent}<{tag.tag_name} {attributes}>{content}</{tag.tag_name}>\n'
            else:
                return f'{indent}<{tag.tag_name} {attributes}>\n{inner_indent}{content}\n{indent}</{tag.tag_name}>\n'
        else:
            if(tag.tag_name == "img"):
                try:
                    return f'{indent}<{tag.tag_name} {attributes} src="{tag.image.image.name}" />\n'
                except:
                    return f'{indent}<{tag.tag_name} {attributes} />\n'
            return f'{indent}<{tag.tag_name} {attributes} />\n'

    root_tags = Tag.objects.filter(template=template, parent_tag__isnull=True).order_by('position')
    html_structure = ''.join(build_tag_tree(tag, 1) for tag in root_tags)

    complete_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{template.name}</title>
         <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.0.0/dist/tailwind.min.css" rel="stylesheet">
         <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mx-auto" id="-1">
    {html_structure}
        </div>
    </body>
    </html>
    """

    # Parse the HTML using BeautifulSoup and then prettify it
    soup = BeautifulSoup(complete_html, 'html5lib')
    prettified_html = soup.prettify()
    # print(prettified_html)
    return prettified_html

