import json
from uuid import UUID
from django.core.files.uploadedfile import SimpleUploadedFile
import datetime
import base64
import os
import random
from PIL import Image
import io
import re
class Obj():
    def is_empty(obj):
        if isinstance(obj, dict):
            return not bool(obj)
        elif isinstance(obj, (list, tuple)):
            return not len(obj) > 0
        else:
            return False
        
class Int():
    def is_int(value):
        try:
            int(value)
            return True
        except ValueError:
            return False   

class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj):
            # if the obj is uuid, we simply return the value of uuid
            return obj.hex
        return json.JSONEncoder.default(self, obj)
    
class Date():
    def validate_date_format(date_string):
        try:
            datetime.datetime.strptime(date_string, '%Y-%m-%d')
            return True
        except ValueError:
            return False
        
class ImageProcessing():
    def base64_to_image(image_data, file_path):
        try:
            # Split the Base64 data into header and actual data
            header, base64_data = image_data.split(",", 1)
            # Extract the file extension from the header
            extension = header.split(";")[0].split("/")[1]
            # Decode the Base64 string
            decoded_data = base64.b64decode(base64_data)
            # Generate a unique file name using the current timestamp
            now = str(datetime.datetime.now().timestamp())
            file_name = f"{now}-{random.randint(1, 100)}.{extension}"
            # Build the full file path
            full_file_path = os.path.join(file_path, file_name)
            # Write the decoded data to the file
            with open(full_file_path, 'wb') as f:
                f.write(decoded_data)
            return full_file_path  # Return the path of the saved image file
        except Exception as e:
            print(f"Error: {e}")
            return None
        