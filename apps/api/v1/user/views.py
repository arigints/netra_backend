from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from apps.serializers import UserCreateSerializer, UserListSerializer, UserUpdateSerializer, UserInformationSerializer
from django.db import IntegrityError, transaction
from kubernetes import client, config
import re
from apps.models import UserProfile
from apps.kube_utils import get_role_yaml, get_role_binding_yaml
import subprocess
from apps.api.v1.oai.views import create_all_components, delete_all_components

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

    config.load_kube_config() 
    api_instance = client.CoreV1Api()
    rbac_api_instance = client.RbacAuthorizationV1Api()

    try:
        user_count = int(request.data.get('number', 0))
        user_count = max(user_count, 1)  # Ensure at least one user is created

        highest_number = 0
        created_users = []  # Track successfully created users

        # Find the highest existing username number
        for user in User.objects.filter(username__startswith='user'):
            match = re.match(r'user(\d+)', user.username)
            if match:
                number = int(match.group(1))
                highest_number = max(highest_number, number)

        # Start creating users from the next available number
        for i in range(highest_number + 1, highest_number + user_count + 1):
            username = f'user{i}'
            password = f'user{i}'
            namespace = f'user{i}-namespace'
            role_name = f'user{i}-role'
            role_binding_name = f'user{i}-rolebinding'

            if not User.objects.filter(username=username).exists():
                try:
                    with transaction.atomic():
                        new_user = User.objects.create_user(username=username, password=password)
                        UserProfile.objects.get_or_create(user=new_user, defaults={'level': 1, 'completion': 0.0})
                    
                        # Create the user's namespace
                        subprocess.run(["kubectl", "create", "namespace", namespace])

                        # Generate the role and role binding YAML
                        role_yaml = get_role_yaml(namespace, role_name)
                        role_binding_yaml = get_role_binding_yaml(namespace, role_binding_name, username, role_name)

                        # Apply the role and role binding
                        subprocess.run(["kubectl", "apply", "-f", "-"], input=role_yaml.encode('utf-8'))
                        subprocess.run(["kubectl", "apply", "-f", "-"], input=role_binding_yaml.encode('utf-8'))

                        response = create_all_components(request, namespace)
                        if response != "Success":
                            return HttpResponse(response)

                        created_users.append(username)
                except IntegrityError as e:
                    return Response({'error': f"Failed to create {username}: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': f"Users created successfully: {created_users}"}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'error': f"An error occurred: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

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
    config.load_kube_config()
    api_instance = client.CoreV1Api()

    try:
        user = User.objects.get(pk=pk)
        username = user.username

        # Assume the namespace, role, and rolebinding follow a specific naming convention
        namespace = f"{username}-namespace"
        role_name = f"{username}-role"
        role_binding_name = f"{username}-rolebinding"

        try:
            # Delete the rolebinding
            subprocess.run(["kubectl", "delete", "rolebinding", role_binding_name, "--namespace", namespace])
        except ApiException as e:
            return Response({'error': f'Failed to delete rolebinding: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            # Delete the role
            subprocess.run(["kubectl", "delete", "role", role_name, "--namespace", namespace])
        except ApiException as e:
            return Response({'error': f'Failed to delete role: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            # Delete the namespace
            subprocess.run(["kubectl", "delete", "namespace", namespace])
        except ApiException as e:
            return Response({'error': f'Failed to delete namespace: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        response = delete_all_components(request, namespace)
        if response != "Success":
            return HttpResponse(response)

        # Delete the user after cleaning up associated resources
        user.delete()

        return Response({'message': 'User and associated Kubernetes resources deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
    except User.DoesNotExist:
        return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_information(request):
    user = request.user
    serializer = UserInformationSerializer(user)
    return Response(serializer.data)