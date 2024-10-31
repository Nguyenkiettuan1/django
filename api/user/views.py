# Create your views here to print json.
from requests import Response
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .serializers import UserSerializer
from .models import UserCustomer
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
import random
import re
import json
from ..utils import Obj, Int, UUIDEncoder
from ..policies import customPermission
from ..jwt_token import jwtToken
import jwt
class UserViewSet(viewsets.ModelViewSet):
    permission_classes_by_action = {'create': [AllowAny]}

    queryset = UserCustomer.objects.all().order_by('id')
    serializer_class = UserSerializer

@csrf_exempt
def login(request):
    if not request.method == 'POST':
        return JsonResponse({'error': 'Send a valid POST request'})
    raw_data = request.body.decode('utf-8')
    data = json.loads(raw_data)
    username = data.get('email')
    password = data.get('password')

    if not re.match("^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$", username):
        return JsonResponse({'error': 'Ivalid email address'})

    try:
        user = UserCustomer.objects.get(email = username)
        user_password = user.password or ''
        if user.password != password:
            return JsonResponse({
                'code': -1,
                'message': 'Invalid user information'
            })
        user_id = str(user.id) or ''
        token = jwtToken.generate_token(user_id)
        user_info = {
            "id" : user_id,
            "email" : user.email or ''
        }
        # remove user password
        return JsonResponse({
            'code': 0,
            'data': {
                'token': token, 
                'user': user_info
            },
            'message': 'Login successfully'
        })

    except LookupError :
        return JsonResponse({
            'code': -1,
            'message': LookupError.__doc__
        })
    
def list_user(request):
    if not request.method == 'GET':
        return JsonResponse({'error': 'Send a valid GET request'})
    # Get header value
    header_value = request.headers or {}
    token = header_value.get('Authorization', '')
    # Get param
    params_value = request.GET or {}
    user_id = params_value.get('id', '')
    user_email = params_value.get('email', '')
    user_status = params_value.get('status', '')
    # Pagination
    page = int(params_value.get('page', 1))
    limit = int(params_value.get('status', 10))
    offset = (page - 1) * limit
    # Validate authen
    if not customPermission.is_role_admin(token):
        return JsonResponse({
            'code': -1,
            'message': "User dont't have permission to access this action"
        })
    # Init prepared query
    prepared_query = {}
    if not user_id == '':
        prepared_query['id'] = user_id
    if not user_status == '':
        prepared_query['status'] = user_status
    if not user_email == '':
        prepared_query['email'] = user_email
    # Go query
    found_users = UserCustomer.objects.filter(**prepared_query)
    # Count total
    total_count = found_users.count()
    # Paginate
    found_users = list(found_users.values()[offset:offset + limit])
    for i in range(len(found_users)):
        found_users[i].pop('password')
    return JsonResponse({
        'code': 0,
        'data': found_users,
        'pagination': {
            'page': page,
            'limit': limit,
            'total': total_count
        },
        'message': "Get list user successfully"
    })
    
    

