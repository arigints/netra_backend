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
import subprocess

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
            namespace = f'user{i}'
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

    old_username = user.username
    serializer = UserUpdateSerializer(user, data=request.data, partial=True)  # partial=True allows for partial updates
    if serializer.is_valid():
        serializer.save()
        
        # Check if the username has been updated
        new_username = serializer.data.get('username')
        if old_username != new_username:
            try:
                # Run the subprocess command to update the Kubernetes namespace
                subprocess.run(['kubectl', 'rename', 'namespace', old_username, new_username], check=True)
            except subprocess.CalledProcessError as e:
                return Response({'error': f'Failed to update Kubernetes namespace: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
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

        # Derive namespace, role, and rolebinding names
        namespace = f"{username}"
        role_name = f"{username}-role"
        role_binding_name = f"{username}-rolebinding"

        # First, delete all components for the user
        response = delete_all_components(request, namespace)
        if response != "Success":
            return HttpResponse(response)

        # Then, proceed with deleting the Kubernetes resources
        try:
            subprocess.run(["kubectl", "delete", "rolebinding", role_binding_name, "--namespace", namespace], check=True)
            subprocess.run(["kubectl", "delete", "role", role_name, "--namespace", namespace], check=True)
            subprocess.run(["kubectl", "delete", "namespace", namespace], check=True)
        except subprocess.CalledProcessError as e:
            return Response({'error': f'Failed to delete Kubernetes resources: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from apps.models import UserConfiguration
from django.http import JsonResponse
import subprocess
import yaml

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def compare_cu_config(request):
    user_namespace = f"{request.user.username}"

    # Execute helm get values command
    command = ["helm", "get", "values", "single-cu", "--namespace", user_namespace]
    try:
        helm_output = subprocess.check_output(command, stderr=subprocess.STDOUT)
        values_yaml = helm_output.decode('utf-8')

        # Convert YAML to JSON
        values_json = yaml.safe_load(values_yaml)

        # Extract specific values
        specific_values = {
            'cuId': values_json.get('config', {}).get('cuId', ''),    
            'cellId': values_json.get('config', {}).get('cellId', ''),  
            'f1InterfaceIPadd': values_json.get('multus', {}).get('f1Interface', {}).get('IPadd', ''),
            'f1cuPort': values_json.get('config', {}).get('f1cuPort', ''),
            'f1duPort': values_json.get('config', {}).get('f1duPort', ''),
            'n2InterfaceIPadd': values_json.get('multus', {}).get('n2Interface', {}).get('IPadd', ''),
            'n3InterfaceIPadd': values_json.get('multus', {}).get('n3Interface', {}).get('IPadd', ''),
            'mcc': values_json.get('config', {}).get('mcc', ''),
            'mnc': values_json.get('config', {}).get('mnc', ''),
            'tac': values_json.get('config', {}).get('tac', ''),
            'sst': values_json.get('config', {}).get('sst', ''),
            'amfhost': values_json.get('config', {}).get('amfhost', '')
        }

        # Fetch the user's configuration from the database
        user = request.user
        try:
            user_configuration = UserConfiguration.objects.get(user=user)
        except UserConfiguration.DoesNotExist:
            return Response({"error": "User configuration not found"}, status=status.HTTP_404_NOT_FOUND)

        # Compare the values
        db_values = {
            'cuId': user_configuration.cu_config.cuId,
            'cellId': user_configuration.cu_config.cellId,
            'f1InterfaceIPadd': user_configuration.cu_config.f1InterfaceIPadd,
            'f1cuPort': user_configuration.cu_config.f1cuPort,
            'f1duPort': user_configuration.cu_config.f1duPort,
            'n2InterfaceIPadd': user_configuration.cu_config.n2InterfaceIPadd,
            'n3InterfaceIPadd': user_configuration.cu_config.n3InterfaceIPadd,
            'mcc': user_configuration.cu_config.mcc,
            'mnc': user_configuration.cu_config.mnc,
            'tac': user_configuration.cu_config.tac,
            'sst': user_configuration.cu_config.sst,
            'amfhost': user_configuration.cu_config.amfhost
        }

        matches = {key: specific_values[key] == db_values[key] for key in specific_values.keys()}

        if all(matches.values()):
            return JsonResponse({'status': 'success', 'message': 'All configurations match', 'matches': matches})
        else:
            return JsonResponse({'status': 'failure', 'message': 'Configurations do not match', 'matches': matches})

    except subprocess.CalledProcessError as e:
        return JsonResponse({'error': 'Failed to retrieve Helm release values', 'details': e.output.decode('utf-8')}, status=500)
    except Exception as e:
        return JsonResponse({'error': 'An unexpected error occurred', 'details': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def compare_du_config(request):
    user_namespace = f"{request.user.username}"

    # Execute helm get values command
    command = ["helm", "get", "values", "single-du", "--namespace", user_namespace]
    try:
        helm_output = subprocess.check_output(command, stderr=subprocess.STDOUT)
        values_yaml = helm_output.decode('utf-8')

        # Convert YAML to JSON
        values_json = yaml.safe_load(values_yaml)

        # Extract specific values
        specific_values = {
            'gnbId': values_json.get('config', {}).get('gnbId', ''),   
            'duId': values_json.get('config', {}).get('duId', ''),      
            'cellId': values_json.get('config', {}).get('cellId', ''),
            'f1InterfaceIPadd': values_json.get('multus', {}).get('f1Interface', {}).get('IPadd', ''),
            'f1cuPort': values_json.get('config', {}).get('f1cuPort', ''),
            'f1duPort': values_json.get('config', {}).get('f1duPort', ''),
            'mcc': values_json.get('config', {}).get('mcc', ''),
            'mnc': values_json.get('config', {}).get('mnc', ''),
            'tac': values_json.get('config', {}).get('tac', ''),
            'sst': values_json.get('config', {}).get('sst', ''),
            'usrp': values_json.get('config', {}).get('usrp', ''),
            'cuHost': values_json.get('config', {}).get('cuHost', '')
        }

        # Fetch the user's configuration from the database
        user = request.user
        try:
            user_configuration = UserConfiguration.objects.get(user=user)
        except UserConfiguration.DoesNotExist:
            return Response({"error": "User configuration not found"}, status=status.HTTP_404_NOT_FOUND)

        # Compare the values
        db_values = {
            'gnbId': user_configuration.du_config.gnbId,
            'duId': user_configuration.du_config.duId,
            'cellId': user_configuration.du_config.cellId,
            'f1InterfaceIPadd': user_configuration.du_config.f1InterfaceIPadd,
            'f1cuPort': user_configuration.du_config.f1cuPort,
            'f1duPort': user_configuration.du_config.f1duPort,
            'mcc': user_configuration.du_config.mcc,
            'mnc': user_configuration.du_config.mnc,
            'tac': user_configuration.du_config.tac,
            'sst': user_configuration.du_config.sst,
            'usrp': user_configuration.du_config.usrp,
            'cuHost': user_configuration.du_config.cuHost
        }

        matches = {key: specific_values[key] == db_values[key] for key in specific_values.keys()}

        if all(matches.values()):
            return JsonResponse({'status': 'success', 'message': 'All configurations match', 'matches': matches})
        else:
            return JsonResponse({'status': 'failure', 'message': 'Configurations do not match', 'matches': matches})

    except subprocess.CalledProcessError as e:
        return JsonResponse({'error': 'Failed to retrieve Helm release values', 'details': e.output.decode('utf-8')}, status=500)
    except Exception as e:
        return JsonResponse({'error': 'An unexpected error occurred', 'details': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def compare_ue_config(request):
    user_namespace = f"{request.user.username}"

    # Execute helm get values command
    command = ["helm", "get", "values", "single-ue", "--namespace", user_namespace]
    try:
        helm_output = subprocess.check_output(command, stderr=subprocess.STDOUT)
        values_yaml = helm_output.decode('utf-8')

        # Convert YAML to JSON
        values_json = yaml.safe_load(values_yaml)

        # Extract specific values
        specific_values = {
            'multusIPadd': values_json.get('multus', {}).get('ipadd', ''),
            'rfSimServer': values_json.get('config', {}).get('rfSimServer', ''),
            'fullImsi': values_json.get('config', {}).get('fullImsi', ''),
            'fullKey': values_json.get('config', {}).get('fullKey', ''),
            'opc': values_json.get('config', {}).get('opc', ''),
            'dnn': values_json.get('config', {}).get('dnn', ''),
            'sst': values_json.get('config', {}).get('sst', ''),
            'sd': values_json.get('config', {}).get('sd', ''),
            'usrp': values_json.get('config', {}).get('usrp', '')
        }

        # Fetch the user's configuration from the database
        user = request.user
        try:
            user_configuration = UserConfiguration.objects.get(user=user)
        except UserConfiguration.DoesNotExist:
            return Response({"error": "User configuration not found"}, status=status.HTTP_404_NOT_FOUND)

        # Compare the values
        db_values = {
            'multusIPadd': user_configuration.ue_config.multusIPadd,
            'rfSimServer': user_configuration.ue_config.rfSimServer,
            'fullImsi': user_configuration.ue_config.fullImsi,
            'fullKey': user_configuration.ue_config.fullKey,
            'opc': user_configuration.ue_config.opc,
            'dnn': user_configuration.ue_config.dnn,
            'sst': user_configuration.ue_config.sst,
            'sd': user_configuration.ue_config.sd,
            'usrp': user_configuration.ue_config.usrp
        }

        matches = {key: specific_values[key] == db_values[key] for key in specific_values.keys()}

        if all(matches.values()):
            return JsonResponse({'status': 'success', 'message': 'All configurations match', 'matches': matches})
        else:
            return JsonResponse({'status': 'failure', 'message': 'Configurations do not match', 'matches': matches})

    except subprocess.CalledProcessError as e:
        return JsonResponse({'error': 'Failed to retrieve Helm release values', 'details': e.output.decode('utf-8')}, status=500)
    except Exception as e:
        return JsonResponse({'error': 'An unexpected error occurred', 'details': str(e)}, status=500)