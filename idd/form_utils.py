from django.apps import apps
from django.utils.html import escape
from django.shortcuts import get_object_or_404
from django.apps import apps

def get_model_class(table_name):
    # Iterate over all registered apps
    for app_config in apps.get_app_configs():
        try:
            model_class = apps.get_model(app_config.label, table_name)
            if model_class:
                return model_class
        except LookupError:
            # If the model is not in this app, continue
            continue
    # If not found, raise an error or return None
    raise LookupError(f"Model '{table_name}' not found in any registered app.")


def generate_add_view_html(table_name):
    """
    Function that generates an HTML form for adding an object
    to the specified model (table_name).
    """
    model_class = get_model_class(table_name)

    # Start building the HTML form
    html_form = '''
    <form method="POST" action="" class="max-w-md mx-auto bg-[#003161] p-6 rounded-lg shadow-md transition-all duration-300 hover:shadow-lg mt-10 space-y-4">
        {% csrf_token %}
    '''

    # Iterate through the model fields and create HTML inputs
    for field in model_class._meta.fields:
        if field.name != 'id':  # Skip the 'id' field
            field_label = escape(field.verbose_name.title())
            field_name = escape(field.name)

            # Determine the input type based on the field type
            if field.get_internal_type() in ['CharField', 'TextField']:
                html_form += f'''
                <div>
                    <label for="{field_name}" class="block  font-semibold">{field_label}</label>
                    <input type="text" id="{field_name}" name="{field_name}" class="form-input block w-full p-2 mt-1 rounded-md focus:ring-2 focus:ring-[#000B58] focus:outline-none transition duration-200 ease-in-out transform hover:scale-105" required>
                </div>
                '''
            elif field.get_internal_type() == 'IntegerField':
                html_form += f'''
                <div>
                    <label for="{field_name}" class="block  font-semibold">{field_label}</label>
                    <input type="number" id="{field_name}" name="{field_name}" class="form-input block w-full p-2 mt-1 rounded-md focus:ring-2 focus:ring-[#000B58] focus:outline-none transition duration-200 ease-in-out transform hover:scale-105" required>
                </div>
                '''
            elif field.get_internal_type() == 'BooleanField':
                html_form += f'''
                <div class="flex items-center">
                    <input type="checkbox" id="{field_name}" name="{field_name}" class="form-checkbox text-[#000B58] focus:ring-2 focus:ring-[#000B58] transition duration-200 ease-in-out transform hover:scale-105">
                    <label for="{field_name}" class="ml-2  font-semibold">{field_label}</label>
                </div>
                '''
            elif field.get_internal_type() == 'DateField':
                html_form += f'''
                <div>
                    <label for="{field_name}" class="block  font-semibold">{field_label}</label>
                    <input type="date" id="{field_name}" name="{field_name}" class="form-input block w-full p-2 mt-1 rounded-md focus:ring-2 focus:ring-[#000B58] focus:outline-none transition duration-200 ease-in-out transform hover:scale-105" required>
                </div>
                '''
            # Add more field types as necessary
            else:
                html_form += f'''
                <div>
                    <label for="{field_name}" class="block  font-semibold">{field_label}</label>
                    <input type="text" id="{field_name}" name="{field_name}" class="form-input block w-full p-2 mt-1 rounded-md focus:ring-2 focus:ring-[#000B58] focus:outline-none transition duration-200 ease-in-out transform hover:scale-105" required>
                </div>
                '''

    # Add the submit button
    html_form += '''
        <button type="submit" class="w-full bg-[#000B58]  font-semibold py-2 px-4 rounded-md hover:bg-[#003161] transition-all duration-300 ease-in-out transform hover:scale-105">
            Submit
        </button>
    </form>
    '''

    return html_form


from django.utils.html import escape
from django.apps import apps

