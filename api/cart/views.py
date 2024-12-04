from rest_framework import viewsets
from requests import Response
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .serializers import CartSerializer  # Make sure to create this serializer
from rest_framework.permissions import AllowAny
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.forms.models import model_to_dict
from .models import Cart, cart_config
from ..product.models import Product, ProductDetails, Color, Size, Material, Type, ProductMaterials, ProductTypes,product_config, product_details_config, color_config, product_colors_config, size_config, product_sizes_config, material_config, product_materials_config, type_config, product_types_config
from ..user.models import UserCustomer
import json
import re
from ..utils import Obj, Int, UUIDEncoder
from ..policies import customPermission
from ..jwt_token import jwtToken
class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [AllowAny]  # Adjust permissions as needed

@csrf_exempt
def add_to_cart(request):
    if not request.method == 'POST':
        return JsonResponse({'error': 'Send a valid POST request'})
    # Get header value
    header_value = request.headers or {}
    token = header_value.get('Authorization', '')
    # Get raw data
    raw_data = request.body.decode('utf-8')
    data = json.loads(raw_data)
    # Get param
    product_details = data.get('productDetails', '')
    product_qty = data.get('productQty', '')
    try:
        # Validate authen
        if not customPermission.is_authenticated(request, token):
            return JsonResponse({
                'code': -1,
                'message': "User have to login"
            })
        # get uid from request
        req_uid = request.content_params.get('uid', '')
        # Validate param
        if product_details == '':
            return JsonResponse({
                'code': -1,
                'message': "Product details is required"
            })
        # Validate product details
        found_product_details = ProductDetails.objects.filter(
                id = product_details,
                status = product_details_config.get('status').get('ACTIVE'),
                product__status = product_config.get('status').get('ACTIVE')
            ).select_related('product').first() or {}
        if found_product_details == {}:
            return JsonResponse({
                'code': -1,
                'message': "Product detail not found"
            })
        product_details_info = model_to_dict(found_product_details)
        product_info = model_to_dict(found_product_details.product)
        product_details_qty = product_details_info.get('qty', 0)
        if product_qty == '':
            return JsonResponse({
                'code': -1,
                'message': "Order qty is required"
            })
        else:
            # Validate qty
            if not isinstance(product_qty, int):
                return JsonResponse({
                    'code': -1,
                    'message': "Qty must be a number"
                })
            if product_qty < 0:
                return JsonResponse({
                    'code': -1,
                    'message': "Qty must be positive integer"
                })
            if product_details_qty < product_qty:
                return JsonResponse({
                    'code': -1,
                    'message': "Don't have enough available product"
                })
        # Go found cart
        found_cart = Cart.objects.filter(
            product_details__in = [product_details],
            user__in = [req_uid]
        ).first() or {}
        # init cart
        create_cart = {}
        if(found_cart != {}):
            # parse found_cart
            found_cart = model_to_dict(found_cart)
            # Get cart id
            found_cart_id = str(found_cart.get('id'))
            found_cart_qty = found_cart.get('qty')
            found_cart_status = found_cart.get('status')
            total_qty = product_qty
            if(found_cart_status == cart_config.get('status').get('ACTIVE')):
                total_qty += found_cart_qty
            if product_details_qty < total_qty:
                return JsonResponse({
                    'code': -1,
                    'message': "Don't have enough available product"
                })
            # Go update
            Cart.objects.filter(id = found_cart_id).update(
                status = cart_config.get('status').get('ACTIVE'),
                qty = total_qty
            )
            # found after update
            create_cart = model_to_dict(Cart.objects.filter(id = found_cart_id).first())
        else:
            # Get user 
            get_user = UserCustomer.objects.get(id = req_uid)
            # Go create cart
            create_cart = model_to_dict(Cart.objects.create(
                product_details = found_product_details,
                user = get_user,
                qty = product_qty
            ))
        return JsonResponse({
            'code': 0,
            'message': 'Add to cart successfully',
            'data': create_cart
        })
    except LookupError :
        return JsonResponse({
            'code': -1,
            'message': LookupError.__doc__
        })

