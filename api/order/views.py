from rest_framework import viewsets
from .serializers import OrderSerializer,OrderdetailsSerializer
# Import model
from .models import OrderDetails, Order, order_config
from ..product.models import Product, ProductDetails, Color, Size, Material, Type, ProductMaterials, ProductTypes,product_config, product_details_config, color_config, product_colors_config, size_config, product_sizes_config, material_config, product_materials_config, type_config, product_types_config
from ..user.models import UserCustomer
from ..payment.models import UserPayments, user_payments_config, payment_config
from ..cart.models import Cart, cart_config
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework.decorators import action
from django.views.decorators.csrf import csrf_exempt
from django.forms.models import model_to_dict
import re
import json
from ..utils import Obj, Int, UUIDEncoder, Date
from ..policies import customPermission
from ..jwt_token import jwtToken
from django.db.models import F

# ViewSet for Product
class orderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [AllowAny]
    
class orderdetailsViewSet(viewsets.ModelViewSet):
    queryset = OrderDetails.objects.all()
    serializer_class = OrderdetailsSerializer
    permission_classes = [AllowAny]


# Go add order
@csrf_exempt
def add_order(request):
    if not request.method == 'POST':
        return JsonResponse({'error': 'Send a valid POST request'})
    # Get header value
    header_value = request.headers or {}
    token = header_value.get('Authorization', '')
    # Get body value
    raw_data = request.body.decode('utf-8')
    data = json.loads(raw_data)
    # Get order value
    carts = data.get('carts', [])
    product = data.get('product', {})
    user_payment_method = data.get('userPaymentMethod', '')
    order_address = data.get('address', '')
    try:
        # Validate authen
        if not customPermission.is_authenticated(request, token):
            return JsonResponse({
                'code': -1,
                'message': "User have to login before do this action"
            })
        # get uid from request
        req_uid = request.content_params.get('uid', '')
        # Go found user
        req_user_info = UserCustomer.objects.get(id = req_uid)
        if Obj.is_empty(carts) and Obj.is_empty(product):
            return JsonResponse({
                'code': -1,
                'message': "Don't have any product to create order"
            })
        # Init found payment
        found_user_payment = {}
        # Validate user payment
        if user_payment_method != '':
            found_user_payment = UserPayments.objects.filter(
                id = user_payment_method,
                user = req_uid,
                status = user_payments_config.get('status').get('ACTIVE'),
                payment_method__status = payment_config.get('status').get('ACTIVE')
            ).select_related('payment_method').first() or {}
            if found_user_payment == {}:
                return JsonResponse({
                    'code': -1,
                    'message': "User payment method not found"
                })
        # Init prepared order
        prepared_order = {
            "user": req_user_info,
            "status": order_config.get('status').get("PROGRESS"),
        }
        # Init prepared order_details
        prepared_order_details = []
        # Init order_total
        order_total = 0.0
        if not Obj.is_empty(product): 
            product_details = product.get('details', ''),
            product_qty = product.get('qty', '')
            # Go found product details
            found_product_details = ProductDetails.objects.filter(
                id = product_details,
                status = product_details_config.get('status').get('ACTIVE'),
                product__status = product_config.get('status').get('ACTIVE')
            ).select_related('product').first() or {}
            if found_product_details == {}:
                return JsonResponse({
                    'code': -1,
                    'message': "Product not found"
                })
            # Detact found_product_details
            product_details_info = model_to_dict(found_product_details)
            # Get product detail qty
            product_details_qty = product_details_info.get('qty')
            if product_qty > product_details_qty:
                return JsonResponse({
                    'code': -1,
                    'message': "Don't have enough available product to create order"
                })
            # Get product price
            product_price = model_to_dict(found_product_details.product).get('price')
            # Count order total
            order_total += product_price * product_qty
            prepared_order_details.append({
                "product_details" : found_product_details,
                "qty": product_qty
            })
        if not Obj.is_empty(carts):
            # Go found user cart
            found_user_carts = Cart.objects.filter(
                id__in = carts,
                user = req_uid,
                status = cart_config.get('status').get('ACTIVE')
            ).select_related('product_details')
            parsed_found_user_carts = list(found_user_carts)
            if len(parsed_found_user_carts) < len(carts):
                return JsonResponse({
                    'code': -1,
                    'message': "Missing cart value"
                })
            for found_cart in parsed_found_user_carts:
                # Parse cart info
                cart_info = model_to_dict(found_cart)
                product_details_info = found_cart.product_details
                product_info = model_to_dict(product_details_info.product)
                # Parse product details info
                parse_product_details_info = model_to_dict(product_details_info)
                # Get cart qty 
                cart_qty = cart_info.get('qty')
                # get product details qty 
                product_details_qty = parse_product_details_info.get('qty')
                product_details_status = product_info.get('status')
                # Get product price
                product_price = product_info.get('price')
                product_status = product_info.get('status')
                if product_details_qty < cart_qty :
                    return JsonResponse({
                        'code': -1,
                        'message': "Don't have enough available product to create order"
                    })
                if (product_details_status != product_details_config.get('status').get('ACTIVE')
                    or product_status != product_config.get('status').get('ACTIVE')):
                    return JsonResponse({
                        'code': -1,
                        'message': "Product sold out"
                    })
                order_total += product_price * cart_qty
                prepared_order_details.append({
                    "product_details" : product_details_info,
                    "qty": cart_qty
                })
        # Go validate found_user_payment
        # Init balance info
        balance_info = {
            "total": order_total,
            "prepaid" : 0.0,
            "remaining": order_total
        }
        # Init final address
        final_address = ''
        if found_user_payment != {}:
            # Detect user_payment
            user_payment_info = model_to_dict(found_user_payment)
            # Set final address
            final_address = user_payment_info.get('product_details', {}).get('address', '')
            # Detect payment method
            payment_method = model_to_dict(found_user_payment.payment_method)
            # Get payment name
            payment_method_name = payment_method.get('name')
            # Add payment info
            prepared_order["payment"] = found_user_payment
            # Alter balance info
            if payment_method_name in payment_config.get('is_prepaid', {}):
                balance_info = {
                    "prepaid" : order_total,
                    "total": order_total,
                    "remaining": 0.0
                }
        if order_address != '':
            final_address = order_address
        else:
            if final_address == '':
                return JsonResponse({
                    'code': -1,
                    'message': "Order address is required"
                })
        prepared_order = {
            **prepared_order,
            **balance_info,
            "address": final_address
        }
        # Go create order
        create_order = Order.objects.create(**prepared_order)
        # parse create order
        # Create order details
        created_order_details = []
        for detail in prepared_order_details:
            # Create order details.
            product_details_info = detail.get('product_details')
            detect_product_detail = model_to_dict(product_details_info)
            product_detail_qty = detect_product_detail.get('qty')
            product_detail_id = detect_product_detail.get('id')
            # Create order details
            create_order_details = OrderDetails.objects.create(
                **detail,
                order = create_order
            )
            # Update product detail qty
            new_qty = product_detail_qty - detail.get('qty')
            # Go update product details qty
            ProductDetails.objects.filter(id = product_detail_id).update(qty = new_qty)
            created_order_details.append(model_to_dict(create_order_details))
        # update cart
        found_user_carts.update(
            status = cart_config.get('status').get('IN_ACTIVE')
        )
        return JsonResponse({
            'code': 0,
            'message': "Create order successfully",
            'data': {
                **model_to_dict(create_order),
                "details": created_order_details
            },
        })
        # Go validate order detals
    except LookupError :
        return JsonResponse({
            'code': -1,
            'message': LookupError.__doc__
        })
    
