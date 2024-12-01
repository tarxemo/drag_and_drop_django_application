from django.apps import apps
from django.shortcuts import render
from django.http import Http404

def generate_table_list_view_code(table_name, user):
    view_code = f"""
def {table_name.lower()}_list_view(request):
    \"\"\"
    View function to retrieve all data from the '{table_name}' table.
    \"\"\"
    queryset = {table_name}.objects.all()
    return render(request, '{user.username}_{table_name}_list.html', {{
        '{table_name}': '{table_name}',
        '{table_name.lower()}s': queryset
    }})
    """
    print(view_code)
    return view_code


def generate_table_create_view_code(table_name, user):
    view_code = f"""
def {table_name.lower()}_create_view(request):
    \"\"\"
    View function to create a new '{table_name}' instance.
    \"\"\"
    if request.method == 'POST':
        form = {table_name}Form(request.POST)
        if form.is_valid():
            form.save()
            return redirect('{user.username}_{table_name.lower()}_list')
    else:
        form = {table_name}Form()

    return render(request, '{user.username}_{table_name}_form.html', {{
        'form': form
    }})
    """
    return view_code

def generate_table_detail_view_code(table_name, user):
    view_code = f"""
def {table_name.lower()}_detail_view(request, pk):
    \"\"\"
    View function to retrieve details of a single '{table_name}' instance.
    \"\"\"
    try:
        instance = {table_name}.objects.get(pk=pk)
    except {table_name}.DoesNotExist:
        raise Http404("'{table_name}' instance does not exist.")

    return render(request, '{user.username}_{table_name}_detail.html', {{
        '{table_name.lower()}': instance
    }})
    """
    print(view_code)
    return view_code

def generate_table_update_view_code(table_name, user):
    view_code = f"""
def {table_name.lower()}_update_view(request, pk):
    \"\"\"
    View function to update an existing '{table_name}' instance.
    \"\"\"
    try:
        instance = {table_name}.objects.get(pk=pk)
    except {table_name}.DoesNotExist:
        raise Http404("'{table_name}' instance does not exist.")

    if request.method == 'POST':
        form = {table_name}Form(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('{user.username}_{table_name.lower()}_detail', pk=pk)
    else:
        form = {table_name}Form(instance=instance)

    return render(request, '{user.username}_{table_name}_form.html', {{
        'form': form
    }})
    """
    print(view_code)
    return view_code


def generate_table_delete_view_code(table_name, user):
    view_code = f"""
def {table_name.lower()}_delete_view(request, pk):
    \"\"\"
    View function to delete a '{table_name}' instance.
    \"\"\"
    try:
        instance = {table_name}.objects.get(pk=pk)
    except {table_name}.DoesNotExist:
        raise Http404("'{table_name}' instance does not exist.")

    if request.method == 'POST':
        instance.delete()
        return redirect('{user.username}_{table_name.lower()}_list')

    return render(request, '{user.username}_{table_name}_confirm_delete.html', {{
        '{table_name.lower()}': instance
    }})
    """
    print(view_code)
    return view_code