@csrf_exempt
def get_list_cart(request):
    if not request.method == 'GET':
        return JsonResponse({'error': 'Send a valid GET request'})
    # Get header value
    header_value = request.headers or {}
    token = header_value.get('Authorization', '')
    # Get param
    params_value = request.GET or {}
    parse_params = dict(params_value)
    cart_id = parse_params.get('id[]', [])

    try:
        # Validate authen
        if not customPermission.is_authenticated(request, token):
            return JsonResponse({
                'code': -1,
                'message': "User have to login"
            })
        # get uid from request
        req_uid = request.content_params.get('uid', '')
        # Init prepared_query
        prepared_query = {}
        if not Obj.is_empty(cart_id):
            prepared_query['id__in'] = cart_id
        
        # Find all cart by user id
        found_user_carts = list(
            Cart.objects.filter(
                **prepared_query,
                user = req_uid,
                status = cart_config.get('status').get('ACTIVE')
            ).select_related('product_details')
        )
        # filter and parse cart
        filter_cart = []
        for user_cart in found_user_carts:
            # Get product detail
            product_detail = model_to_dict(user_cart.product_details)
            product_detail_qty = product_detail.get('qty')
            product_detail_status = product_detail.get('status')
            # found product detail color
            product_detail_color = model_to_dict(user_cart.product_details.color)
            product_detail_color_name = product_detail_color.get('name')
            # found product detail size
            product_detail_size = model_to_dict(user_cart.product_details.size)
            product_detail_size_name = product_detail_size.get('name')
            # found product info
            product = model_to_dict(user_cart.product_details.product)
            product_name = product.get('name')
            product_price = product.get('price')
            product_status = product.get('status')
            product_img = product.get('image')[0] or ''
            # Parse cart
            tmp_cart = model_to_dict(user_cart)
            tmp_cart.pop('user')
            tmp_cart_qty = tmp_cart.get('qty')
            tmp_cart_id = str(tmp_cart.get('id'))
            if (product_detail_qty == 0 
               or product_detail_status != product_details_config.get('status').get('ACTIVE')
               or product_status != product_config.get('status').get('ACTIVE')
            ):
                Cart.objects.filter(id = tmp_cart_id).update(
                    status = cart_config.get('status').get('IN_ACTIVE'),
                    qty = 0
                )
                # Go update cart
                continue
            if tmp_cart_qty > product_detail_qty:
                # Update new qry for cart
                Cart.objects.filter(id = tmp_cart_id).update(
                    qty = product_detail_qty
                )
                # Renew tmp_cart_qty
                tmp_cart_qty = product_detail_qty

            filter_cart.append({
                **tmp_cart,
                "qty": tmp_cart_qty,
                "product": {
                    "name": product_name,
                    "price": product_price,
                    "img": product_img
                },
                "color": product_detail_color_name,
                "size": product_detail_size_name,
                "availableQty": product_detail_qty
            })
            
        # validate cart
        return JsonResponse({
            'code': 0,
            'message': 'Get list cart successfully',
            'data': filter_cart
        })
    except LookupError :
        return JsonResponse({
            'code': -1,
            'message': LookupError.__doc__
        })

@csrf_exempt
def edit_cart(request):
    if not request.method == 'PUT':
        return JsonResponse({'error': 'Send a valid PUT request'})
    # Get header value
    header_value = request.headers or {}
    token = header_value.get('Authorization', '')
    # Get raw data
    raw_data = request.body.decode('utf-8')
    data = json.loads(raw_data)
    # Get param
    cart_id = data.get('cart', '')
    cart_status = data.get('status', '')
    cart_qty = data.get('qty', '')
    try:
        # Validate authen
        if not customPermission.is_authenticated(request, token):
            return JsonResponse({
                'code': -1,
                'message': "User have to login"
            })
        # get uid from request
        req_uid = request.content_params.get('uid', '')
        if cart_id == '':
            return JsonResponse({
                'code': -1,
                'message': "id is required"
            })
        # Found cart
        found_cart = Cart.objects.filter(
            id = cart_id,
            user = req_uid,
            status = cart_config.get('status').get('ACTIVE')
        )
        # Detect cart
        detect_cart = found_cart.select_related('product_details').first()
        if not detect_cart:
            return JsonResponse({
                'code': -1,
                'message': "Cart not found"
            })
        # Init prepared_update
        prepared_update = {}
        # Get product details qty
        product_details_qty = model_to_dict(detect_cart.product_details).get('qty')
        cart_info = model_to_dict(detect_cart)
        cart_info.pop('user')
        if cart_qty != '':
            # Validate qty
            if not isinstance(cart_qty, int):
                return JsonResponse({
                    'code': -1,
                    'message': "Qty must be a number"
                })
            if cart_qty < 0:
                return JsonResponse({
                    'code': -1,
                    'message': "Qty must be positive integer"
                })
            if product_details_qty < cart_qty:
                return JsonResponse({
                    'code': -1,
                    'message': "Don't have enough available product"
                })
            prepared_update['qty'] = cart_qty
        
        # Validate status
        if cart_status != '':
            if not cart_status in [
                cart_config.get('status').get('IN_ACTIVE'),
                cart_config.get('status').get('DELETED')]:
                return JsonResponse({
                    'code': -1,
                    'message': "Status does not support in this action"
                })
            prepared_update['status'] = cart_status
            # Auto detact cart qty to 0
            prepared_update['qty'] = 0
        if Obj.is_empty(prepared_update):
            return JsonResponse({
                'code': -1,
                'message': "Don't have any data to update"
            })
        # Go update
        found_cart.update(**prepared_update)
        # validate cart
        return JsonResponse({
            'code': 0,
            'message': 'Update cart successfully',
            'data': {
                **cart_info,
                **prepared_update
            }
        })
    except LookupError :
        return JsonResponse({
            'code': -1,
            'message': LookupError.__doc__
        })