@csrf_exempt
def get_list_order(request):
    if not request.method == 'GET':
        return JsonResponse({'error': 'Send a valid GET request'})
    # Get header value
    header_value = request.headers or {}
    token = header_value.get('Authorization', '')
    # Get params
    params_value = request.GET or {}
    # Only payment value
    order_id = params_value.get('order', '')
    order_status = params_value.get('status', '')
    from_date = params_value.get('fromDate', '')
    to_date = params_value.get('toDate', '')
    must_show_other = params_value.get('mustShowOther', False)
    # Pagination
    page = int(params_value.get('page', 0))
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
        # Go detect user
        is_ad_staff = customPermission.is_role_admin_or_staff(request, token)
        # Init preparedQuery
        prepared_query = {}
        # Auto add if user is not admin or staff
        if not is_ad_staff or not must_show_other:
            prepared_query['user'] = req_uid
        if order_id != '':
            prepared_query['id'] = order_id
        if from_date != '':
            if not Date.validate_date_format(from_date):
                return JsonResponse({
                    'code': -1,
                    'message': "Invalid from date format"
                })
            prepared_query['created_at__gte'] = from_date
        if to_date != '':
            if not Date.validate_date_format(to_date):
                return JsonResponse({
                    'code': -1,
                    'message': "Invalid to date format"
                })
            prepared_query['created_at__lte'] = to_date
        if order_status != '':
            if order_status not in list(order_config.get('status', {}).values()):
                return JsonResponse({
                    'code': -1,
                    'message': "Trạng thái không được hỗ trợ"
                })
            prepared_query['status'] = order_status
        # Go found order
        found_orders = Order.objects.filter(**prepared_query).select_related('payment')
        # Count total
        total_count = found_orders.count()
        annotated_orders  = found_orders.annotate(payment_method_name=F('payment__payment_method__name'))
        # Paginate
        detect_orders = list(annotated_orders.values()[offset:offset + limit])
        # return
        return JsonResponse({
            'code': 0,
            'message': "Get list orders successfully",
            'data': detect_orders,
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

@csrf_exempt
def order_info(request):
    if not request.method == 'GET':
        return JsonResponse({'error': 'Send a valid GET request'})
    # Get header value
    header_value = request.headers or {}
    token = header_value.get('Authorization', '')
    # Get params
    params_value = request.GET or {}
    # Only payment value
    order_id = params_value.get('id', '') 
    try:
        # Validate authen
        if not customPermission.is_authenticated(request, token):
            return JsonResponse({
                'code': -1,
                'message': "User dont't have permission to access this action"
            })
        #  Get req user
        req_uid = request.content_params.get('uid', '')
        # Go detect user
        is_ad_staff = customPermission.is_role_admin_or_staff(request, token)
        if order_id == '':
            return JsonResponse({
                'code': -1,
                'message': "Order id is required"
            })
        # Init preparedQuery
        prepared_query = {
            "id": order_id
        }
        # Auto add if user is not admin or staff
        if not is_ad_staff:
            prepared_query['user'] = req_uid
        # Go found order
        found_orders = Order.objects.filter(**prepared_query).first() or {}
        if found_orders == {}:
            return JsonResponse({
                'code': -1,
                'message': "Order not found"
            })
        found_orders = model_to_dict(found_orders)
        # Go found order details
        found_order_details = OrderDetails.objects.filter(order = order_id).select_related('product_details')
        annotated_order_details  = found_order_details.annotate(    product_name=F('product_details__product__name'),
                                                                    product_price=F('product_details__product__price'),
                                                                    product_size=F('product_details__size__name'),
                                                                    product_color=F('product_details__color__name'))
        # Paginate
        detect_order_details = list(annotated_order_details.values())
        return JsonResponse({
                'code': 0,
                'message': "Get order info successfully",
                'data': {
                    **found_orders,
                    'details': detect_order_details
                }
            })
    except LookupError :
        return JsonResponse({
            'code': -1,
            'message': LookupError.__doc__
        })

@csrf_exempt
def update_order_status(request):
    if not request.method == 'PUT':
        return JsonResponse({'error': 'Send a valid PUT request'})
    # Get header value
    header_value = request.headers or {}
    token = header_value.get('Authorization', '')
    # Get body value
    raw_data = request.body.decode('utf-8')
    data = json.loads(raw_data)
    # Get order data
    order_id = data.get('id', '')
    order_status = data.get('status', '')
    # Init must update product_details_qty
    must_update_product_details_qty = False
    try:
    # Validate authen
        if not customPermission.is_authenticated(request, token):
            return JsonResponse({
                'code': -1,
                'message': "User have to login before do this action"
            })
        # Get uid from request
        req_uid = request.content_params.get('uid', '')
        # Init is_admin_or_staff
        is_admin_or_staff = customPermission.is_role_admin_or_staff(request, token)
        if order_id == '':
            return JsonResponse({
                'code': -1,
                'message': "Order id is required"
            })
        # Init prepare query
        prepared_query = {
            'id': order_id
        }
        if not is_admin_or_staff:
            prepared_query['user'] = req_uid
        # Get order info
        found_order = Order.objects.filter(**prepared_query) or {}
        detect_found_order = found_order.first() or {}
        if detect_found_order == {}:
            return JsonResponse({
                'code': -1,
                'message': "Order not found"
            })
        # Detect order_info
        found_order_info = model_to_dict(detect_found_order)
        found_order_status = found_order_info.get('status', '')
        available_status = list(order_config.get('status', {}).values())
        # Validate update status
        if order_status == '':
            return JsonResponse({
                'code': -1,
                'message': "Trạng thái đơn hàng đang trống"
            })
        # go filter available status for user
        if not is_admin_or_staff:
                # User have only deleted status to access
            if found_order_status == order_config.get('status').get('PROGRESS'):
                available_status = [order_config.get('status').get("DELETED")]
                # User have only completed status to access
            if found_order_status == order_config.get('status').get('TO_SHIP'):
                available_status = [order_config.get('status').get("COMPLETED")]
                # User have any status to access
            if found_order_status in [order_config.get('status').get("DELETED"), 
                                      order_config.get('status').get("COMPLETED")]:
                available_status = []
        if not order_status in available_status:
            return JsonResponse({
                'code': -1,
                'message': "Trạng thái đơn hàng không hỗ trợ"
            })
        if order_status == found_order_status:
            return JsonResponse({
                    'code': -1,
                    'message': "Trang thái đang được cập nhật trùng lặp"
            })
        # if found_order_status in [order_config.get('status').get('TO_SHIP'), order_config.get('status').get('COMPLETED')] and order_status == order_config.get('status').get('DELETED'):
        #     return JsonResponse({
        #             'code': -1,
        #             'message': "Can not delete order while it's on shipping"
        #         })                
        if order_status in [order_config.get('status').get('DELETED')]:
            # Found order details by order id
            found_order_details = OrderDetails.objects.filter(order = order_id).select_related('product_details')
            found_order_details = list(found_order_details)
            # Get order_details
            for order_detail in found_order_details:
                product_details = order_detail.product_details
                order_detail_qty = order_detail.qty
                product_details_qty = product_details.qty
                product_details_id = str(product_details.id)
                final_qty = product_details_qty + order_detail_qty
                # Go update product details qty
                ProductDetails.objects.filter(id = product_details_id).update(qty = final_qty)
            # Update qty to order detais
        found_order.update(status = order_status)
        return JsonResponse({
            'code': 0,
            'message': 'Update order status successfully'
        })
    except LookupError :
        return JsonResponse({
            'code': -1,
            'message': LookupError.__doc__
        })
            


