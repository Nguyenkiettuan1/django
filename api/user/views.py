# Create your views here to print json.
from requests import Response
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .serializers import UserSerializer
from .models import UserCustomer, user_config
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.forms.models import model_to_dict
import random
import re
import json
from ..utils import Obj, Int, UUIDEncoder
from ..policies import customPermission
from ..jwt_token import jwtToken
import uuid

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
    try:
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
    except LookupError :
        return JsonResponse({
            'code': -1,
            'message': LookupError.__doc__
        })

def user_info(request):
    if not request.method == 'GET':
        return JsonResponse({'error': 'Send a valid GET request'})
    # Get header value
    header_value = request.headers or {}
    token = header_value.get('Authorization', '')
    # Get param
    params_value = request.GET or {}
    user_id = params_value.get('id', '')
    try:
        # Validate authen
        if not customPermission.is_authenticated(request, token):
            return JsonResponse({
                'code': -1,
                'message': "User have to login"
            })
        # get uid from request
        req_uid = request.content_params.get('uid', '')
        if req_uid != user_id:
            if not customPermission.is_role_admin(request, token):
                return JsonResponse({
                    'code': -1,
                    'message': "User dont't have permission to access this action"
                })
        # Go query
        found_users = UserCustomer.objects.get(id = user_id)
        # Go convert to object
        user_info = model_to_dict(found_users)
        # remove password field
        user_info.pop('password')
        return JsonResponse({
            "code": 0,
            "message": "Get user info successfully",
            "data": user_info
        })
    except LookupError :
        return JsonResponse({
            'code': -1,
            'message': LookupError.__doc__
        })

@csrf_exempt
def register(request):
    # Validate method
    if not request.method == 'POST':
        return JsonResponse({'error': 'Send a valid POST request'})
    # Get header value
    header_value = request.headers or {}
    token = header_value.get('Authorization', '')
    # Get body value
    raw_data = request.body.decode('utf-8')
    # Parse raw data
    data = json.loads(raw_data)
    user_email = data.get('email', '')
    user_password = data.get('password', '')
    user_role = data.get('role', '')
    user_phone = data.get('phone', '')
    user_status = data.get('status', '')
    try:
        # Validate adcmin add field
        if user_role == '':
            user_role = user_config.get('role', {}).get('USER', 'user')
        else: 
            if not user_role in list(user_config.get('role', {}).values()):
                return JsonResponse({
                    'code': -1,
                    'message': "Invalid role value"
                })
            else:
                if user_role != 'user' and not customPermission.is_role_admin(request, token):
                    return JsonResponse({
                        'code': -1,
                        'message': "User dont't have permission to access this field"
                    })
        # Validate email
        if user_email == '':
            return JsonResponse({
                'code': -1,
                'message': "Email is required"
            })
        else: 
            if not re.match("^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$", user_email):
                return JsonResponse({
                    'code': -1,
                    'message': "Invalid email value"
                })
            # Go found user with email
            go_found_user =  UserCustomer.objects.filter(email = user_email).first() or {}
            if(go_found_user != {}):
                found_user = model_to_dict(go_found_user)
                if not Obj.is_empty(found_user):
                    return JsonResponse({
                        'code': -1,
                        'message': "Email existed, please contact admin"
                })
        # Validate password
        if user_password == '':
            return JsonResponse({
                'code': -1,
                'message': "Password is required"
            })
        else:
            if len(user_password) < 6:
                return JsonResponse({
                    'code': -1,
                    'message': "Password must has at least 6 character"
                })
        # Validate phoneNumber
        if user_phone == '':
            return JsonResponse({
                'code': -1,
                'message': "Phone number is required"
            })
        # Validate status
        if user_status == '':
            user_status = user_config.get('status', {}).get('ACTIVE', '')
        else:
            if not user_status in list(user_config.get('role', {}).values()):
                return JsonResponse({
                    'code': -1,
                    'message': "Invalid status value"
                })
        # prepared create
        prepared_create = {
            "email": user_email,
            "password": user_password,
            "role": user_role,
            "phone": user_phone,
            "status": user_status
        }
        create_user = UserCustomer.objects.create(**prepared_create)
        # Go convert to object
        user_info = model_to_dict(create_user)
        # remove password field
        user_info.pop('password')
        # return resp
        return JsonResponse({
            "code": 0,
            "message": "Register successfully",
            "data": user_info
        })
    except LookupError :
        return JsonResponse({
            'code': -1,
            'message': LookupError.__doc__
        })


    




    
    

