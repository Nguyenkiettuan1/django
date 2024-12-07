from rest_framework import viewsets
from .models import Product, ProductDetails, Color, Size, feedback
from .serializers import ProductSerializer, ProductDetailsSerializer, ColorSerializer, SizeSerializer, FeedBackSerializer
from rest_framework.permissions import AllowAny
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.forms.models import model_to_dict
import json
from ..policies import customPermission
from .models import Product, ProductDetails, Color, Size, Material, Type, ProductMaterials, ProductTypes,product_config, product_details_config, color_config, product_colors_config, size_config, product_sizes_config, material_config, product_materials_config, type_config, product_types_config
from ..utils import Obj, Int, UUIDEncoder, ImageProcessing
import os
# ViewSet for Product
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

# ViewSet for ProductDetails
class ProductDetailsViewSet(viewsets.ModelViewSet):
    queryset = ProductDetails.objects.all()
    serializer_class = ProductDetailsSerializer
    permission_classes = [AllowAny]

# ViewSet for Color
class ColorViewSet(viewsets.ModelViewSet):
    queryset = Color.objects.all()
    serializer_class = ColorSerializer
    permission_classes = [AllowAny]

# ViewSet for Size
class SizeViewSet(viewsets.ModelViewSet):
    queryset = Size.objects.all()
    serializer_class = SizeSerializer
    permission_classes = [AllowAny]
    
class feedback_viewset(viewsets.ModelViewSet):
    queryset = feedback.objects.all()
    serializer_class = FeedBackSerializer
    permission_classes = [AllowAny]

# --------- PRODUCT ---------
@csrf_exempt
def add_product(request):
    if not request.method == 'POST':
        return JsonResponse({'error': 'Send a valid POST request'})
    # Get header value
    header_value = request.headers or {}
    token = header_value.get('Authorization', '')
    # Get body value
    raw_data = request.body.decode('utf-8')
    data = json.loads(raw_data)
    # Only product value
    product_name = data.get('name', '')
    product_price = data.get('price', 0)
    product_status = data.get('status', '')
    product_description = data.get('description', '')
    product_images = data.get('images', [])
    # get relation data
    product_types = data.get('types', [])
    product_materials = data.get('materials', [])
    product_details = data.get('details', [])
    try:
        # Validate authen
        if not customPermission.is_role_admin(request, token):
            return JsonResponse({
                'code': -1,
                'message': "User dont't have permission to access this action"
            })
        # Go validate product field
        if product_name == '':
            return JsonResponse({
                'code': -1,
                'message': "Product name is required"
            })
        else:
            # found product by name
            found_products = Product.objects.filter(name__iexact = product_name).first() or {}
            if(found_products != {}):
                # Parse to dict
                found_products = model_to_dict(found_products)
                # Validate product
                if not Obj.is_empty(found_products):
                    return JsonResponse({
                        'code': -1,
                        'message': "Product name is exited"
                })
        # Validate product price
        if not isinstance(product_price, (int, float)):
                return JsonResponse({
                    'code': -1,
                    'message': "Product price is required or must be a number"
                })
        else:
            if product_price < 0:
                return JsonResponse({
                    'code': -1,
                    'message': "Product price must be positive integer"
                })
        # parse float product price
        product_price = float(product_price)
        if product_status != '':
            if not product_status in list(product_config.get('status', {}).values()):
                return JsonResponse({
                    'code': -1,
                    'message': "Status value does not support"
                })
        else:    
            product_status = product_config.get('status').get('ACTIVE')
        #  Validate type
        validated_types = {}
        types_name = []
        for type in product_types:
            if validated_types.get(type, {}) != {}:
                return JsonResponse({
                    'code': -1,
                    'message': "Duplicate product type value"
                })
            found_type = {}
            try:
                found_type = Type.objects.get(id = type)
            except Type.DoesNotExist:
                  return JsonResponse({
                    'code': -1,
                    'message': "Invalid type value"
                })
            types_name.append(model_to_dict(found_type).get('name', ''))
            validated_types[type] = found_type
        # Validate material 
        validated_materials = {}
        materials_name = []
        for material in product_materials:
            if validated_materials.get(material, {}) != {}:
                return JsonResponse({
                    'code': -1,
                    'message': "Duplicate product material value"
                })
            found_material = {}
            try:
                found_material = Material.objects.get(id = material)
            except Material.DoesNotExist:
                 return JsonResponse({
                    'code': -1,
                    'message': "Invalid material value"
                })
            materials_name.append(model_to_dict(found_material).get('name', ''))
            validated_materials[material] = found_material
        # Validate product details 
        validated_details = []
        validated_color = {}
        validated_size = {}
        for detail in product_details:
            color_id = detail.get('color', '')
            size_id = detail.get('size', '')
            qty = detail.get('qty', 0)
            if f'{color_id}-{size_id}' in validated_details:
                return JsonResponse({
                    'code': -1,
                    'message': "Duplicate product details value"
                })
            # Validate color
            found_color = {}
            try:
                found_color = Color.objects.get(id=color_id)
            except Color.DoesNotExist:
                return JsonResponse({
                    'code': -1,
                    'message': "Color not found or missing value"
                })
            # Validate size
            found_size = {}
            try:
                found_size = Size.objects.get(id=size_id)
            except Size.DoesNotExist:
                return JsonResponse({
                    'code': -1,
                    'message': "Size not found or missing value"
                })
            # Validate qty
            if not isinstance(qty, int):
                return JsonResponse({
                    'code': -1,
                    'message': "Qty must be a number"
                })
            else:
                if qty < 0:
                    return JsonResponse({
                    'code': -1,
                    'message': "Qty must be positive integer"
                })
            validated_details.append(f'{color_id}-{size_id}')
            validated_color[color_id] = found_color
            validated_size[size_id] = found_size
        written_images = []
        if not Obj.is_empty(product_images):
            for image in product_images:
                write_image = ImageProcessing.base64_to_image(image, 'img/product')
                written_images.append(write_image)
        # Go create product
        create_product = Product.objects.create(
            name = product_name,
            price = product_price,
            status = product_status,
            description = product_description,
            image = written_images
        )
        product_info = model_to_dict(create_product)
        # Go create product details 
        created_product_details = []
        for detail in product_details:
            color_id = detail.get('color', '')
            size_id = detail.get('size', '')
            qty = detail.get('qty', 0)
            #  create
            create_product_details = ProductDetails.objects.create(
                product = create_product,
                color = validated_color.get(color_id),
                size = validated_size.get(size_id),
                qty = qty
            )
            # add ro list
            created_product_details.append({
                    **model_to_dict(create_product_details),
                    "color": model_to_dict(validated_color.get(color_id)).get('name'),
                    "size": model_to_dict(validated_size.get(size_id)).get('name')
                })
        # Create product materials
        created_product_materials = []
        for material in product_materials:
            #  create
            create_product_materials = ProductMaterials.objects.create(
                product = create_product,
                material = validated_materials.get(material)
            )
            # add ro list
            created_product_materials.append(model_to_dict(create_product_materials))
        # Create product types
        created_product_types = []
        for type in product_types:
            #  create
            create_product_types = ProductTypes.objects.create(
                product = create_product,
                type = validated_types.get(type)
            )
            # add ro list
            created_product_types.append(model_to_dict(create_product_types))
        return JsonResponse({
                'code': 0,
                'message': "Create product successfully",
                'data':{
                    **product_info,
                    "details": created_product_details,
                    "type": types_name,
                    "material": materials_name
                }
            })
    except LookupError :
        return JsonResponse({
            'code': -1,
            'message': LookupError.__doc__
        })
    
