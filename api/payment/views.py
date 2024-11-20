from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import UserPayments, PaymentMethod, user_payments_config, payment_config
from .serializers import PaymentSerializer, PaymentMethodSerializer
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.forms.models import model_to_dict
import json
from ..policies import customPermission
from ..product.models import Product, ProductDetails, Color, Size, Material, Type, ProductMaterials, ProductTypes,product_config, product_details_config, color_config, product_colors_config, size_config, product_sizes_config, material_config, product_materials_config, type_config, product_types_config
from ..cart.models import Cart, cart_config
from ..utils import Obj, Int, UUIDEncoder
from ..user.models import UserCustomer

class PaymentMethodViewSet(viewsets.ModelViewSet):
    queryset = PaymentMethod.objects.all()
    serializer_class = PaymentMethodSerializer
    permission_classes = [AllowAny]  # Change this according to your needs

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = UserPayments.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [AllowAny]  # Change this according to your needs
# -----------------------
# --------PAYMENT--------
# -----------------------
@csrf_exempt
def add_payment(request):
    if not request.method == 'POST':
        return JsonResponse({'error': 'Send a valid POST request'})
    # Get header value
    header_value = request.headers or {}
    token = header_value.get('Authorization', '')
    # Get body value
    raw_data = request.body.decode('utf-8')
    data = json.loads(raw_data)
    # Only payment value
    payment_name = data.get('name', '')
    payment_status = data.get('status', '')
    payment_required_field = data.get('requiredDetails', [])
    try:
        # Validate authen
        if not customPermission.is_role_admin(request, token):
            return JsonResponse({
                'code': -1,
                'message': "User dont't have permission to access this action"
            })
        # Go validate payment field
        if payment_name == '':
            return JsonResponse({
                'code': -1,
                'message': "Payment name is required"
            })
        if payment_status != '':
            if not payment_status in list(payment_config.get('status', {}).values()):
                return JsonResponse({
                    'code': -1,
                    'message': "Status does not support"
                })
        else:
            payment_status = payment_config.get('status').get('ACTIVE')
        # Go create
        create_payment = PaymentMethod.objects.create(
            name = payment_name,
            status = payment_status,
            required_details = payment_required_field
        )
        # return
        return JsonResponse({
            'code': 0,
            'message': "Create new payment successfully",
            'data': model_to_dict(create_payment)
        })
    except LookupError :
        return JsonResponse({
            'code': -1,
            'message': LookupError.__doc__
        })

@csrf_exempt
def edit_payment(request):
    if not request.method == 'PUT':
        return JsonResponse({'error': 'Send a valid PUT request'})
    # Get header value
    header_value = request.headers or {}
    token = header_value.get('Authorization', '')
    # Get body value
    raw_data = request.body.decode('utf-8')
    data = json.loads(raw_data)
    # Only payment value
    payment_id = data.get('id', '')
    payment_name = data.get('name', '')
    payment_status = data.get('status', '')
    payment_required_field = data.get('requiredDetails', {})
    try:
        # Validate authen
        if not customPermission.is_role_admin(request, token):
            return JsonResponse({
                'code': -1,
                'message': "User dont't have permission to access this action"
            })
        # Go validate payment field
        if payment_id == '':
            return JsonResponse({
                'code': -1,
                'message': "Payment id is required"
            })
        # Go found payment
        found_payments = PaymentMethod.objects.filter(id = payment_id)
        detect_payment = found_payments.first() or {}
        if detect_payment == {}:
            return JsonResponse({
                'code': -1,
                'message': "Payment not found"
            })
        # Init prepared update
        prepared_update = {}
        if payment_name != '':
            # found payment by name
            found_payment = PaymentMethod.objects.filter(name__iexact = payment_name).first() or {}
            if found_payment != {}:
                # parse found_payments
                found_payments = model_to_dict(found_payment)
                if str(found_payment.get('id')) != payment_id:
                    return JsonResponse({
                        'code': -1,
                        'message': f'Payment {payment_name} is existed'
                    })
            prepared_update['name'] = payment_name
        if payment_status != '':
            if not payment_status in list(payment_config.get('status', {}).values()):
                return JsonResponse({
                    'code': -1,
                    'message': "Status does not support"
                })
            prepared_update['status'] = payment_status
        if payment_required_field != '':
            if not isinstance(payment_required_field, list):
                return JsonResponse({
                    'code': -1,
                    'message': "Payment required field value must be array"
                })
            prepared_update['required_details'] = payment_required_field
        # Go update
        found_payments.update(**prepared_update)
        # return
        return JsonResponse({
            'code': 0,
            'message': "Edit payment successfully",
            'data': { 
                    **model_to_dict(detect_payment)
                    **prepared_update
                }
        })
    except LookupError :
        return JsonResponse({
            'code': -1,
            'message': LookupError.__doc__
        })
    
@csrf_exempt
def get_list_payment(request):
    if not request.method == 'GET':
        return JsonResponse({'error': 'Send a valid GET request'})
    # Get header value
    header_value = request.headers or {}
    token = header_value.get('Authorization', '')
    # Get param value
    params_value = request.GET or {}
    # Only payment value
    payment_id = params_value.get('id', '')
    payment_name = params_value.get('name', '')
    payment_status = params_value.get('status', '')
    # Pagination
    page = int(params_value.get('page', 1))
    limit = int(params_value.get('limit', 10))
    offset = page * limit
    try:
        # Validate authen
        if not customPermission.is_authenticated(request, token):
            return JsonResponse({
                'code': -1,
                'message': "User have to login to access this action"
            })
        # Init prepared update
        prepared_query = {}
        if payment_id != '':
            prepared_query['id'] = payment_id
        if payment_name != '':
            prepared_query['name'] = payment_name
        if payment_status != '':
            if not payment_status in list(payment_config.get('status', {}).values()):
                return JsonResponse({
                    'code': -1,
                    'message': "Status does not support"
                })
            prepared_query['status'] = payment_status
        # Go update
        found_payments = PaymentMethod.objects.filter(**prepared_query)
        # Count total
        total_count = found_payments.count()
        # Paginate
        found_payments = list(found_payments.values()[offset:offset + limit])
        # return
        return JsonResponse({
            'code': 0,
            'message': "Edit payment successfully",
            'data': found_payments,
            'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': total_count
                },
        })
    except LookupError :
        return JsonResponse({
            'code': -1,
            'message': LookupError.__doc__
        })
