import os
from django.conf import settings
from django.http import Http404
from django.shortcuts import get_object_or_404
from bs4 import BeautifulSoup
from .models import *
from .form_utils import *

from django.template import Template as DjangoTemplate, Context
from django.http import Http404

from django.template import Template as DjangoTemplate, Context
from django.http import Http404

def generate_template(username, table_name, action):
    template_name = f"{username}_{table_name}_{action}"
    try:
        template = get_object_or_404(Template, name=template_name)
    except Http404:
        # Generate a dynamic template if it doesn't exist in the database
        if action == "add":
            template_content = generate_add_view_html(table_name)
        elif action == "details":
            template_content = generate_detail_view_html(table_name)
        elif action == "list":
            template_content = generate_list_view_html(table_name)
        elif action == "edit":
            template_content = generate_edit_view_html(table_name)
        
        template = parse_and_save_html(template_content, template_name)

    # Build tag tree and handle Django tags
    def build_tag_tree(tag, indent_level=0):
        indent = '    ' * indent_level
        attributes = ' '.join(
            [f'{attr.attribute_name}="{attr.attribute_value}"' for attr in tag.attributes.all()] +
            [f'class="{" ".join(cls.class_name.class_name for cls in tag.tagclasses.all())}"'] +
            [f'id="{tag.id}"']
        )
        
        # Process django_tag_type to insert corresponding template tags
        if tag.django_tag_type in {'csrf_token', 'for', 'if', 'block', 'extends', 'endif', 'endblock', 'endfor'}:
            content = f'{tag.text_content}'
        else:
            content = tag.text_content or ''

        # Recursive call to include children
        children = ''.join(build_tag_tree(child, indent_level + 1) for child in tag.children.all().order_by('position'))
        content += children

        # Handle opening and closing tags, self-closing tags, and block endings
        if tag.django_tag_type in {'csrf_token', 'for', 'if', 'block', 'extends', 'endif', 'endblock', 'endfor'}:
            return f'{indent}{content}\n'
        if tag.tag_name == "img":
            return f'{indent}<{tag.tag_name} {attributes} src="{tag.image.image.url}" />\n'
        else:
            return f'{indent}<{tag.tag_name} {attributes}>{content}</{tag.tag_name}>\n'
    
    # Build the root structure from top-level tags
    root_tags = Tag.objects.filter(template=template, parent_tag__isnull=True).order_by('position')
    html_structure = ''.join(build_tag_tree(tag, 1) for tag in root_tags)

    # Complete HTML template structure
    error = "{% endif %}"
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

    return complete_html


def generate_template_by_id(template_id):
    template = get_object_or_404(Template, id=template_id)

    # Build tag tree and handle Django tags
    def build_tag_tree(tag, indent_level=0):
        indent = '    ' * indent_level
        attributes = ' '.join(
            [f'{attr.attribute_name}="{attr.attribute_value}"' for attr in tag.attributes.all()] +
            [f'class="{" ".join(cls.class_name.class_name for cls in tag.tagclasses.all())}"'] +
            [f'id="{tag.id}"']
        )
        
        # Process django_tag_type to insert corresponding template tags
        if tag.django_tag_type in {'csrf_token', 'for', 'if', 'block', 'extends', 'endif', 'endblock', 'endfor'}:
            content = f'{tag.text_content}'
        else:
            content = tag.text_content or ''

        # Recursive call to include children
        children = ''.join(build_tag_tree(child, indent_level + 1) for child in tag.children.all().order_by('position'))
        content += children

        # Handle opening and closing tags, self-closing tags, and block endings
        if tag.django_tag_type in {'csrf_token', 'for', 'if', 'block', 'extends', 'endif', 'endblock', 'endfor'}:
            return f'{indent}{content}\n'
        if tag.tag_name == "img":
            return f'{indent}<{tag.tag_name} {attributes} src="{tag.image.image.url}" />\n'
        else:
            return f'{indent}<{tag.tag_name} {attributes}>{content}</{tag.tag_name}>\n'
    
    # Build the root structure from top-level tags
    root_tags = Tag.objects.filter(template=template, parent_tag__isnull=True).order_by('position')
    html_structure = ''.join(build_tag_tree(tag, 1) for tag in root_tags)

    # Complete HTML template structure
    error = "{% endif %}"
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

    return complete_html

