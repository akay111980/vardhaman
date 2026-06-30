from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken, TokenError

def tokenVerified(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Check if the Authorization header is present
        authorization_header = request.headers.get('Authorization')
        if not authorization_header or not authorization_header.startswith('Bearer '):
            return Response({'detail': 'Invalid or missing Authorization header'}, status=status.HTTP_401_UNAUTHORIZED)

        # Extract the token from the Authorization header
        token = authorization_header.split(' ')[1]

        try:
            # Try to decode the token
            decoded_token = AccessToken(token)
            # Additional checks can be added here if needed

        except TokenError as e:
            return Response({'detail': f'Invalid token: {str(e)}'}, status=status.HTTP_401_UNAUTHORIZED)

        # Call the original view function with the validated token
        return view_func(request, *args, **kwargs)

    return _wrapped_view