@csrf_exempt
def edit_product(request):
    if not request.method == 'PUT':
        return JsonResponse({'error': 'Send a valid PUT request'})
    # Get header value
    header_value = request.headers or {}
    token = header_value.get('Authorization', '')
    # Get body value
    raw_data = request.body.decode('utf-8')
    data = json.loads(raw_data)
    # Only product value
    product_id = data.get('id', '')
    product_name = data.get('name', '')
    product_price = data.get('price', '')
    product_status = data.get('status', '')
    product_description = data.get('description', '')
    # get relation data
    add_product_types = data.get('addTypes', [])
    add_product_materials = data.get('addMaterials', [])
    delete_product_types = data.get('deleteTypes', [])
    delete_product_materials = data.get('deleteMaterials', [])
    add_product_images = data.get('addImages', [])
    delete_product_images = data.get('deleteImages', [])
    try:
        # Validate authen
        if not customPermission.is_role_admin(request, token):
            return JsonResponse({
                'code': -1,
                'message': "User dont't have permission to access this action"
            })
        # Validate product by id
        if product_id == '':
            return JsonResponse({
                    'code': -1,
                    'message': "id is required"
                })
        found_product = {}
        try:
                found_product = Product.objects.get(id = product_id)
        except Product.DoesNotExist:
                 return JsonResponse({
                    'code': -1,
                    'message': "Product not found"
                })
        # Init prepared_product_update
        prepared_product_update = {}
        # Go validate product field
        if product_name != '':
            # found product by name
            found_products = Product.objects.filter(name__iexact = product_name).first() or {}
            if found_products != {}:
                # parse found_products
                found_products = model_to_dict(found_products)
                if str(found_products.get('id')) != product_id:
                    return JsonResponse({
                        'code': -1,
                        'message': f'Product {product_name} is existed'
                    })
            prepared_product_update['name'] = product_name
        # Validate product price
        if product_price != '':
            if not isinstance(product_price, (int, float)):
                return JsonResponse({
                    'code': -1,
                    'message': "Product must be a number"
                })
            else:
                if product_price < 0:
                    return JsonResponse({
                        'code': -1,
                        'message': "Product price must be positive integer"
                    })
            # parse float product price
            prepared_product_update['price'] = float(product_price)
        # Validate product status
        if product_status != '':
            if not product_status in list(product_config.get('status', {}).values()):
                return JsonResponse({
                    'code': -1,
                    'message': "Status value does not support"
                })
            prepared_product_update['status'] = product_status
        # Product description
        if product_description != '':
            prepared_product_update['description'] = product_description

        existed_product_types = []
        valided_add_type = {}
        product_types_name = {}
        # Go found all product
        if not Obj.is_empty(add_product_types) or not Obj.is_empty(delete_product_types):
            found_all_product_types = list(ProductTypes.objects.filter(product = product_id).select_related('type'))
            # parse all
            for product_type in found_all_product_types:
                tmp_dict = model_to_dict(product_type)
                tmp_type = model_to_dict(product_type.type)
                tmp_type_id = str(tmp_type.get('id'))
                existed_product_types.append(tmp_type_id)
                product_types_name[tmp_type_id] = tmp_type.get('name')
        # Validate add_product_types
        if not Obj.is_empty(add_product_types):
            for type in add_product_types:
                # validate exited type
                if type in existed_product_types:
                    return JsonResponse({
                        'code': -1,
                        'message': "Type is duplicated"
                    })
                # Go found type
                found_type = {}
                try:
                    found_type = Type.objects.get(id = type)
                except Type.DoesNotExist:
                  return JsonResponse({
                        'code': -1,
                        'message': "Type not found"
                    })
                existed_product_types.append(type)
                valided_add_type[type] = found_type
                product_types_name[type] = model_to_dict(found_type).get('name')
        # Validate delete_product_types
        if not Obj.is_empty(delete_product_types):
            for type in delete_product_types:
                # validate exited type
                if not type in existed_product_types:
                    return JsonResponse({
                        'code': -1,
                        'message': "This product type not exited"
                    })
                product_types_name.pop(type)
        # Validate material
        existed_product_materials = []
        valided_add_material = {}
        product_materials_name = {}
        # Go found all product
        if not Obj.is_empty(add_product_materials) or not Obj.is_empty(delete_product_materials):
            found_all_product_materials = list(ProductMaterials.objects.filter(product = product_id).select_related('material'))
            # parse all
            for product_material in found_all_product_materials:
                tmp_material = model_to_dict(product_material.material)
                tmp_material_id = str(tmp_material.get('id'))
                existed_product_materials.append(tmp_material_id)
                product_materials_name[tmp_material_id] = tmp_material.get('name')

        # Validate add_product_materials
        if not Obj.is_empty(add_product_materials):
            for material in add_product_materials:
                # validate exited material
                if material in existed_product_materials:
                    return JsonResponse({
                        'code': -1,
                        'message': "Material is duplicated"
                    })
                # Go found material
                found_material = {}
                try:
                 found_material = Material.objects.get(id = material)
                except Material.DoesNotExist:
                  return JsonResponse({
                        'code': -1,
                        'message': "Material not found"
                    })
            
                existed_product_materials.append(material)
                valided_add_material[material] = found_material
                product_materials_name[material] = model_to_dict(found_material).get('name')

        # Validate delete_product_materials
        if not Obj.is_empty(delete_product_materials):
            for material in delete_product_materials:
                # validate exited material
                if not material in existed_product_materials:
                    return JsonResponse({
                        'code': -1,
                        'message': "This product material not exited"
                    })
                product_materials_name.pop(material)
        written_images = found_product.image
        if not Obj.is_empty(add_product_images):
            for image in add_product_images:
                write_image = ImageProcessing.base64_to_image(image, 'img/product')
                written_images.append(write_image)
        if not Obj.is_empty(delete_product_images):
            written_images = [img for img in written_images if img not in delete_product_images]
            for delete_img in delete_product_images:
                os.remove(delete_img)
        if not Obj.is_empty(add_product_images) or not Obj.is_empty(delete_product_images):
            prepared_product_update['image'] = written_images
        # Go update all value
        if (Obj.is_empty(prepared_product_update) 
            and Obj.is_empty(add_product_types)
            and Obj.is_empty(delete_product_types)
            and Obj.is_empty(add_product_materials)
            and Obj.is_empty(delete_product_materials)
            ):
            return JsonResponse({
                        'code': -1,
                        'message': "Don't have value to update"
                    })
        # Go add more product type info
        if not Obj.is_empty(add_product_types):
            for type in add_product_types:
                ProductTypes.objects.create(
                    product = found_product,
                    type = valided_add_type.get(type)
                )
        # delete product type
        if not Obj.is_empty(delete_product_types):
            for type in delete_product_types:
                ProductTypes.objects.filter(
                    product = product_id,
                    type = type
                ).delete()
        # Go add more product material info
        if not Obj.is_empty(add_product_materials):
            for material in add_product_materials:
                ProductMaterials.objects.create(
                    product = found_product,
                    material = valided_add_material.get(material)
                )
        # delete product material
        if not Obj.is_empty(delete_product_materials):
            for material in delete_product_materials:
                ProductMaterials.objects.filter(
                    product = product_id,
                    material = material
                ).delete()
        # Go update product info
        if not Obj.is_empty(prepared_product_update):
            Product.objects.filter(id = product_id).update(**prepared_product_update)
        # Get product info after update
        product_info = Product.objects.filter(id = product_id).first() or {}
        product_info = model_to_dict(product_info)
        # parse to list
        if Obj.is_empty(product_types_name):
            product_types_name = []
        else:
            product_types_name = list(product_types_name.values())
        if Obj.is_empty(product_materials_name):
            product_materials_name = []
        else:
            product_materials_name = list(product_materials_name.values())
        return JsonResponse({
                'code': 0,
                'message': "Create product successfully",
                'data':{
                    **product_info,
                    "type": product_types_name,
                    "material": product_materials_name
                }
            })
    except LookupError :
        return JsonResponse({
            'code': -1,
            'message': LookupError.__doc__
        })

