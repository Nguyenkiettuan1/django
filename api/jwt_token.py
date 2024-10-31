import jwt
import datetime
import pytz

secret_key = 'af922637-a439-4746-974f-1bc3e4550e38'
algorithm = 'HS256'

class jwtToken():
    def generate_token(user_id):
        tz = pytz.timezone("Etc/GMT+7")
        current_time = datetime.datetime.now().replace(tzinfo=tz)
        expiration_time = current_time + datetime.timedelta(minutes=30)
        print(current_time)
        print(expiration_time)
        payload = {
            'uid': user_id,
        }
        token = jwt.encode(payload, secret_key, algorithm=algorithm)
        return token
    
    def verify_token(token):
        try:
            # Init result
            result = {
                "code" : 0,
            }
            # Go decoded token
            decoded_token = jwt.decode(token, secret_key, [algorithm])
            # get token data
            uid = decoded_token.get('uid', '')
            # Validate token still available
            # if decoded_token['exp'] < datetime.datetime.now():
            #     result = {
            #         **result,
            #         "code" : -1,
            #         "message": "Token expired"
            #     }
            # else:
                # return user uid
            result = {
                **result,
                "message": "verify token success fully",
                "data": {
                    "user_id": uid
                }
            }
        except LookupError:
                result =  {
                "code" : -1,
                "message": LookupError
            }
        return result
    