def generate_edit_view_html(table_name):
    """
    Function that generates an HTML form template for editing an object of the specified model (table_name)
    without retrieving the object. The structure will be populated dynamically at runtime.
    """
    model_class = get_model_class(table_name)
    model_name = model_class._meta.model_name.lower()  # e.g., 'book' for the 'Book' model

    # Start building the HTML form with placeholders for dynamic content
    html_form = f'<form method="post" action="" class="space-y-6">\n'
    html_form += '{% csrf_token %}\n'  # Include CSRF token for security

    # Generate form fields based on model fields
    for field in model_class._meta.fields:
        field_label = escape(field.verbose_name.title())
        field_name = field.name
        field_placeholder = f'{{{{ {model_name}.{field_name} }}}}'  # Placeholder for field value

        html_form += f'<div>\n<label class="block text-sm font-medium text-gray-700">{field_label}</label>\n'

        # Different input types based on field characteristics
        if field.get_internal_type() == "TextField":
            html_form += (
                f'<textarea name="{field_name}" rows="3" '
                f'class="mt-1 block w-full shadow-sm sm:text-sm border border-gray-300 rounded-md">'
                f'{field_placeholder}</textarea>\n'
            )
        elif field.get_internal_type() == "AutoField":
            pass
        elif field.get_internal_type() == "BooleanField":
            html_form += (
                f'<input type="checkbox" name="{field_name}" '
                f'class="mt-1 block shadow-sm sm:text-sm border-gray-300 rounded-md" '
                f'{"{{ checked }}" if field_placeholder else ""}>\n'
            )
        else:
            html_form += (
                f'<input type="text" name="{field_name}" value="{field_placeholder}" '
                f'class="mt-1 block w-full shadow-sm sm:text-sm border border-gray-300 rounded-md">\n'
            )

        html_form += '</div>\n'

    # Add a submit button
    html_form += (
        '<div>\n'
        '    <button type="submit" class="w-full inline-flex justify-center py-2 px-4 border border-transparent shadow-sm '
        'text-sm font-medium rounded-md  bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 '
        'focus:ring-offset-2 focus:ring-indigo-500">Save Changes</button>\n'
        '</div>\n'
    )
    html_form += '</form>\n'

    return html_form


def generate_list_view_html(table_name):
    """
    Function that generates an HTML template structure to display a list of objects
    of the specified model (table_name) without retrieving objects.
    """
    model_class = get_model_class(table_name)
    model_name = model_class._meta.model_name.lower()
    collection_name = (model_name + "s").lower()

    # Start building the HTML table structure
    html_table = '<table class="min-w-full divide-y divide-gray-200">\n'
    html_table += '<thead class="bg-gray-50">\n<tr>\n'

    # Create table headers based on model fields
    for field in model_class._meta.fields:
        field_label = escape(field.verbose_name.title())
        html_table += f'<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{field_label}</th>\n'

    # Add an extra column for edit/delete actions
    html_table += '<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>\n'
    html_table += '</tr>\n</thead>\n'

    # Create table body with placeholders for dynamic rendering
    html_table += '<tbody class="bg-white divide-y divide-gray-200">\n'
    html_table += f'{{% for {model_name} in {collection_name} %}}\n<tr>\n'
    
    # Placeholder for each field value within the object
    for field in model_class._meta.fields:
        html_table += f'<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{{{ {model_name}.{field.name} }}}}</td>\n'

    # Add placeholders for edit and delete buttons
    html_table += (
        f'<td class="px-6 py-4 whitespace-nowrap text-sm font-medium">'
        f'<a href="/{table_name}/edit/{{{{ {model_name}.id }}}}" class="text-indigo-600 hover:text-indigo-900">Edit</a> | '
        f'<a href="/{table_name}/delete/{{{{ {model_name}.id }}}}" class="text-red-600 hover:text-red-900">Delete</a>'
        f'</td>\n'
    )

    html_table += '</tr>\n{{% endfor %}}\n'
    html_table += '</tbody>\n</table>\n'

    return html_table

def generate_detail_view_html(table_name):
    """
    Function that generates an HTML structure for displaying details of an object 
    of the specified model (table_name), with placeholders for dynamic data population.
    """
    model_class = get_model_class(table_name)
    model_name = model_class._meta.model_name.lower()  # e.g., 'book' for the 'Book' model

    # Start building the HTML structure
    html_detail = '<div class="space-y-6">\n'
    
    # Loop over model fields and add placeholders for each field value
    for field in model_class._meta.fields:
        field_label = escape(field.verbose_name.title())  # Human-readable field name
        field_name = field.name  # Field name for data access
        field_value_placeholder = f'{{{{ {model_name}.{field_name} }}}}'  # Placeholder for field value

        # Display field label and value
        html_detail += (
            f'<div class="flex items-center space-x-4">\n'
            f'    <span class="text-gray-700 font-medium">{field_label}:</span>\n'
            f'    <span class="text-gray-900">{field_value_placeholder}</span>\n'
            '</div>\n'
        )

    # Add an Edit button to navigate to the edit page
    html_detail += (
        '<div class="mt-4">\n'
        f'    <a href="/{table_name}/edit/{{{{ {model_name}.id }}}}/" '
        'class="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm '
        'text-sm font-medium rounded-md  bg-indigo-600 hover:bg-indigo-700 focus:outline-none '
        'focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">Edit</a>\n'
        '</div>\n'
    )
    
    html_detail += '</div>\n'

    return html_detail