@csrf_exempt
def product_info(request):
    if not request.method == 'GET':
        return JsonResponse({'error': 'Send a valid GET request'})
    # Get header value
    header_value = request.headers or {}
    token = header_value.get('Authorization', '')
    # Get param
    params_value = request.GET or {}
    product_id = params_value.get('id', '')
    # init is admin
    is_admin = False
    try:
        # Set is admin if had token
        if token != '':
            is_admin = customPermission.is_role_admin(request, token)
        if product_id == '':
            return JsonResponse({
                'code': -1,
                'message': "Product id is required"
            })
        # Go found product
        found_product = Product.objects.filter(id = product_id).first() or {}
        # Throw error if product not found
        if found_product == {}:
            return JsonResponse({
                'code': -1,
                'message': "Product not found"
            })
        # parse to dict
        found_product = model_to_dict(found_product)
        # Init prepared product details
        prepared_product_details = {
            'product': product_id
        }
        # Detect to only active details if user is not admin
        if not is_admin:
            prepared_product_details['status__in'] = [product_details_config.get('status').get('ACTIVE')]
        # Go found product details
        found_product_details =  ProductDetails.objects.filter(**prepared_product_details).select_related('size', 'color') or {}
        # Parse to list
        found_product_details = list(found_product_details)
        parsed_product_details = []
        # Init total_qty
        total_qty = 0
        # Parse detail info
        for detail in found_product_details:
            tmp_product_detail = model_to_dict(detail)
            tmp_product_detail.pop('product')
            tmp_product_detail_qty = tmp_product_detail.get('qty', 0)
            tmp_color_info = model_to_dict(detail.color)
            tmp_size_info = model_to_dict(detail.size)
            parsed_product_details.append({
                **tmp_product_detail,
                "id": str(tmp_product_detail.get('id')),
                "color": {
                    "id": str(tmp_color_info.get('id')),
                    "name": tmp_color_info.get('name')
                },
                "size": {
                    "id": str(tmp_size_info.get('id')),
                    "name": tmp_size_info.get('name')
                }
            })
            total_qty += tmp_product_detail_qty
        # Return resp
        return JsonResponse({
                'code': 0,
                'message': "Get product info successfully",
                'data': {
                    **found_product,
                    'totalQty': total_qty,
                    'details': parsed_product_details
                }
            })
    except LookupError :
        return JsonResponse({
            'code': -1,
            'message': LookupError.__doc__
        })