from django.conf import settings
from bs4 import BeautifulSoup
import re
import os
import re
from bs4 import BeautifulSoup
from django.conf import settings

def parse_and_save_html(content_data, template_name, is_file_path=False):
    if is_file_path:
        with open(content_data, 'r', encoding='utf-8') as file:
            content = file.read()
    else:
        content = content_data

    soup = BeautifulSoup(content, 'html.parser')
    application = Application.objects.first()
    template = Template.objects.create(name=template_name, application=application)

    def process_django_tag(tag_content, parent=None):
        """
        Helper function to handle Django-specific template tags.
        This function detects both opening and closing Django tags.
        """
        # Capture the opening tag (e.g., "for", "if") or closing tag (e.g., "endfor", "endif")
        tag_type_match = re.match(r'{%\s*(end)?(\w+)', tag_content)
        if tag_type_match:
            is_closing = tag_type_match.group(1) is not None
            tag_type = tag_type_match.group(2)
            if is_closing:
                tag_type = f"end{tag_type}"

        tag = Tag.objects.create(
            template=template,
            parent_tag=parent,
            tag_name='django_tag',
            text_content=tag_content,
            django_tag_type=tag_type,
            position=len(parent.children.all()) if parent else len(Tag.objects.filter(template=template, parent_tag=None))
        )
        return tag

    def create_tag(soup_tag, parent=None):
        if hasattr(soup_tag, 'name'):
            tag_name = soup_tag.name
            text_content = soup_tag.string if soup_tag.string else ''
            position = len(parent.children.all()) if parent else len(Tag.objects.filter(template=template, parent_tag=None))
            
            tag = Tag.objects.create(
                template=template,
                parent_tag=parent,
                tag_name=tag_name,
                text_content=text_content,
                position=position
            )

            for attr, value in soup_tag.attrs.items():
                if attr == 'class':
                    class_names = value if isinstance(value, list) else value.split()
                    for class_name in class_names:
                        # Create or retrieve the Class instance
                        class_obj, created = Class.objects.get_or_create(class_name=class_name)
                        # Create the relationship through TagClass
                        TagClass.objects.create(tag=tag, class_name=class_obj)
                elif attr == 'id':
                    Attribute.objects.create(tag=tag, attribute_name='id', attribute_value=value)
                else:
                    Attribute.objects.create(tag=tag, attribute_name=attr, attribute_value=value)
            
            if tag_name == 'img' and 'src' in soup_tag.attrs:
                img_path = soup_tag['src']
                if img_path.startswith('images/'):
                    img_file = img_path.split('/')[-1]
                    img_full_path = os.path.join(settings.MEDIA_ROOT, 'images', img_file)
                    with open(img_full_path, 'rb') as img_f:
                        image = Image.objects.create(tag=tag)
                        image.image.save(img_file, img_f)

            for child in soup_tag.children:
                if child.name:
                    create_tag(child, tag)
                elif isinstance(child, str):
                    django_tags = re.findall(r'{%.*?%}|{#.*?#}', child)
                    for django_tag in django_tags:
                        process_django_tag(django_tag, tag)
        else:
            django_tags = re.findall(r'{%.*?%}|{#.*?#}', str(soup_tag))
            for django_tag in django_tags:
                process_django_tag(django_tag, parent)

    for child in soup.children:
        if child.name:
            create_tag(child)
        elif isinstance(child, str):
            django_tags = re.findall(r'{%.*?%}|{#.*?#}', child)
            for django_tag in django_tags:
                process_django_tag(django_tag)

    return template
