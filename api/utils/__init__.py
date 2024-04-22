from rest_framework.views import exception_handler
from rest_framework import status


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)
    try:
        if response.status_code == 401:
            response.data.pop('detail')
            if 'messages' in response.data:
                response.data.pop('messages')
            response.data['data'] = None
            response.data['code'] = 401
            response.data['message'] = "Invalid or Expired Token"
    except:
        pass
    return response
