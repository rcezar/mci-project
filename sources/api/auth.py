from mci.models import MCIUser
from rest_framework.response import Response
from django.http import HttpResponse
from rest_framework import status, serializers
from base64 import b64decode
from django.contrib.auth import authenticate


class MCIAuthenticationMiddleware(object):
    def process_request(self, request):
        if request.path.startswith('/api/'):
            try:
                enc_user = request.META['HTTP_AUTHORIZATION'].split()[1]
                username, password = b64decode(enc_user).split(':')
                print username, password
                user = authenticate(username=username, password=password)

                if user is None:
                    response = HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content_type='application/json')
                    response['WWW-Authenticate'] = 'Basic realm="MCI RESTful API"'
                    response.content = '{info: "Invalid user or password", success: false}'
                    return response
                else:
                    request.api_user = user

                # comment
            except KeyError, IndexError:
                response = HttpResponse(status=status.HTTP_401_UNAUTHORIZED, content_type='application/json')
                response['WWW-Authenticate'] = 'Basic realm="MCI RESTful API"'
                response.content = '{info: "Please use basic authentication", success: false}'
                return response