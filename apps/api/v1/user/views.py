from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from apps.serializers import UserCreateSerializer, UserListSerializer, UserUpdateSerializer, UserInformationSerializer
from django.db import IntegrityError

@api_view(['POST'])
@permission_classes([IsAdminUser])
def create_user(request):
    serializer = UserCreateSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAdminUser])
def modified_create_user(request):
    # Attempt to get 'number' from POST data; default to 0 if not found or invalid
    try:
        number_of_users = int(request.data.get('number', 0))
    except ValueError:
        return Response({'error': 'Please provide a valid integer value for "number".'}, status=status.HTTP_400_BAD_REQUEST)

    if number_of_users < 1:
        return Response({'error': 'Please provide a positive integer value.'}, status=status.HTTP_400_BAD_REQUEST)

    created_users = []
    errors = []
    base_username = 'user'
    last_attempt = 0

    for _ in range(number_of_users):
        user_created = False
        while not user_created:
            last_attempt += 1
            username = f"{base_username}{last_attempt}"
            password = username  # Consider using a more secure password generation method

            if not User.objects.filter(username=username).exists():
                try:
                    user = User.objects.create_user(username=username, password=password)
                    created_users.append(user.username)
                    user_created = True
                except IntegrityError as e:
                    errors.append(f"Failed to create {username}: {str(e)}")
                    # Break from the loop if an unexpected error occurs
                    break

    if created_users:
        return Response({'message': f"Users created successfully: {created_users}"}, status=status.HTTP_201_CREATED)
    else:
        error_message = 'No users were created.'
        if errors:
            error_message += ' ' + ' '.join(errors)
        return Response({'error': error_message}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def list_users(request):
    users = User.objects.filter(is_staff=False)
    serializer = UserListSerializer(users, many=True)
    return Response(serializer.data)

@api_view(['PUT', 'PATCH'])
@permission_classes([IsAdminUser])
def update_user(request, pk):
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

    serializer = UserUpdateSerializer(user, data=request.data, partial=True)  # partial=True allows for partial updates
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAdminUser]) 
def delete_user(request, pk):
    try:
        user = User.objects.get(pk=pk)
        user.delete()
        return Response({'message': 'User deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
    except User.DoesNotExist:
        return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_information(request):
    user = request.user
    serializer = UserInformationSerializer(user)
    return Response(serializer.data)