# ----------------------------
# --------USER PAYMENT--------
# ----------------------------

@csrf_exempt
def add_user_payment(request):
    if not request.method == 'POST':
        return JsonResponse({'error': 'Send a valid POST request'})
    # Get header value
    header_value = request.headers or {}
    token = header_value.get('Authorization', '')
    # Get body value
    raw_data = request.body.decode('utf-8')
    data = json.loads(raw_data)
    # Only payment value
    payment_id = data.get('id', '')
    user_payment_details = data.get('paymentDetails', '')
    user_payment_status = data.get('status', '')

    try:
        # Validate authen
        if not customPermission.is_authenticated(request, token):
            return JsonResponse({
                'code': -1,
                'message': "User dont't have permission to access this action"
            })
        # Go validate payment field
        if payment_id == '':
            return JsonResponse({
                'code': -1,
                'message': "Payment is required"
            })
        # Go found payment
        found_payments = PaymentMethod.objects.filter(id = payment_id,
                                                status = payment_config.get('status').get('ACTIVE')
                                                ).first() or {}
        if found_payments == {}:
            return JsonResponse({
                'code': -1,
                'message': "Payment not found or not support"
            })
        detect_payment = model_to_dict(found_payments)
        payment_required_details = detect_payment.get('required_details', [])
        # Validate required details
        for detail in payment_required_details:
            tmp_detail = user_payment_details.get(detail, '')
            if tmp_detail == '':
                return JsonResponse({
                    'code': -1,
                    'message': f"Details {detail} is required"
                })
        # Validate status
        if user_payment_status != '':
            if not user_payment_status in list(user_payments_config.get('status', {}).values()):
                return JsonResponse({
                    'code': -1,
                    'message': "Status does not support"
                })
        else:
            user_payment_status = user_payments_config.get('status').get('ACTIVE')
        # get uid from request
        req_uid = request.content_params.get('uid', '')
        # Get user 
        get_user = UserCustomer.objects.get(id = req_uid)
        # Go create
        create_user_payment = UserPayments.objects.create(
            status = user_payment_status,
            payment_details = user_payment_details,
            user = get_user,
            payment_method = found_payments
        )
        # return
        return JsonResponse({
            'code': 0,
            'message': "Create new user payment successfully",
            'data': model_to_dict(create_user_payment)
        })
    except LookupError :
        return JsonResponse({
            'code': -1,
            'message': LookupError.__doc__
        })

@csrf_exempt
def get_list_user_payment(request):
    if not request.method == 'GET':
        return JsonResponse({'error': 'Send a valid GET request'})
    # Get header value
    header_value = request.headers or {}
    token = header_value.get('Authorization', '')
    # Get param value
    params_value = request.GET or {}
    # Only payment value
    payment_id = params_value.get('payment', '')
    user_id = params_value.get('user', '')
    user_payment_status = params_value.get('status', '')
    # Pagination
    page = int(params_value.get('page', 1))
    limit = int(params_value.get('limit', 10))
    offset = page * limit
    try:
        # Validate authen
        if not customPermission.is_authenticated(request, token):
            return JsonResponse({
                'code': -1,
                'message': "User dont't have permission to access this action"
            })
        #  Get req user
        req_uid = request.content_params.get('uid', '')
        # Init prepared query
        prepared_query = {
            "user": req_uid,
            "status": user_payments_config.get('status').get('ACTIVE')
        }
        # Only admin can access this field
        if user_id != '' or user_payment_status != '':
            if not customPermission.is_role_admin(request, token):
                return JsonResponse({
                    'code': -1,
                    'message': "User dont't have permission to access this action"
                })
            if user_id != '':
                found_users = UserCustomer.objects.filter(id = req_uid).first() or {}
                if found_users == {}:
                    return JsonResponse({
                        'code': -1,
                        'message': "User not found"
                    })
                prepared_query["user"] = user_id
            if user_payment_status != '':
                if not user_payment_status in list(user_payments_config.get('status', {}).values()):
                    return JsonResponse({
                        'code': -1,
                        'message': "Status does not support"
                    })
                prepared_query["status"] = user_payment_status
        else:
            prepared_query['payment_method__status'] = payment_config.get('status').get('ACTIVE')
        # Go validate payment field
        if payment_id != '':
            # Go found payment
            found_payments = PaymentMethod.objects.filter(id = payment_id,
                                                status = payment_config.get('status').get('ACTIVE')
                                                ).first() or {}
            if found_payments == {}:
                return JsonResponse({
                    'code': -1,
                    'message': "Payment not found"
                })
            prepared_query["payment_method"] = payment_id
        # found all user payment
        found_user_payments = UserPayments.objects.filter(**prepared_query).select_related('payment_method')
        # Count total
        total_count = found_user_payments.count()
        # Paginate
        user_payments = list(found_user_payments.values()[offset:offset + limit])
        # return
        return JsonResponse({
            'code': 0,
            'message': "Get list user payment successfully",
            'data': user_payments,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total_count
            },
        })
    except LookupError :
        return JsonResponse({
            'code': -1,
            'message': LookupError.__doc__
        })