@csrf_exempt
def get_list_product(request):
    if not request.method == 'GET':
        return JsonResponse({'error': 'Send a valid GET request'})
        # Get header value
    header_value = request.headers or {}
    token = header_value.get('Authorization', '')
    # Get param
    params_value = request.GET or {}
    product_id = params_value.get('id', '')
    product_name = params_value.get('name', '')
    product_from_price = params_value.get('price[from]', '')
    product_to_price = params_value.get('price[to]', '')
    product_status = params_value.get('status', '')
    # Reference param
    parse_params = dict(params_value)
    product_types = parse_params.get('types[]', [])
    product_materials = parse_params.get('materials[]', [])
    product_sizes = parse_params.get('sizes[]', [])
    product_colors = parse_params.get('colors[]', [])

    # Pagination
    page = int(params_value.get('page', 0))
    limit = int(params_value.get('limit', 10))
    offset = page * limit
    # init is admin
    is_admin = False
    try:
        # Set is admin if had token
        if token != '':
            is_admin = customPermission.is_role_admin(request, token)
        # Init preparedQuery
        prepared_query = {}
         # Detect to only active product if user is not admin
        if not is_admin:
            prepared_query['status__in'] = [product_details_config.get('status').get('ACTIVE')]
        else:
            if product_status != '':
                if not product_status in list(product_config.get('status', {}).values()):
                    return JsonResponse({
                        'code': -1,
                        'message': "Status value does not support"
                    })
                prepared_query['status'] = product_status
        if product_id != '':
            prepared_query['id'] = product_id
        if product_name != '':
            prepared_query["name__icontains"] = product_name
        if product_from_price != '':
            # safe parse
            try:
                product_from_price = float(product_from_price)
                if product_from_price < 0:
                    return JsonResponse({
                        'code': -1,
                        'message': "Product price must be a positive integer"
                    }, status=200)
                prepared_query['price__gte'] = product_from_price
            except ValueError:
                return JsonResponse({
                    'code': -1,
                    'message': "Product price must be a number"
                }, status=200)
        if product_to_price != '':
            # safe parse
            product_to_price = float(product_to_price)
            if not isinstance(product_to_price, (int, float)):
                return JsonResponse({
                    'code': -1,
                    'message': "Product price must be a number"
                })
            else:
                if product_to_price < 0:
                    return JsonResponse({
                        'code': -1,
                        'message': "Product price must be a positive integer"
                    })
            prepared_query['price__lte'] = product_to_price
        product_types_ids = []
        product_materials_ids = []
        if not Obj.is_empty(product_types):
            # Loop go found ProductTypes
            found_product_types = ProductTypes.objects.filter(
                type__in = product_types
            ).values('product')
            # parse to list
            found_product_types = list(found_product_types)
            for product_type in found_product_types:
                product_types_ids.append(str(product_type.get('product')))
        
        if not Obj.is_empty(product_materials):
            # Loop go found ProductMaterials
            found_product_materials = ProductMaterials.objects.filter(
                material__in = product_materials
            ).values('product')
            # parse to list
            found_product_materials = list(found_product_materials)
            for product_material in found_product_materials:
                product_materials_ids.append(str(product_material.get('product')))

        # Init merge product ids
        product_ids = []
        if not Obj.is_empty(product_types) and not Obj.is_empty(product_materials):
            product_ids = set(product_types_ids).intersection(product_materials_ids)
        else:
            if not Obj.is_empty(product_types):
                product_ids = product_types_ids
            if not Obj.is_empty(product_materials):
                product_ids = product_materials_ids
        
        # Add product id to prepared query
        if (not Obj.is_empty(product_types) or 
            not Obj.is_empty(product_materials)
        ):
            prepared_query['id__in'] = product_ids
        found_products = Product.objects.filter(**prepared_query)
        # Count total
        total_count = found_products.count()
        # Paginate
        found_products = list(found_products.values()[offset:offset + limit])
        # Return resp
        return JsonResponse({
                'code': 0,
                'message': "Get list product successfully",
                'data': found_products,
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

# --------- DETAILS ---------
@csrf_exempt
def add_product_details(request):
    global found_color, found_size
    if not request.method == 'POST':
        return JsonResponse({'error': 'Send a valid POST request'})
    # Get header value
    header_value = request.headers or {}
    token = header_value.get('Authorization', '')
    # Get body value
    raw_data = request.body.decode('utf-8')
    data = json.loads(raw_data)
    # Only product value
    product_id = data.get('product', '')
    product_details = data.get('details', [])
    try:
        # Validate authen
        if not customPermission.is_role_admin(request, token):
            return JsonResponse({
                'code': -1,
                'message': "User dont't have permission to access this action"
            })
        # Validate product id
        found_product = Product.objects.filter(id = product_id).first() or {}
        if found_product == {}:
            return JsonResponse({
                    'code': -1,
                    'message': "Product not found"
                })
        # Find all product details
        found_product_details = ProductDetails.objects.filter(product=product_id).values('color', 'size')
        # Parse to list
        validated_details = []
        # Get exited product details
        for detail in found_product_details:
            color_id = detail.get('color', '')
            size_id = detail.get('size', '')
            validated_details.append(f'{color_id}_{size_id}')
        # Get exited product details
        for detail in product_details:
            color_id = detail.get('color', '')
            size_id = detail.get('size', '')
            qty = detail.get('qty', 0)
            # Validate color
            found_color = Color.objects.filter(id = color_id).first() or {}
            if found_color == {}:
                return JsonResponse({
                    'code': -1,
                    'message': "Màu sắc chưa được hỗ trợ"
                })
            # Validate size
            found_size = Size.objects.filter(id = size_id).first() or {}
            if found_size == {}:
                return JsonResponse({
                    'code': -1,
                    'message': "Kích cỡ chưa được hỗ trợ"
                })
            if f'{color_id}_{size_id}' in validated_details:
                return JsonResponse({
                    'code': -1,
                    'message': f"Sản phẩm {found_product.name} với màu săc: {found_color.name} - kích cỡ: {found_size.name} bị trùng lặp"
                })
            # found details
            if not isinstance(qty, int):
                return JsonResponse({
                    'code': -1,
                    'message': "Số lượng phải là con số"
                })
            else:
                if qty < 0:
                    return JsonResponse({
                        'code': -1,
                        'message': "Số lượng phải lớn hơn 0"
                    })
            validated_details.append(f'{color_id}_{size_id}')

        # Go create product details 
        created_product_details = []
        for detail in product_details:
            color_id = detail.get('color', '')
            size_id = detail.get('size', '')
            qty = detail.get('qty', 0)
            found_color = Color.objects.get(id = color_id) or {}
            found_size = Size.objects.get(id = size_id) or {}

            #  create
            create_product_details = ProductDetails.objects.create(
                product = found_product,
                color = found_color,
                size = found_size,
                qty = qty
            )
            # add ro list
            created_product_details.append(model_to_dict(create_product_details))
        return JsonResponse({
                'code': 0,
                'message': "Create product details successfully",
                "data": created_product_details
            })
    except LookupError :
        return JsonResponse({
            'code': -1,
            'message': LookupError.__doc__
        })
    
@csrf_exempt
def edit_product_details(request):
    if not request.method == 'PUT':
        return JsonResponse({'error': 'Send a valid PUT request'})
    # Get header value
    header_value = request.headers or {}
    token = header_value.get('Authorization', '')
    # Get body value
    raw_data = request.body.decode('utf-8')
    data = json.loads(raw_data)
    # Only product value
    product_detail = data.get('id', '')
    product_details_qty = data.get('qty', '')
    product_details_status = data.get('status', '')
    try:
        # Validate authen
        if not customPermission.is_role_admin(request, token):
            return JsonResponse({
                'code': -1,
                'message': "User dont't have permission to access this action"
            })
        # Validate product details id
        found_product_details = ProductDetails.objects.filter(id = product_detail)
        detect_product_details = found_product_details.first() or {}
        if detect_product_details == {}:
            return JsonResponse({
                    'code': -1,
                    'message': "Product details not found"
                })
        # Init prepared update
        prepared_update = {}
        # Validate qty
        if product_details_qty != '':
            if not isinstance(product_details_qty, int):
                return JsonResponse({
                    'code': -1,
                    'message': "Qty must be a number"
                })
            else:
                if product_details_qty < 0:
                    return JsonResponse({
                    'code': -1,
                    'message': "Qty must be positive integer"
                })
            prepared_update['qty'] =  product_details_qty
        if product_details_status != '':
            if not product_details_status in list(product_details_config.get('status', {}).values()):
                    return JsonResponse({
                        'code': -1,
                        'message': "Status value does not support"
                    })
            prepared_update['status'] =  product_details_status
        #  Go update
        found_product_details.update(**prepared_update)
        # Find all product details
        after_update_product_details = ProductDetails.objects.filter(id = product_detail).first()
        # Go convert to object
        product_details_info = model_to_dict(after_update_product_details)
        return JsonResponse({
                'code': 0,
                'message': "Update product details successfully",
                "data": product_details_info
            })
    except LookupError :
        return JsonResponse({
            'code': -1,
            'message': LookupError.__doc__
        })

     
# --------- COLOR ---------
@csrf_exempt
def add_color(request):
    if not request.method == 'POST':
        return JsonResponse({'error': 'Send a valid POST request'})
    # Get header value
    header_value = request.headers or {}
    token = header_value.get('Authorization', '')
    # Get body value
    raw_data = request.body.decode('utf-8')
    data = json.loads(raw_data)
    # Only product value
    color_name = data.get('name', '')
    color_status = data.get('status', '')
    try:
        # Validate authen
        if not customPermission.is_role_admin(request, token):
            return JsonResponse({
                'code': -1,
                'message': "User dont't have permission to access this action"
            })
        if color_name == '':
            return JsonResponse({
                'code': -1,
                'message': "Name is required"
            })
        else:
            # Validate existed color
            found_color = Color.objects.filter(name__iexact = color_name).first() or {}
            if found_color != {}:
                return JsonResponse({
                    'code': -1,
                    'message': f'Color {color_name} is existed'
                })
        if color_status != '':
            if not color_status in list(color_config.get('status', {}).values()):
                return JsonResponse({
                    'code': -1,
                    'message': "Status value does not support"
                })
        else:    
            color_status = color_config.get('status').get('ACTIVE')
        # Go create color
        create_color = Color.objects.create(
            name = color_name,
            status = color_status
        )
        # Parse to dict
        create_color = model_to_dict(create_color)
        return JsonResponse({
                'code': 0,
                'message': "Create color successfully",
                'data': create_color
            })
    except LookupError :
        return JsonResponse({
            'code': -1,
            'message': LookupError.__doc__
        })

@csrf_exempt
def get_list_color(request):
    if not request.method == 'GET':
        return JsonResponse({'error': 'Send a valid GET request'})
    # Get header value
    header_value = request.headers or {}
    token = header_value.get('Authorization', '')
    # Get param
    params_value = request.GET or {}
    color_name = params_value.get('name', '')
    color_status = params_value.get('status', '')
    # Pagination
    page = int(params_value.get('page', 0))
    limit = int(params_value.get('limit', 10))
    offset = page * limit
    # init is admin
    is_admin = False
    try:
        # Set is admin if had token
        if token != '':
            is_admin = customPermission.is_role_admin(request, token)
        # Init preparedQuery
        prepared_query = {}
         # Detect to only active color if user is not admin
        if not is_admin:
            prepared_query['status__in'] = [product_details_config.get('status').get('ACTIVE')]
        else:
            if color_status != '':
                if not color_status in list(color_config.get('status', {}).values()):
                    return JsonResponse({
                        'code': -1,
                        'message': "Status value does not support"
                    })
                prepared_query['status'] = color_status
        # Validate name
        if color_name != '':
            prepared_query['name__icontains'] = color_name
        # Go filter
        found_colors = Color.objects.filter(**prepared_query)
        # Count total
        total_count = found_colors.count()
        # Paginate
        found_colors = list(found_colors.values()[offset:offset + limit])
        return JsonResponse({
            'code': 0,
            'data': found_colors,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total_count
            },
            'message': "Get list color successfully"
        })
    except LookupError :
        return JsonResponse({
            'code': -1,
            'message': LookupError.__doc__
        })
    
@csrf_exempt
def edit_color(request):
    if not request.method == 'PUT':
        return JsonResponse({'error': 'Send a valid PUT request'})
    # Get header value
    header_value = request.headers or {}
    token = header_value.get('Authorization', '')
   # Get body value
    raw_data = request.body.decode('utf-8')
    data = json.loads(raw_data)
    color_id = data.get('id', '')
    color_name = data.get('name', '')
    color_status = data.get('status', '')
    try:
        # Validate authen
        if not customPermission.is_role_admin(request, token):
            return JsonResponse({
                'code': -1,
                'message': "User dont't have permission to access this action"
            })
        # Init where query
        where = {}
        # prepared query
        prepared_update = {}
        # Validate id
        if color_id == '':
            return JsonResponse({
                'code': -1,
                'message': f'Id is required'
            })
        where['id'] = color_id
        # Validate name
        if color_name != '':
            found_color = Color.objects.filter(name__iexact = color_name).first() or {}
            if found_color != {}:
                # parse found_size
                found_color = model_to_dict(found_color)
                if str(found_color.get('id')) != color_id:
                    return JsonResponse({
                        'code': -1,
                        'message': f'Color {color_name} is existed'
                    })
            prepared_update['name'] = color_name
        
        # Validate status
        if color_status != '':
            if not color_status in list(color_config.get('status', {}).values()):
                return JsonResponse({
                    'code': -1,
                    'message': "Status value does not support"
                })
            prepared_update['status'] = color_status
        # Validate prepared update 
        if(Obj.is_empty(prepared_update)):
            return JsonResponse({
                'code': -1,
                'message': "Don't have data to update"
            })
        # Go filter
        found_colors = Color.objects.filter(**where)
        detect_color = found_colors.first() or {}
        if detect_color == {}:
            return JsonResponse({
                'code': -1,
                'message': "Color not found"
            })
        #  Go update
        found_colors.update(**prepared_update)
        # Get user value after update
        after_update_color = Color.objects.filter(**where).first()
        # Go convert to object
        color_info = model_to_dict(after_update_color)
        # Get after update info
        return JsonResponse({
            'code': 0,
            'data': color_info,
            'message': "Update color successfully"
        })
    except LookupError :
        return JsonResponse({
            'code': -1,
            'message': LookupError.__doc__
        })

# ------------------------
# --------- SIZE ---------
# ------------------------
@csrf_exempt
def add_size(request):
    if not request.method == 'POST':
        return JsonResponse({'error': 'Send a valid POST request'})
    # Get header value
    header_value = request.headers or {}
    token = header_value.get('Authorization', '')
    # Get body value
    raw_data = request.body.decode('utf-8')
    data = json.loads(raw_data)
    # Only product value
    size_name = data.get('name', '')
    size_status = data.get('status', '')
    try:
        # Validate authen
        if not customPermission.is_role_admin(request, token):
            return JsonResponse({
                'code': -1,
                'message': "User dont't have permission to access this action"
            })
        if size_name == '':
            return JsonResponse({
                'code': -1,
                'message': "Name is required"
            })
        else:
            # Validate existed size
            found_size = Size.objects.filter(name__iexact = size_name).first() or {}
            if found_size != {}:
                return JsonResponse({
                    'code': -1,
                    'message': f'Size {size_name} is existed'
                })
        if size_status != '':
            if not size_status in list(size_config.get('status', {}).values()):
                return JsonResponse({
                    'code': -1,
                    'message': "Status value does not support"
                })
        else:    
            size_status = size_config.get('status').get('ACTIVE')
        # Go create size
        create_size = Size.objects.create(
            name = size_name,
            status = size_status
        )
        # Parse to dict
        create_size = model_to_dict(create_size)
        return JsonResponse({
                'code': 0,
                'message': "Create size successfully",
                'data': create_size
            })
    except LookupError :
        return JsonResponse({
            'code': -1,
            'message': LookupError.__doc__
        })

@csrf_exempt
def get_list_size(request):
    if not request.method == 'GET':
        return JsonResponse({'error': 'Send a valid GET request'})
    # Get header value
    header_value = request.headers or {}
    token = header_value.get('Authorization', '')
    # Get param
    params_value = request.GET or {}
    size_name = params_value.get('name', '')
    size_status = params_value.get('status', '')
    # Pagination
    page = int(params_value.get('page', 0))
    limit = int(params_value.get('limit', 10))
    offset = page * limit
     # init is admin
    is_admin = False
    try:
        # Set is admin if had token
        if token != '':
            is_admin = customPermission.is_role_admin(request, token)
        # Init preparedQuery
        prepared_query = {}
         # Detect to only active size if user is not admin
        if not is_admin:
            prepared_query['status__in'] = [product_details_config.get('status').get('ACTIVE')]
        else:
            if size_status != '':
                if not size_status in list(size_config.get('status', {}).values()):
                    return JsonResponse({
                        'code': -1,
                        'message': "Status value does not support"
                    })
                prepared_query['status'] = size_status
        # Validate name
        if size_name != '':
            prepared_query['name__icontains'] = size_name
        # Go filter
        found_sizes = Size.objects.filter(**prepared_query)
        # Count total
        total_count = found_sizes.count()
        # Paginate
        found_sizes = list(found_sizes.values()[offset:offset + limit])
        return JsonResponse({
            'code': 0,
            'data': found_sizes,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total_count
            },
            'message': "Get list size successfully"
        })
    except LookupError :
        return JsonResponse({
            'code': -1,
            'message': LookupError.__doc__
        })

