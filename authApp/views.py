# from rest_framework import generics, permissions
# from rest_framework_simplejwt.tokens import RefreshToken
# from django.contrib.auth import authenticate, login
# from rest_framework.response import Response
# from rest_framework import status
# from authApp.models import *
# from .serializers import *
# from django.contrib.auth.models import User


# class RegisterView(generics.CreateAPIView):
#     queryset = CustomUser.objects.all()
#     serializer_class = UserSerializer
#     permission_classes = [permissions.AllowAny]

# class LoginView(generics.GenericAPIView):
#     serializer_class = UserLoginSerializer
#     permission_classes = [permissions.AllowAny]

#     def post(self, request, *args, **kwargs):
#         email = request.data.get('email')
#         password = request.data.get('password')
        
#         # Use authenticate to handle password checking and user retrieval
#         user = authenticate(request, email=email, password=password)
        
#         if user:
#             login(request, user)
            
#             refresh = RefreshToken.for_user(user)
#             user_data = UserSerializer(user).data
            
#             return Response({
#                 'user': user_data,
#                 'refresh': str(refresh),
#                 'access': str(refresh.access_token),
#             })
        
#         return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)




# In views.py
from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm
from django.contrib.auth import logout

def signup(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()  # Save the new user
            return redirect('login')  # Redirect to the login page after successful signup
    else:
        form = CustomUserCreationForm()
    
    return render(request, "registration/signup.html", {"form": form})


def landingpage(request):
    return render(request, 'landingpage.html')

def user_logout(request):
    logout(request)
    return redirect('login') 