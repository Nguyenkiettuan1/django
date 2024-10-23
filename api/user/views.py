# Create your views here to print json.
from requests import Response,request,JSONDecodeError
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .serializers import UserSerializer
from .models import usercustomer
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, logout
from rest_framework.decorators import api_view
import random
import re
import json
import uuid
# Create your views here.





class UserViewSet(viewsets.ModelViewSet):
    permission_classes_by_action = {'create': [AllowAny]}

    queryset = usercustomer.objects.all().order_by('id')
    serializer_class = UserSerializer
    
    def get_permissions(self):
        try:
            return [permission() for permission in self.permission_classes_by_action[self.action]]
        except KeyError:
            return [permission() for permission in self.permission_classes]
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()  # Lấy danh sách người dùng
        serializer = self.get_serializer(queryset, many=True)  # Serialize dữ liệu
        return Response(serializer.data) 
    
    def generate_session_token(length=10):
     return ''.join(random.SystemRandom().choice([chr(i) for i in range(97, 123)] + [str(i) for i in range(10)]) for _ in
                   range(length))


    @api_view(['POST'])
    def login(request):
        
        if not request.method == 'POST':
            return JsonResponse({'error': 'Send a valid POST request'})
        rawdata = request.body.decode('utf-8')
        # username = request.POST.get('email')
        # password = request.POST.get('password')
        data = json.loads(rawdata)
        username = data.get('email')
        password = data.get('password')
        if len(str(password)) < 3:
            return JsonResponse({'error': 'Password needs to be at least 3 character'})
        if not username or not password:
                return JsonResponse({'error': 'Email and password are required.','user':username,'password':password}, status=400)
        # UserModel = usercustomer.objects.get(email = username)
        try:
                # Fetch the user by email
                user = usercustomer.objects.filter(email=username).first()
                if user is None:
                    return JsonResponse({'error': 'User not found'}, status=404)

                # Check the password
                if user.password == password:
                    # Get user data, excluding the password
                    usr_dict = usercustomer.objects.filter(email=username).values().first()
                    usr_dict.pop('password', None)  # Safely remove password if it exists

                    # # Check if a session already exists
                    # if user.session_token != "0":
                    #     return JsonResponse({'error': 'Previous Session Exists'}, status=403)

                    # Generate and save the new session token
                    token = UserViewSet.generate_session_token()
                    user.session_token = token
                    user.save()
                    
                    # Log in the user
                    login(request, user)
                    
                    # Return the token and user data
                    return JsonResponse({'token': token, 'user': usr_dict})

                else:
                    return JsonResponse({'error': 'Invalid Password'}, status=401)

        except Exception as e:
                return JsonResponse({'error': str(e)}, status=400)

    @csrf_exempt
    def signout(request):
        rawdata = request.body.decode('utf-8')# Get the UUID from the request
        data = json.loads(rawdata)
        user_id = data.get('id')
        user_id = uuid.UUID(user_id)
        if not user_id:
            return JsonResponse({'error': 'User ID is required to log out'}, status=400)

        try:
            # Find the user by UUID
            user = usercustomer.objects.get(id=user_id)

            if user is None:
                return JsonResponse({'error': 'User not found'}, status=404)

            # Invalidate the session token
            user.session_token = "0"
            user.save()

            # Log out the user
            logout(request)
            return JsonResponse({'success': 'Logout successful'})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

# class SnippetListView(viewsets.ViewSet):
#     def list(self, request):
#         # Your logic to return snippets
#         snippets = Snippet.objects.all()
#         serializer = SnippetSerializer(snippets, many=True)
#         return Response(serializer.data)

# snippet_list = SnippetListView.as_view({'get': 'list'})



    