@csrf_exempt
def edit_size(request):
    if not request.method == 'PUT':
        return JsonResponse({'error': 'Send a valid PUT request'})
    # Get header value
    header_value = request.headers or {}
    token = header_value.get('Authorization', '')
   # Get body value
    raw_data = request.body.decode('utf-8')
    data = json.loads(raw_data)
    size_id = data.get('id', '')
    size_name = data.get('name', '')
    size_status = data.get('status', '')
    try:
        # Validate authen
        if not customPermission.is_role_admin(request, token):
            return JsonResponse({
                'code': -1,
                'message': "User dont't have permission to access this action"
            })
        # Init where query
        where = {}
        # prepared query
        prepared_update = {}
        # Validate id
        if size_id == '':
            return JsonResponse({
                'code': -1,
                'message': f'Id is required'
            })
        where['id'] = size_id
        # Validate name
        if size_name != '':
            found_size = Size.objects.filter(name__iexact = size_name).first() or {}
            if found_size != {}:
                # parse found_size
                found_size = model_to_dict(found_size)
                if str(found_size.get('id')) != size_id:
                    return JsonResponse({
                        'code': -1,
                        'message': f'Size {size_name} is existed'
                    })
            prepared_update['name'] = size_name
        # Validate status
        if size_status != '':
            if not size_status in list(size_config.get('status', {}).values()):
                return JsonResponse({
                    'code': -1,
                    'message': "Status value does not support"
                })
            prepared_update['status'] = size_status
        # Validate prepared update 
        if(Obj.is_empty(prepared_update)):
            return JsonResponse({
                'code': -1,
                'message': "Don't have data to update"
            })
        # Go filter
        found_sizes = Size.objects.filter(**where)
        detect_size = found_sizes.first() or {}
        if detect_size == {}:
            return JsonResponse({
                'code': -1,
                'message': "Size not found"
            })
        #  Go update
        found_sizes.update(**prepared_update)
        # Get user value after update
        after_update_size = Size.objects.filter(**where).first()
        # Go convert to object
        size_info = model_to_dict(after_update_size)
        # Get after update info
        return JsonResponse({
            'code': 0,
            'data': size_info,
            'message': "Update size successfully"
        })
    except LookupError :
        return JsonResponse({
            'code': -1,
            'message': LookupError.__doc__
        })
