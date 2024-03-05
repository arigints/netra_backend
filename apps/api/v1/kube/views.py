from kubernetes import client, config
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import json
from django.http import JsonResponse

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
        user_namespace = f"{request.user.username}-namespace"

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

    namespace = f"{request.user.username}-namespace"

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
        namespace = f"{request.user.username}-namespace"

        result = subprocess.run(
            ["kubectl", "rollout", "restart", "deployment", "single-cu", "--namespace", namespace],
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
        namespace = f"{request.user.username}-namespace"

        result = subprocess.run(
            ["kubectl", "rollout", "restart", "deployment", "single-du", "--namespace", namespace],
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
        namespace = f"{request.user.username}-namespace"

        result = subprocess.run(
            ["kubectl", "rollout", "restart", "deployment", "single-ue", "--namespace", namespace],
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
        namespace = f"{request.user.username}-namespace"

        result = subprocess.run(
            ["kubectl", "rollout", "restart", "deployment", "multignb-cu", "--namespace", namespace],
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
        namespace = f"{request.user.username}-namespace"

        result = subprocess.run(
            ["kubectl", "rollout", "restart", "deployment", "multignb-du1", "--namespace", namespace],
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
        namespace = f"{request.user.username}-namespace"

        result = subprocess.run(
            ["kubectl", "rollout", "restart", "deployment", "multignb-du2", "--namespace", namespace],
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
        namespace = f"{request.user.username}-namespace"

        result = subprocess.run(
            ["kubectl", "rollout", "restart", "deployment", "multignb-ue1", "--namespace", namespace],
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
        namespace = f"{request.user.username}-namespace"

        result = subprocess.run(
            ["kubectl", "rollout", "restart", "deployment", "multignb-ue2", "--namespace", namespace],
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
        namespace = f"{request.user.username}-namespace"

        result = subprocess.run(
            ["kubectl", "rollout", "restart", "deployment", "multiue-cu", "--namespace", namespace],
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
        namespace = f"{request.user.username}-namespace"

        result = subprocess.run(
            ["kubectl", "rollout", "restart", "deployment", "multiue-du", "--namespace", namespace],
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
        namespace = f"{request.user.username}-namespace"

        result = subprocess.run(
            ["kubectl", "rollout", "restart", "deployment", "multiue-ue1", "--namespace", namespace],
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
        namespace = f"{request.user.username}-namespace"

        result = subprocess.run(
            ["kubectl", "rollout", "restart", "deployment", "multiue-ue2", "--namespace", namespace],
            capture_output=True, text=True
        )

        # If the subprocess call was successful, return a success response
        return Response({"message": "Deployment restarted successfully.", "details": result.stdout}, status=200)
    except subprocess.CalledProcessError as e:
        # Return an error response if the subprocess call failed
        return Response({"error": "An error occurred while restarting the deployment.", "details": str(e)}, status=500)