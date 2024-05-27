from kubernetes import client, config
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import json
from django.http import JsonResponse
import subprocess
from rest_framework import status
from apps.models import UserProfile

def get_network_status_annotations():
    # Load your Kubernetes configuration, either in-cluster or from a local Kubeconfig file
    config.load_kube_config()

    # Initialize the Kubernetes API client
    v1 = client.CoreV1Api()

    # Create a dictionary to hold pod names and their network status in JSON format
    pod_network_status = {}

    # List all pods across all namespaces
    pods = v1.list_pod_for_all_namespaces()

    for pod in pods.items:
        # Ensure annotations are not None
        annotations = pod.metadata.annotations or {}

        # Extract the 'k8s.v1.cni.cncf.io/network-status' annotation
        network_status_str = annotations.get('k8s.v1.cni.cncf.io/network-status')

        if network_status_str:
            try:
                # Parse the network status string as JSON
                network_status_json = json.loads(network_status_str)
                # Store the parsed JSON against the pod's name
                pod_network_status[pod.metadata.name] = network_status_json
            except json.JSONDecodeError:
                # Handle cases where the annotation is not valid JSON
                pod_network_status[pod.metadata.name] = "Invalid JSON or not available"

    return pod_network_status

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_pods(request):
    try:
        config.load_kube_config()
        v1 = client.CoreV1Api()

        # Derive namespace from the current user's username
        user_namespace = f"{request.user.username}"

        # List pods in the specific namespace
        pods_list = v1.list_namespaced_pod(namespace=user_namespace)

        # Retrieve all network statuses in advance
        network_statuses = get_network_status_annotations()

        # Convert the pods_list to a list of dictionaries
        pods_info = []
        for pod in pods_list.items:
            # Ensure annotations are not None
            annotations = pod.metadata.annotations or {}

            # Retrieve the network status for the current pod
            network_status_json = network_statuses.get(pod.metadata.name, 'Not available')

            pod_info = {
                'name': pod.metadata.name,
                'ip': pod.status.pod_ip,
                'network_status': network_status_json,  # Inserting network status in JSON format
                'state': pod.status.phase,
                'namespace': pod.metadata.namespace,
                'node': pod.spec.node_name,
                # Add more fields as needed
            }
            pods_info.append(pod_info)

        # Return JsonResponse with the list of pod information
        return JsonResponse({'pods': pods_info})
    except client.rest.ApiException as e:
        return Response({"error": f"Failed to retrieve pods: {str(e)}"}, status=e.status)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_deployments(request):
    config.load_kube_config()
    apps_v1 = client.AppsV1Api()

    namespace = f"{request.user.username}"

    try:
        deployments = apps_v1.list_namespaced_deployment(namespace)
        deployment_data = []
        for deployment in deployments.items:
            deployment_info = {
                "deployment_name": deployment.metadata.name,
                "namespace": deployment.metadata.namespace,
                "replicas": deployment.spec.replicas,
                "available_replicas": deployment.status.available_replicas,
                "ready_replicas": deployment.status.ready_replicas,
                "updated_replicas": deployment.status.updated_replicas,
                "strategy": deployment.spec.strategy.type,
                "conditions": [condition.type for condition in deployment.status.conditions] if deployment.status.conditions else []
            }
            deployment_data.append(deployment_info)

        return Response(deployment_data)
    except client.rest.ApiException as e:
        return Response({"error": f"Failed to retrieve deployments: {str(e)}"}, status=e.status)