# -----------------------------
# --------- Materials ---------
# -----------------------------

@csrf_exempt
def add_material(request):
    if not request.method == 'POST':
        return JsonResponse({'error': 'Send a valid POST request'})
    # Get header value
    header_value = request.headers or {}
    token = header_value.get('Authorization', '')
    # Get body value
    raw_data = request.body.decode('utf-8')
    data = json.loads(raw_data)
    # Only product value
    material_name = data.get('name', '')
    material_status = data.get('status', '')
    try:
        # Validate authen
        if not customPermission.is_role_admin(request, token):
            return JsonResponse({
                'code': -1,
                'message': "User dont't have permission to access this action"
            })
        if material_name == '':
            return JsonResponse({
                'code': -1,
                'message': "Name is required"
            })
        else:
            # Validate existed material
            found_material = Material.objects.filter(name__iexact = material_name).first() or {}
            if found_material != {}:
                return JsonResponse({
                    'code': -1,
                    'message': f'Material {material_name} is existed'
                })
        if material_status != '':
            if not material_status in list(material_config.get('status', {}).values()):
                return JsonResponse({
                    'code': -1,
                    'message': "Status value does not support"
                })
        else:    
            material_status = material_config.get('status').get('ACTIVE')
        # Go create material
        create_material = Material.objects.create(
            name = material_name,
            status = material_status
        )
        # Parse to dict
        create_material = model_to_dict(create_material)
        return JsonResponse({
                'code': 0,
                'message': "Create material successfully",
                'data': create_material
            })
    except LookupError :
        return JsonResponse({
            'code': -1,
            'message': LookupError.__doc__
        })

