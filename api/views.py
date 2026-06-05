from django.contrib.auth import authenticate
from django.core.cache import cache
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from vault.models import Credential

_MAX_ATTEMPTS    = 5
_LOCKOUT_SECONDS = 300


def _get_ip(request):
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR', '')
    return forwarded.split(',')[0].strip() if forwarded else request.META.get('REMOTE_ADDR', '')


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    username = request.data.get('username', '').strip()
    password = request.data.get('password', '')
    if not username or not password:
        return Response({'error': 'Username and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

    ip        = _get_ip(request)
    cache_key = f'api_login_fail_{ip}'
    attempts  = cache.get(cache_key, 0)

    if attempts >= _MAX_ATTEMPTS:
        return Response({'error': 'Too many failed attempts. Please wait 5 minutes.'}, status=status.HTTP_429_TOO_MANY_REQUESTS)

    user = authenticate(username=username, password=password)
    if user:
        cache.delete(cache_key)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'username': user.username})

    cache.set(cache_key, attempts + 1, _LOCKOUT_SECONDS)
    return Response({'error': 'Invalid username or password.'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    request.user.auth_token.delete()
    return Response({'message': 'Logged out.'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_credential(request):
    site_name = request.data.get('site_name', '').strip()
    username  = request.data.get('username', '').strip()
    password  = request.data.get('password', '')
    notes     = request.data.get('notes', '')

    if not site_name or not password:
        return Response({'error': 'site_name and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

    credential = Credential.objects.create(
        owner=request.user,
        site_name=site_name,
        username=username,
        password=password,
        notes=notes,
    )
    return Response({'message': 'Credential saved.', 'id': credential.id}, status=status.HTTP_201_CREATED)
