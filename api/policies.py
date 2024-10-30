from .user.models import UserCustomer
from .jwt_token import jwtToken
from .utils import Obj
class customPermission():
    def is_role_admin(token):
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
        found_user =  UserCustomer.objects.get(id = user_id)
        # Validate user role
        found_user_role = found_user.role
        if(found_user_role != 'admin'):
            return False
        return True
    
    def is_authenticated(token):
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
        user_id = decoded_token_data.get('id', '')
        # Go find user
        found_user =  UserCustomer.objects.get(id = user_id)
        if(Obj.is_empty(found_user)):
            return False
        return True