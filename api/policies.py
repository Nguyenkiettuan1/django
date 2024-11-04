from .user.models import UserCustomer, user_config
from django.forms.models import model_to_dict
from .jwt_token import jwtToken
from .utils import Obj
import json
class customPermission():
    def is_role_admin(request, token):
        if(token == ''):
            return False
        # Extract token
        extract_token = token.split('Bearer ')[1]
        # Go decode by extract_token
        decoded_token = jwtToken.verify_token(extract_token)
        # validate decoded action
        if(decoded_token['code'] != 0):
            return False
        decoded_token_data = decoded_token.get('data', {})
        user_id = decoded_token_data.get('user_id', '')
        # Go find user
        found_user =  UserCustomer.objects.filter(id = user_id).first()
        # Validate user role
        found_user_role = found_user.role
        if(found_user_role != user_config.get('role', {}).get('ADMIN', 'admin')):
            return False
        return True
    
    def is_role_admin_or_staff(request, token):
        if(token == ''):
            return False
        # Extract token
        extract_token = token.split('Bearer ')[1]
        # Go decode by extract_token
        decoded_token = jwtToken.verify_token(extract_token)
        # validate decoded action
        if(decoded_token['code'] != 0):
            return False
        decoded_token_data = decoded_token.get('data', {})
        user_id = decoded_token_data.get('user_id', '')
        # Go find user
        found_user =  UserCustomer.objects.filter(id = user_id).first()
        # Validate user role
        found_user_role = found_user.role
        if not found_user_role in [user_config.get('role', {}).get('ADMIN', 'admin'), 
                                   user_config.get('role', {}).get('STAFF', 'staff')]:
            return False
        return True
    
    def is_authenticated(request, token):
        if(token == ''):
            return False
        # Extract token
        extract_token = token.split('Bearer ')[1]
        # Go decode by extract_token
        decoded_token = jwtToken.verify_token(extract_token)
        # validate decoded action
        if(decoded_token['code'] != 0):
            return False
        decoded_token_data = decoded_token.get('data', {})
        user_id = decoded_token_data.get('user_id', '')
        request.content_params['uid'] = user_id
        # Go find user
        go_found_user =  UserCustomer.objects.filter(id = user_id).first()
        found_user = model_to_dict(go_found_user)
        if(Obj.is_empty(found_user)):
            return False
        return True