###RELATED TO 5G COMPONENTS MANAGEMENT FEATURE###
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def restart_single_cu(request):
    try:
        # Derive the namespace from the current user's username
        namespace = f"{request.user.username}"
        deployment_name = f"oai-cu-level1-{namespace}"  # Dynamically create the deployment name

        result = subprocess.run(
            ["kubectl", "rollout", "restart", "deployment", deployment_name, "--namespace", namespace],
            capture_output=True, text=True
        )

        # If the subprocess call was successful, return a success response
        return Response({"message": "Deployment restarted successfully.", "details": result.stdout}, status=200)
    except subprocess.CalledProcessError as e:
        # Return an error response if the subprocess call failed
        return Response({"error": "An error occurred while restarting the deployment.", "details": str(e)}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def restart_single_du(request):
    try:
        # Derive the namespace from the current user's username
        namespace = f"{request.user.username}"
        deployment_name = f"oai-du-level1-{namespace}"  # Dynamically create the deployment name

        result = subprocess.run(
            ["kubectl", "rollout", "restart", "deployment", deployment_name, "--namespace", namespace],
            capture_output=True, text=True
        )

        # If the subprocess call was successful, return a success response
        return Response({"message": "Deployment restarted successfully.", "details": result.stdout}, status=200)
    except subprocess.CalledProcessError as e:
        # Return an error response if the subprocess call failed
        return Response({"error": "An error occurred while restarting the deployment.", "details": str(e)}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def restart_single_ue(request):
    try:
        # Derive the namespace from the current user's username
        namespace = f"{request.user.username}"
        deployment_name = f"oai-nr-ue-level1-{namespace}"  # Dynamically create the deployment name

        result = subprocess.run(
            ["kubectl", "rollout", "restart", "deployment", deployment_name, "--namespace", namespace],
            capture_output=True, text=True
        )

        # If the subprocess call was successful, return a success response
        return Response({"message": "Deployment restarted successfully.", "details": result.stdout}, status=200)
    except subprocess.CalledProcessError as e:
        # Return an error response if the subprocess call failed
        return Response({"error": "An error occurred while restarting the deployment.", "details": str(e)}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def restart_multignb_cu(request):
    try:
        # Derive the namespace from the current user's username
        namespace = f"{request.user.username}"
        deployment_name = f"oai-cu-level2-{namespace}"  # Dynamically create the deployment name

        result = subprocess.run(
            ["kubectl", "rollout", "restart", "deployment", deployment_name, "--namespace", namespace],
            capture_output=True, text=True
        )

        # If the subprocess call was successful, return a success response
        return Response({"message": "Deployment restarted successfully.", "details": result.stdout}, status=200)
    except subprocess.CalledProcessError as e:
        # Return an error response if the subprocess call failed
        return Response({"error": "An error occurred while restarting the deployment.", "details": str(e)}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def restart_multignb_du1(request):
    try:
        # Derive the namespace from the current user's username
        namespace = f"{request.user.username}"
        deployment_name = f"oai-du1-level2-{namespace}"  # Dynamically create the deployment name

        result = subprocess.run(
            ["kubectl", "rollout", "restart", "deployment", deployment_name, "--namespace", namespace],
            capture_output=True, text=True
        )

        # If the subprocess call was successful, return a success response
        return Response({"message": "Deployment restarted successfully.", "details": result.stdout}, status=200)
    except subprocess.CalledProcessError as e:
        # Return an error response if the subprocess call failed
        return Response({"error": "An error occurred while restarting the deployment.", "details": str(e)}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def restart_multignb_du2(request):
    try:
        # Derive the namespace from the current user's username
        namespace = f"{request.user.username}"
        deployment_name = f"oai-du2-level2-{namespace}"  # Dynamically create the deployment name

        result = subprocess.run(
            ["kubectl", "rollout", "restart", "deployment", deployment_name, "--namespace", namespace],
            capture_output=True, text=True
        )

        # If the subprocess call was successful, return a success response
        return Response({"message": "Deployment restarted successfully.", "details": result.stdout}, status=200)
    except subprocess.CalledProcessError as e:
        # Return an error response if the subprocess call failed
        return Response({"error": "An error occurred while restarting the deployment.", "details": str(e)}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def restart_multignb_ue1(request):
    try:
        # Derive the namespace from the current user's username
        namespace = f"{request.user.username}"
        deployment_name = f"oai-nr-ue1-level2-{namespace}"  # Dynamically create the deployment name

        result = subprocess.run(
            ["kubectl", "rollout", "restart", "deployment", deployment_name, "--namespace", namespace],
            capture_output=True, text=True
        )

        # If the subprocess call was successful, return a success response
        return Response({"message": "Deployment restarted successfully.", "details": result.stdout}, status=200)
    except subprocess.CalledProcessError as e:
        # Return an error response if the subprocess call failed
        return Response({"error": "An error occurred while restarting the deployment.", "details": str(e)}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def restart_multignb_ue2(request):
    try:
        # Derive the namespace from the current user's username
        namespace = f"{request.user.username}"
        deployment_name = f"oai-nr-ue2-level2-{namespace}"  # Dynamically create the deployment name

        result = subprocess.run(
            ["kubectl", "rollout", "restart", "deployment", deployment_name, "--namespace", namespace],
            capture_output=True, text=True
        )

        # If the subprocess call was successful, return a success response
        return Response({"message": "Deployment restarted successfully.", "details": result.stdout}, status=200)
    except subprocess.CalledProcessError as e:
        # Return an error response if the subprocess call failed
        return Response({"error": "An error occurred while restarting the deployment.", "details": str(e)}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def restart_multiue_cu(request):
    try:
        # Derive the namespace from the current user's username
        namespace = f"{request.user.username}"
        deployment_name = f"oai-cu-level3-{namespace}"  # Dynamically create the deployment name

        result = subprocess.run(
            ["kubectl", "rollout", "restart", "deployment", deployment_name, "--namespace", namespace],
            capture_output=True, text=True
        )

        # If the subprocess call was successful, return a success response
        return Response({"message": "Deployment restarted successfully.", "details": result.stdout}, status=200)
    except subprocess.CalledProcessError as e:
        # Return an error response if the subprocess call failed
        return Response({"error": "An error occurred while restarting the deployment.", "details": str(e)}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def restart_multiue_du(request):
    try:
        # Derive the namespace from the current user's username
        namespace = f"{request.user.username}"
        deployment_name = f"oai-du-level3-{namespace}"  # Dynamically create the deployment name

        result = subprocess.run(
            ["kubectl", "rollout", "restart", "deployment", deployment_name, "--namespace", namespace],
            capture_output=True, text=True
        )

        # If the subprocess call was successful, return a success response
        return Response({"message": "Deployment restarted successfully.", "details": result.stdout}, status=200)
    except subprocess.CalledProcessError as e:
        # Return an error response if the subprocess call failed
        return Response({"error": "An error occurred while restarting the deployment.", "details": str(e)}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def restart_multiue_ue1(request):
    try:
        # Derive the namespace from the current user's username
        namespace = f"{request.user.username}"
        deployment_name = f"oai-nr-ue1-level3-{namespace}"  # Dynamically create the deployment name

        result = subprocess.run(
            ["kubectl", "rollout", "restart", "deployment", deployment_name, "--namespace", namespace],
            capture_output=True, text=True
        )

        # If the subprocess call was successful, return a success response
        return Response({"message": "Deployment restarted successfully.", "details": result.stdout}, status=200)
    except subprocess.CalledProcessError as e:
        # Return an error response if the subprocess call failed
        return Response({"error": "An error occurred while restarting the deployment.", "details": str(e)}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def restart_multiue_ue2(request):
    try:
        # Derive the namespace from the current user's username
        namespace = f"{request.user.username}"
        deployment_name = f"oai-nr-ue2-level3-{namespace}"  # Dynamically create the deployment name

        result = subprocess.run(
            ["kubectl", "rollout", "restart", "deployment", deployment_name, "--namespace", namespace],
            capture_output=True, text=True
        )

        # If the subprocess call was successful, return a success response
        return Response({"message": "Deployment restarted successfully.", "details": result.stdout}, status=200)
    except subprocess.CalledProcessError as e:
        # Return an error response if the subprocess call failed
        return Response({"error": "An error occurred while restarting the deployment.", "details": str(e)}, status=500)


###MONITORING - LOGS###
from datetime import datetime

def parse_kubernetes_timestamp(timestamp_str):
    # Trim the nanoseconds and ignore the timezone for simplicity
    # Kubernetes timestamp format: 2024-03-07T14:56:38.473658908+07:00
    # Simplified format: 2024-03-07T14:56:38
    simplified_timestamp_str = timestamp_str.split('.')[0]
    return datetime.fromisoformat(simplified_timestamp_str)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_pod_logs(request, pod_name):
    namespace = f"{request.user.username}"
    try:
        cmd = [
            "kubectl", "logs", pod_name,
            "-n", namespace,
            "--tail=10",  # Fetch the last 10 lines of logs
            "--timestamps"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        logs = result.stdout.strip().split('\n')

        structured_logs = []
        for line in logs:
            parts = line.split(maxsplit=1)  # Split only on the first space
            if len(parts) == 2:
                timestamp_str, log_message = parts
                # Parse the timestamp and reformat it to show only the time
                timestamp = parse_kubernetes_timestamp(timestamp_str)
                time_only_str = timestamp.strftime('%H:%M:%S')
                structured_logs.append({"timestamp": time_only_str, "log": log_message})
        
        return JsonResponse(structured_logs, safe=False)

    except subprocess.CalledProcessError as e:
        error_message = f"Failed to fetch logs: {e.stderr}"
        return JsonResponse({"error": error_message}, status=400)


def get_valid_deployments(user, user_level):
    base_names_by_level = {
        'level1': [
            'oai-cu',
            'oai-du',
            'oai-nr-ue'
        ],
        'level2': [
            'oai-cu',
            'oai-du1',
            'oai-du2',
            'oai-nr-ue1',
            'oai-nr-ue2'
        ],
        'level3': [
            'oai-cu',
            'oai-du',
            'oai-nr-ue1',
            'oai-nr-ue2'
        ]
    }

    base_names = base_names_by_level.get(f'level{user_level}', [])
    matching_deployments = []
    non_matching_deployments = []

    for level in ['level1', 'level2', 'level3']:
        for base in base_names_by_level[level]:
            deployment_name = f"{base}-{level}-{user.username}"
            if level == f'level{user_level}':
                matching_deployments.append(deployment_name)
            else:
                non_matching_deployments.append(deployment_name)

    return matching_deployments, non_matching_deployments

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def set_replicaset(request):
    user = request.user  # Get the authenticated user from the request
    namespace = f"{user.username}"
    profile, _ = UserProfile.objects.get_or_create(user=user)
    user_level = profile.level  # Get the user level from the profile

    matching_deployments, non_matching_deployments = get_valid_deployments(user, user_level)

    errors = []

    # Scale up the deployments that match the user's level to 1
    for deployment in matching_deployments:
        try:
            subprocess.run(['kubectl', 'scale', 'deployment', deployment, '--replicas=1', f"--namespace={namespace}"], check=True)
        except subprocess.CalledProcessError as e:
            errors.append(f"Failed to scale up {deployment}: {str(e)}")

    # Scale down the deployments that do not match the user's level to 0
    for deployment in non_matching_deployments:
        try:
            subprocess.run(['kubectl', 'scale', 'deployment', deployment, '--replicas=0', f"--namespace={namespace}"], check=True)
        except subprocess.CalledProcessError as e:
            errors.append(f"Failed to scale down {deployment}: {str(e)}")

    if errors:
        return Response({'error': 'Some deployments could not be scaled down/up', 'details': errors}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({'message': 'ReplicaSets updated successfully', 'scaled_up_deployments': matching_deployments, 'scaled_down_deployments': non_matching_deployments})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ping_google(request):
    user = request.user
    namespace = f"{user.username}"

    try:
        profile = UserProfile.objects.get(user=user)
        user_level = profile.level
        component_container = "nr-ue"  # The container you want to exec into
        pod_label = f"oai-nr-ue-level{user_level}-{user.username}"

        # Construct the command to get the pod name
        get_pod_command = f"kubectl get pods -n {namespace} | grep {pod_label} | awk '{{print $1}}'"
        pod_name = subprocess.check_output(get_pod_command, shell=True).decode('utf-8').strip()

        if pod_name:
            ping_command = f"kubectl exec -n {namespace} -c {component_container} {pod_name} -- ping -c 10 8.8.8.8"
            ping_output = subprocess.check_output(ping_command, shell=True).decode('utf-8').strip()

            return Response({"message": "Ping successful", "output": ping_output}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Pod not found"}, status=status.HTTP_404_NOT_FOUND)
    except subprocess.CalledProcessError as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except UserProfile.DoesNotExist:
        return Response({"error": "User profile not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def curl_google(request):
    user = request.user
    namespace = f"{user.username}"

    try:
        profile = UserProfile.objects.get(user=user)
        user_level = profile.level
        component_container = "nr-ue"  # The container you want to exec into
        pod_label = f"oai-nr-ue-level{user_level}-{user.username}"

        # Construct the command to get the pod name
        get_pod_command = f"kubectl get pods -n {namespace} | grep {pod_label} | awk '{{print $1}}'"
        pod_name = subprocess.check_output(get_pod_command, shell=True).decode('utf-8').strip()

        if pod_name:
            curl_command = f"kubectl exec -n {namespace} -c {component_container} {pod_name} -- curl www.google.com"
            curl_output = subprocess.check_output(curl_command, shell=True).decode('utf-8').strip()

            return Response({"message": "curl successful", "output": curl_output}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Pod not found"}, status=status.HTTP_404_NOT_FOUND)
    except subprocess.CalledProcessError as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except UserProfile.DoesNotExist:
        return Response({"error": "User profile not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)