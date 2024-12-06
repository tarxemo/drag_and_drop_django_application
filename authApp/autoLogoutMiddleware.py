from datetime import timedelta, datetime
from django.utils.timezone import now
from django.shortcuts import redirect

class AutoLogoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            last_activity = request.session.get('last_activity')
            current_time = now()

            if last_activity:
                # Convert the string back to a datetime object
                last_activity_time = datetime.fromisoformat(last_activity)
                elapsed_time = current_time - last_activity_time

                if elapsed_time > timedelta(seconds=600):  # 10 minutes
                    from django.contrib.auth import logout
                    logout(request)
                    return redirect('login')  # Replace with your login URL

            # Store the current time as an ISO 8601 string
            request.session['last_activity'] = current_time.isoformat()

        return self.get_response(request)
