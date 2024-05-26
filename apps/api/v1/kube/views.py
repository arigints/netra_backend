from kubernetes import client, config
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import json
from django.http import JsonResponse
import subprocess
from rest_framework import status

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


def get_deployment_names(user, level):
    base_names = [
        'oai-cu',
        'oai-du',
        'oai-du1',
        'oai-du2',
        'oai-nr-ue',
        'oai-nr-ue1',
        'oai-nr-ue2'
    ]
    levels = ['level1', 'level2', 'level3']
    user_deployments = []

    for base in base_names:
        for lvl in levels:
            user_deployments.append(f"{base}-{lvl}-{user.username}")

    return user_deployments

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def set_replicaset(request):
    user = request.user  # Get the authenticated user from the request
    profile, _ = UserProfile.objects.get_or_create(user=user)
    user_level = profile.level  # Get the user level from the profile

    all_deployments = get_deployment_names(user, user_level)

    # Determine the deployments that need to be scaled down
    deployments_to_scale_down = [dep for dep in all_deployments if f"level{user_level}" not in dep]

    errors = []

    for deployment in deployments_to_scale_down:
        try:
            # Use kubectl to scale the ReplicaSet to 0
            subprocess.run(['kubectl', 'scale', 'deployment', deployment, '--replicas=0'], check=True)
        except subprocess.CalledProcessError as e:
            errors.append(f"Failed to scale {deployment}: {str(e)}")

    if errors:
        return Response({'error': 'Some deployments could not be scaled down', 'details': errors}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({'message': 'ReplicaSets updated successfully', 'scaled_down_deployments': deployments_to_scale_down})