@csrf_exempt
def get_list_material(request):
    if not request.method == 'GET':
        return JsonResponse({'error': 'Send a valid GET request'})
    # Get header value
    header_value = request.headers or {}
    token = header_value.get('Authorization', '')
    # Get param
    params_value = request.GET or {}
    material_name = params_value.get('name', '')
    material_status = params_value.get('status', '')
    # Pagination
    page = int(params_value.get('page', 0))
    limit = int(params_value.get('limit', 10))
    offset = page * limit
     # init is admin
    is_admin = False
    try:
        # Set is admin if had token
        if token != '':
            is_admin = customPermission.is_role_admin(request, token)
        # Init preparedQuery
        prepared_query = {}
         # Detect to only active material if user is not admin
        if not is_admin:
            prepared_query['status__in'] = [product_details_config.get('status').get('ACTIVE')]
        else:
            if material_status != '':
                if not material_status in list(material_config.get('status', {}).values()):
                    return JsonResponse({
                        'code': -1,
                        'message': "Status value does not support"
                    })
                prepared_query['status'] = material_status
        # Validate name
        if material_name != '':
            prepared_query['name__icontains'] = material_name
        # Go filter
        found_materials = Material.objects.filter(**prepared_query)
        # Count total
        total_count = found_materials.count()
        # Paginate
        found_materials = list(found_materials.values()[offset:offset + limit])
        return JsonResponse({
            'code': 0,
            'data': found_materials,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total_count
            },
            'message': "Get list material successfully"
        })
    except LookupError :
        return JsonResponse({
            'code': -1,
            'message': LookupError.__doc__
        })

@csrf_exempt
def edit_material(request):
    if not request.method == 'PUT':
        return JsonResponse({'error': 'Send a valid PUT request'})
    # Get header value
    header_value = request.headers or {}
    token = header_value.get('Authorization', '')
   # Get body value
    raw_data = request.body.decode('utf-8')
    data = json.loads(raw_data)
    material_id = data.get('id', '')
    material_name = data.get('name', '')
    material_status = data.get('status', '')
    try:
        # Validate authen
        if not customPermission.is_role_admin(request, token):
            return JsonResponse({
                'code': -1,
                'message': "User dont't have permission to access this action"
            })
        # Init where query
        where = {}
        # prepared query
        prepared_update = {}
        # Validate id
        if material_id == '':
            return JsonResponse({
                'code': -1,
                'message': f'Id is required'
            })
        where['id'] = material_id
        # Validate name
        if material_name != '':
            found_material = Material.objects.filter(name__iexact = material_name).first() or {}
            if found_material != {}:
                # parse found_size
                found_material = model_to_dict(found_material)
                if str(found_material.get('id')) != material_id:
                    return JsonResponse({
                        'code': -1,
                        'message': f'Material {material_name} is existed'
                    })
            prepared_update['name'] = material_name
        # Validate status
        if material_status != '':
            if not material_status in list(material_config.get('status', {}).values()):
                return JsonResponse({
                    'code': -1,
                    'message': "Status value does not support"
                })
            prepared_update['status'] = material_status
        # Validate prepared update 
        if(Obj.is_empty(prepared_update)):
            return JsonResponse({
                'code': -1,
                'message': "Don't have data to update"
            })
        # Go filter
        found_materials = Material.objects.filter(**where)
        detect_material = found_materials.first() or {}
        if detect_material == {}:
            return JsonResponse({
                'code': -1,
                'message': "Material not found"
            })
        #  Go update
        found_materials.update(**prepared_update)
        # Get user value after update
        after_update_material = Material.objects.filter(**where).first()
        # Go convert to object
        material_info = model_to_dict(after_update_material)
        # Get after update info
        return JsonResponse({
            'code': 0,
            'data': material_info,
            'message': "Update material successfully"
        })
    except LookupError :
        return JsonResponse({
            'code': -1,
            'message': LookupError.__doc__
        })

