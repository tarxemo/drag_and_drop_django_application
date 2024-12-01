# authApp/middleware.py
from django.shortcuts import redirect
from django.urls import reverse

class LoginRequiredMiddleware:
    """
    Middleware that redirects users who are not logged in to the login page.
    You can customize which views to apply it to.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Exclude certain paths from being protected (like login or signup)
        if not request.user.is_authenticated and request.path not in [reverse('login'), reverse('signup'), reverse('signup')]:
            return redirect('login')  # or `redirect('/auth/login/')`

        response = self.get_response(request)
        return response
