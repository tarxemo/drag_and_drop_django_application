from django.template import TemplateDoesNotExist
from django.http import HttpResponseServerError
from django.utils.deprecation import MiddlewareMixin
from TB.utils import *
class TemplateGenerationMiddleware(MiddlewareMixin):
    """
    Middleware to handle missing templates by generating them dynamically.
    """

    def process_template_response(self, request, response):
        """
        Check if the response is a template response and handle missing templates.
        """
        # Check if the response is an HttpResponse object
        if hasattr(response, 'render') and callable(response.render):
            try:
                response.render()  # Try to render the response
            except TemplateDoesNotExist as e:
                # Handle the case where the template does not exist
                # Extracting the template name from the exception message
                template_name = str(e).split(' ')[-1].strip("'")

                # Generate the template based on the request
                model_name = template_name.split('_')[1]  # Assuming format is 'username_model_action'
                action = template_name.split('_')[-1]  # Get the action part
                username = request.user.username

                # Call the function to parse and save the HTML template
                parse_and_save_html(request, model_name, action)

                # Re-attempt rendering now that the template should exist
                response.render()
        
        return response  # Continue processing the request