# -------------------------
# --------- Types ---------
# -------------------------

@csrf_exempt
def add_type(request):
    if not request.method == 'POST':
        return JsonResponse({'error': 'Send a valid POST request'})
    # Get header value
    header_value = request.headers or {}
    token = header_value.get('Authorization', '')
    # Get body value
    raw_data = request.body.decode('utf-8')
    data = json.loads(raw_data)
    # Only product value
    type_name = data.get('name', '')
    type_status = data.get('status', '')
    try:
        # Validate authen
        if not customPermission.is_role_admin(request, token):
            return JsonResponse({
                'code': -1,
                'message': "User dont't have permission to access this action"
            })
        if type_name == '':
            return JsonResponse({
                'code': -1,
                'message': "Name is required"
            })
        else:
            # Validate existed type
            found_type = Type.objects.filter(name__iexact = type_name).first() or {}
            if found_type != {}:
                return JsonResponse({
                    'code': -1,
                    'message': f'Type {type_name} is existed'
                })
        if type_status != '':
            if not type_status in list(type_config.get('status', {}).values()):
                return JsonResponse({
                    'code': -1,
                    'message': "Status value does not support"
                })
        else:    
            type_status = type_config.get('status').get('ACTIVE')
        # Go create type
        create_type = Type.objects.create(
            name = type_name,
            status = type_status
        )
        # Parse to dict
        create_type = model_to_dict(create_type)
        return JsonResponse({
                'code': 0,
                'message': "Create type successfully",
                'data': create_type
            })
    except LookupError :
        return JsonResponse({
            'code': -1,
            'message': LookupError.__doc__
        })

@csrf_exempt
def get_list_type(request):
    if not request.method == 'GET':
        return JsonResponse({'error': 'Send a valid GET request'})
    # Get header value
    header_value = request.headers or {}
    token = header_value.get('Authorization', '')
    # Get param
    params_value = request.GET or {}
    type_name = params_value.get('name', '')
    type_status = params_value.get('status', '')
    # Pagination
    page = int(params_value.get('page', 0))
    limit = int(params_value.get('limit', 10))
    offset = page * limit
    # init is admin
    is_admin = False
    try:
        # Set is admin if had token
        if token != '':
            is_admin = customPermission.is_role_admin(request, token)
        # Init preparedQuery
        prepared_query = {}
         # Detect to only active type if user is not admin
        if not is_admin:
            prepared_query['status__in'] = [product_details_config.get('status').get('ACTIVE')]
        else:
            if type_status != '':
                if not type_status in list(type_config.get('status', {}).values()):
                    return JsonResponse({
                        'code': -1,
                        'message': "Status value does not support"
                    })
                prepared_query['status'] = type_status
        # Validate name
        if type_name != '':
            prepared_query['name__icontains'] = type_name
        # Validate status
        if type_status != '':
            if not type_status in list(type_config.get('status', {}).values()):
                return JsonResponse({
                    'code': -1,
                    'message': "Status value does not support"
                })
            prepared_query['status'] = type_status
        # Go filter
        found_types = Type.objects.filter(**prepared_query)
        # Count total
        total_count = found_types.count()
        # Paginate
        found_types = list(found_types.values()[offset:offset + limit])
        return JsonResponse({
            'code': 0,
            'data': found_types,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total_count
            },
            'message': "Get list type successfully"
        })
    except LookupError :
        return JsonResponse({
            'code': -1,
            'message': LookupError.__doc__
        })

@csrf_exempt
def edit_type(request):
    if not request.method == 'PUT':
        return JsonResponse({'error': 'Send a valid PUT request'})
    # Get header value
    header_value = request.headers or {}
    token = header_value.get('Authorization', '')
   # Get body value
    raw_data = request.body.decode('utf-8')
    data = json.loads(raw_data)
    type_id = data.get('id', '')
    type_name = data.get('name', '')
    type_status = data.get('status', '')
    try:
        # Validate authen
        if not customPermission.is_role_admin(request, token):
            return JsonResponse({
                'code': -1,
                'message': "User dont't have permission to access this action"
            })
        # Init where query
        where = {}
        # prepared query
        prepared_update = {}
        # Validate id
        if type_id == '':
            return JsonResponse({
                'code': -1,
                'message': f'Id is required'
            })
        where['id'] = type_id
        # Validate name
        if type_name != '':
            found_type = Type.objects.filter(name__iexact = type_name).first() or {}
            if found_type != {}:
                # parse found_size
                found_type = model_to_dict(found_type)
                if str(found_type.get('id')) == type_id:
                    return JsonResponse({
                        'code': -1,
                        'message': f'Type {type_name} is existed'
                    })
            prepared_update['name'] = type_name
        # Validate status
        if type_status != '':
            if not type_status in list(type_config.get('status', {}).values()):
                return JsonResponse({
                    'code': -1,
                    'message': "Status value does not support"
                })
            prepared_update['status'] = type_status
        # Validate prepared update 
        if(Obj.is_empty(prepared_update)):
            return JsonResponse({
                'code': -1,
                'message': "Don't have data to update"
            })
        # Go filter
        found_types = Type.objects.filter(**where)
        detect_type = found_types.first() or {}
        if detect_type == {}:
            return JsonResponse({
                'code': -1,
                'message': "Type not found"
            })
        #  Go update
        found_types.update(**prepared_update)
        # Get user value after update
        after_update_type = Type.objects.filter(**where).first()
        # Go convert to object
        type_info = model_to_dict(after_update_type)
        # Get after update info
        return JsonResponse({
            'code': 0,
            'data': type_info,
            'message': "Update type successfully"
        })
    except LookupError :
        return JsonResponse({
            'code': -1,
            'message': LookupError.__doc__
        })
