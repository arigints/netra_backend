from django.shortcuts import render, HttpResponse, redirect
from rest_framework.response import Response
from rest_framework.decorators import api_view
import subprocess
import yaml
import os
from apps.models import UserProfile
import json
from django.http import JsonResponse
from pathlib import Path
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status

BASE_DIR = Path(__file__).resolve().parent.parent

SINGLE_CU_BASE_DIR = os.path.join(BASE_DIR, 'oai/oai-e2e/oai-cu/')  
SINGLE_DU_BASE_DIR = os.path.join(BASE_DIR, 'oai/oai-e2e/oai-du/')  
SINGLE_UE_BASE_DIR = os.path.join(BASE_DIR, 'oai/oai-e2e/oai-nr-ue/')  

MULTI_GNB_CU_BASE_DIR = os.path.join(BASE_DIR, 'oai/oai-multi-gnb/oai-cu/')  
MULTI_GNB_DU1_BASE_DIR = os.path.join(BASE_DIR, 'oai/oai-multi-gnb/oai-du-1/')  
MULTI_GNB_DU2_BASE_DIR = os.path.join(BASE_DIR, 'oai/oai-multi-gnb/oai-du-2/')  
MULTI_GNB_UE1_BASE_DIR = os.path.join(BASE_DIR, 'oai/oai-multi-gnb/oai-nr-ue-1/') 
MULTI_GNB_UE2_BASE_DIR = os.path.join(BASE_DIR, 'oai/oai-multi-gnb/oai-nr-ue-2/')  

MULTI_UE_CU_BASE_DIR = os.path.join(BASE_DIR, 'oai/oai-multi-ue/oai-cu/')  
MULTI_UE_DU_BASE_DIR = os.path.join(BASE_DIR, 'oai/oai-multi-ue/oai-du/')  
MULTI_UE_UE1_BASE_DIR = os.path.join(BASE_DIR, 'oai/oai-multi-ue/oai-nr-ue-1/')  
MULTI_UE_UE2_BASE_DIR = os.path.join(BASE_DIR, 'oai/oai-multi-ue/oai-nr-ue-2/') 

SINGLE_CU_VALUES_FILE_PATH = os.path.join(SINGLE_CU_BASE_DIR, 'values.yaml')
SINGLE_DU_VALUES_FILE_PATH = os.path.join(SINGLE_DU_BASE_DIR, 'values.yaml')
SINGLE_UE_VALUES_FILE_PATH = os.path.join(SINGLE_UE_BASE_DIR, 'values.yaml')

MULTI_GNB_CU_VALUES_FILE_PATH = os.path.join(MULTI_GNB_CU_BASE_DIR, 'values.yaml')
MULTI_GNB_DU1_VALUES_FILE_PATH = os.path.join(MULTI_GNB_DU1_BASE_DIR, 'values.yaml')
MULTI_GNB_DU2_VALUES_FILE_PATH = os.path.join(MULTI_GNB_DU2_BASE_DIR, 'values.yaml')
MULTI_GNB_UE1_VALUES_FILE_PATH = os.path.join(MULTI_GNB_UE1_BASE_DIR, 'values.yaml')
MULTI_GNB_UE2_VALUES_FILE_PATH = os.path.join(MULTI_GNB_UE2_BASE_DIR, 'values.yaml')

MULTI_UE_CU_VALUES_FILE_PATH = os.path.join(MULTI_UE_CU_BASE_DIR, 'values.yaml')
MULTI_UE_DU_VALUES_FILE_PATH = os.path.join(MULTI_UE_DU_BASE_DIR, 'values.yaml')
MULTI_UE_UE1_VALUES_FILE_PATH = os.path.join(MULTI_UE_UE1_BASE_DIR, 'values.yaml')
MULTI_UE_UE2_VALUES_FILE_PATH = os.path.join(MULTI_UE_UE2_BASE_DIR, 'values.yaml')

SINGLE_CU_CHART_FILE_PATH = os.path.join(SINGLE_CU_BASE_DIR, 'Chart.yaml')
SINGLE_DU_CHART_FILE_PATH = os.path.join(SINGLE_DU_BASE_DIR, 'Chart.yaml')
SINGLE_UE_CHART_FILE_PATH = os.path.join(SINGLE_UE_BASE_DIR, 'Chart.yaml')

MULTI_GNB_CU_CHART_FILE_PATH = os.path.join(MULTI_GNB_CU_BASE_DIR, 'Chart.yaml')
MULTI_GNB_DU1_CHART_FILE_PATH = os.path.join(MULTI_GNB_DU1_BASE_DIR, 'Chart.yaml')
MULTI_GNB_DU2_CHART_FILE_PATH = os.path.join(MULTI_GNB_DU2_BASE_DIR, 'Chart.yaml')
MULTI_GNB_UE1_CHART_FILE_PATH = os.path.join(MULTI_GNB_UE1_BASE_DIR, 'Chart.yaml')
MULTI_GNB_UE2_CHART_FILE_PATH = os.path.join(MULTI_GNB_UE2_BASE_DIR, 'Chart.yaml')

MULTI_UE_CU_CHART_FILE_PATH = os.path.join(MULTI_UE_CU_BASE_DIR, 'Chart.yaml')
MULTI_UE_DU_CHART_FILE_PATH = os.path.join(MULTI_UE_DU_BASE_DIR, 'Chart.yaml')
MULTI_UE_UE1_CHART_FILE_PATH = os.path.join(MULTI_UE_UE1_BASE_DIR, 'Chart.yaml')
MULTI_UE_UE2_CHART_FILE_PATH = os.path.join(MULTI_UE_UE2_BASE_DIR, 'Chart.yaml')

def update_chart_name(chart_file_path, username):
    with open(chart_file_path, 'r') as file:
        chart_yaml = yaml.safe_load(file)

    # Append the username to the existing chart name with a hyphen
    chart_yaml['name'] = f"{chart_yaml['name']}-{username}"

    with open(chart_file_path, 'w') as file:
        yaml.dump(chart_yaml, file)


def revert_chart_name(chart_file_path, original_name):
    with open(chart_file_path, 'r') as file:
        chart_yaml = yaml.safe_load(file)

    chart_yaml['name'] = original_name

    with open(chart_file_path, 'w') as file:
        yaml.dump(chart_yaml, file)


###CREATE ALL 5G COMPONENT NEEDED BY THE USER###
def create_all_components(request, namespace):
    original_names = {}

    # Define paths to your chart files (assuming these are defined elsewhere)
    chart_files = {
        "single_cu": SINGLE_CU_CHART_FILE_PATH,
        "single_du": SINGLE_DU_CHART_FILE_PATH,
        "single_ue": SINGLE_UE_CHART_FILE_PATH,
        "multignb_cu": MULTI_GNB_CU_CHART_FILE_PATH,
        "multignb_du1": MULTI_GNB_DU1_CHART_FILE_PATH,
        "multignb_du2": MULTI_GNB_DU2_CHART_FILE_PATH,
        "multignb_ue1": MULTI_GNB_UE1_CHART_FILE_PATH,
        "multignb_ue2": MULTI_GNB_UE2_CHART_FILE_PATH,
        "multiue_cu": MULTI_UE_CU_CHART_FILE_PATH,
        "multiue_du": MULTI_UE_DU_CHART_FILE_PATH,
        "multiue_ue1": MULTI_UE_UE1_CHART_FILE_PATH,
        "multiue_ue2": MULTI_UE_UE2_CHART_FILE_PATH,
    }

    try:
        # Store original names and update with new names
        for key, chart_file_path in chart_files.items():
            with open(chart_file_path, 'r') as file:
                chart_yaml = yaml.safe_load(file)
                original_names[chart_file_path] = chart_yaml['name']
            update_chart_name(chart_file_path, namespace)

        # Define the Helm install commands
        helm_commands = {
            "single_cu": [SINGLE_CU_BASE_DIR, "single-cu"],
            "single_du": [SINGLE_DU_BASE_DIR, "single-du"],
            "single_ue": [SINGLE_UE_BASE_DIR, "single-ue"],
            "multignb_cu": [MULTI_GNB_CU_BASE_DIR, "multignb-cu"],
            "multignb_du1": [MULTI_GNB_DU1_BASE_DIR, "multignb-du1"],
            "multignb_du2": [MULTI_GNB_DU2_BASE_DIR, "multignb-du2"],
            "multignb_ue1": [MULTI_GNB_UE1_BASE_DIR, "multignb-ue1"],
            "multignb_ue2": [MULTI_GNB_UE2_BASE_DIR, "multignb-ue2"],
            "multiue_cu": [MULTI_UE_CU_BASE_DIR, "multiue-cu"],
            "multiue_du": [MULTI_UE_DU_BASE_DIR, "multiue-du"],
            "multiue_ue1": [MULTI_UE_UE1_BASE_DIR, "multiue-ue1"],
            "multiue_ue2": [MULTI_UE_UE2_BASE_DIR, "multiue-ue2"],
        }

        # Install Helm charts
        for key, value in helm_commands.items():
            base_dir, release_name = value
            subprocess.run([
                "helm", "install", release_name, "--values", "values.yaml",
                ".", "--namespace", namespace
            ], cwd=base_dir)

        # Define and scale deployments for each level
        level1_deployments = ["cu", "du", "nr-ue"]
        level2_deployments = ["cu", "du1", "du2", "nr-ue1", "nr-ue2"]
        level3_deployments = ["cu", "du", "nr-ue1", "nr-ue2"]

        for component in level1_deployments:
            deployment_name = f"oai-{component}-level1-{namespace}"
            subprocess.run([
                "kubectl", "scale", "deployment", deployment_name, "--replicas=0",
                "--namespace=" + namespace
            ])

        for component in level2_deployments:
            deployment_name = f"oai-{component}-level2-{namespace}"
            subprocess.run([
                "kubectl", "scale", "deployment", deployment_name, "--replicas=0",
                "--namespace=" + namespace
            ])

        for component in level3_deployments:
            deployment_name = f"oai-{component}-level3-{namespace}"
            subprocess.run([
                "kubectl", "scale", "deployment", deployment_name, "--replicas=0",
                "--namespace=" + namespace
            ])

        return "Success"

    except subprocess.CalledProcessError as e:
        return Response({"error": f"An error occurred: {e}"}, status=500)
    finally:
        # Revert the names back to original
        for chart_file_path, original_name in original_names.items():
            revert_chart_name(chart_file_path, original_name)



###DELETE ALL 5G COMPONENT ALONGSIDE USER ACCOUNT DELETION###
def delete_all_components(request, namespace):
    try:
        #SINGLE - CU
        subprocess.run([
            "helm", "delete", "single-cu", "--namespace", namespace
        ])

        #SINGLE - DU
        subprocess.run([
            "helm", "delete", "single-du", "--namespace", namespace
        ])

        #SINGLE - UE
        subprocess.run([
            "helm", "delete", "single-ue", "--namespace", namespace
        ])

        #MULTI-GNB - CU
        subprocess.run([
            "helm", "delete", "multignb-cu", "--namespace", namespace
        ])

        #MULTI-GNB - DU1
        subprocess.run([
            "helm", "delete", "multignb-du1", "--namespace", namespace
        ])

        #MULTI-GNB - DU2
        subprocess.run([
            "helm", "delete", "multignb-du2", "--namespace", namespace
        ])

        #MULTI-GNB - UE1
        subprocess.run([
            "helm", "delete", "multignb-ue1", "--namespace", namespace
        ])

        #MULTI-GNB - UE2
        subprocess.run([
            "helm", "delete", "multignb-ue2", "--namespace", namespace
        ])

        #MULTI-UE - CU
        subprocess.run([
            "helm", "delete", "multiue-cu", "--namespace", namespace
        ])

        #MULTI-UE - DU
        subprocess.run([
            "helm", "delete", "multiue-du", "--namespace", namespace
        ])

        #MULTI-UE - UE1
        subprocess.run([
            "helm", "delete", "multiue-ue1", "--namespace", namespace
        ])

        #MULTI-UE - UE2
        subprocess.run([
            "helm", "delete", "multiue-ue2", "--namespace", namespace
        ])

        return "Success"

    except subprocess.CalledProcessError as e:
        # Handle errors in the subprocesses
        return f"An error occurred: {e}"


###SINGLE - CU###
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def values_single_cu(request):
    user_namespace = f"{request.user.username}"

    # Execute helm get values command
    command = ["helm", "get", "values", "single-cu", "--namespace", user_namespace]
    try:
        helm_output = subprocess.check_output(command, stderr=subprocess.STDOUT)
        values_yaml = helm_output.decode('utf-8')

        # Convert YAML to JSON
        values_json = yaml.safe_load(values_yaml)

        # Assuming 'values' is the top-level key as per your example (confirm this path in your actual YAML structure).
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

        return JsonResponse({'values': specific_values})

    except subprocess.CalledProcessError as e:
        return JsonResponse({'error': 'Failed to retrieve Helm release values',
                             'details': e.output.decode('utf-8')}, status=500)

    except Exception as e:
        return JsonResponse({'error': 'An unexpected error occurred',
                             'details': str(e)}, status=500)


###SINGLE - DU###
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def values_single_du(request):
    user_namespace = f"{request.user.username}"

    # Execute helm get values command
    command = ["helm", "get", "values", "single-du", "--namespace", user_namespace]
    try:
        helm_output = subprocess.check_output(command, stderr=subprocess.STDOUT)
        values_yaml = helm_output.decode('utf-8')

        # Convert YAML to JSON
        values_json = yaml.safe_load(values_yaml)  # Assumes PyYAML or similar package is used

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

        return JsonResponse({'values': specific_values})

    except subprocess.CalledProcessError as e:
        return JsonResponse({'error': 'Failed to retrieve Helm release values',
                             'details': e.output.decode('utf-8')}, status=500)

    except Exception as e:
        return JsonResponse({'error': 'An unexpected error occurred',
                             'details': str(e)}, status=500)

###SINGLE - UE###
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def values_single_ue(request):
    user_namespace = f"{request.user.username}"

    # Execute helm get values command
    command = ["helm", "get", "values", "single-ue", "--namespace", user_namespace]
    try:
        helm_output = subprocess.check_output(command, stderr=subprocess.STDOUT)
        values_yaml = helm_output.decode('utf-8')

        # Convert YAML to JSON
        values_json = yaml.safe_load(values_yaml)  # Assumes PyYAML or similar package is used

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

        return JsonResponse({'values': specific_values})

    except subprocess.CalledProcessError as e:
        return JsonResponse({'error': 'Failed to retrieve Helm release values',
                             'details': e.output.decode('utf-8')}, status=500)

    except Exception as e:
        return JsonResponse({'error': 'An unexpected error occurred',
                             'details': str(e)}, status=500)


###MULTIGNB - CU###
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def values_multignb_cu(request):
    user_namespace = f"{request.user.username}"

    # Execute helm get values command
    command = ["helm", "get", "values", "multignb-cu", "--namespace", user_namespace]
    try:
        helm_output = subprocess.check_output(command, stderr=subprocess.STDOUT)
        values_yaml = helm_output.decode('utf-8')

        # Convert YAML to JSON
        values_json = yaml.safe_load(values_yaml)  # Assumes PyYAML or similar package is used

        # It seems like the structure might differ. Make sure to access the correct path.
        # Extract specific values assuming 'values' is the top-level key as per your example.
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

        return JsonResponse({'values': specific_values})

    except subprocess.CalledProcessError as e:
        return JsonResponse({'error': 'Failed to retrieve Helm release values',
                             'details': e.output.decode('utf-8')}, status=500)

    except Exception as e:
        return JsonResponse({'error': 'An unexpected error occurred',
                             'details': str(e)}, status=500)

###GMULTIGNB - DU1###
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def values_multignb_du1(request):
    user_namespace = f"{request.user.username}"

    # Execute helm get values command
    command = ["helm", "get", "values", "multignb-du1", "--namespace", user_namespace]
    try:
        helm_output = subprocess.check_output(command, stderr=subprocess.STDOUT)
        values_yaml = helm_output.decode('utf-8')

        # Convert YAML to JSON
        values_json = yaml.safe_load(values_yaml)  # Assumes PyYAML or similar package is used

        # Extract specific values
        specific_values = {
            'gnbId': values_json.get('config', {}).get('gnbId', ''),   
            'duId': values_json.get('config', {}).get('duId', ''),      
            'cellId': values_json.get('config', {}).get('cellId', ''),
            'phyCellId': values_json.get('config', {}).get('phyCellId', ''),
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

        return JsonResponse({'values': specific_values})

    except subprocess.CalledProcessError as e:
        return JsonResponse({'error': 'Failed to retrieve Helm release values',
                             'details': e.output.decode('utf-8')}, status=500)

    except Exception as e:
        return JsonResponse({'error': 'An unexpected error occurred',
                             'details': str(e)}, status=500)

###MULTIGNB - DU2###
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def values_multignb_du2(request):
    user_namespace = f"{request.user.username}"

    # Execute helm get values command
    command = ["helm", "get", "values", "multignb-du2", "--namespace", user_namespace]
    try:
        helm_output = subprocess.check_output(command, stderr=subprocess.STDOUT)
        values_yaml = helm_output.decode('utf-8')

        # Convert YAML to JSON
        values_json = yaml.safe_load(values_yaml)  # Assumes PyYAML or similar package is used

        # Extract specific values
        specific_values = {
            'gnbId': values_json.get('config', {}).get('gnbId', ''),   
            'duId': values_json.get('config', {}).get('duId', ''),      
            'cellId': values_json.get('config', {}).get('cellId', ''),
            'phyCellId': values_json.get('config', {}).get('phyCellId', ''),
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

        return JsonResponse({'values': specific_values})

    except subprocess.CalledProcessError as e:
        return JsonResponse({'error': 'Failed to retrieve Helm release values',
                             'details': e.output.decode('utf-8')}, status=500)

    except Exception as e:
        return JsonResponse({'error': 'An unexpected error occurred',
                             'details': str(e)}, status=500)

###MULTIGNB - UE1###
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def values_multignb_ue1(request):
    user_namespace = f"{request.user.username}"

    # Execute helm get values command
    command = ["helm", "get", "values", "multignb-ue1", "--namespace", user_namespace]
    try:
        helm_output = subprocess.check_output(command, stderr=subprocess.STDOUT)
        values_yaml = helm_output.decode('utf-8')

        # Convert YAML to JSON
        values_json = yaml.safe_load(values_yaml)  # Assumes PyYAML or similar package is used

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

        return JsonResponse({'values': specific_values})

    except subprocess.CalledProcessError as e:
        return JsonResponse({'error': 'Failed to retrieve Helm release values',
                             'details': e.output.decode('utf-8')}, status=500)

    except Exception as e:
        return JsonResponse({'error': 'An unexpected error occurred',
                             'details': str(e)}, status=500)

###MULTIGNB - UE2###
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def values_multignb_ue2(request):
    user_namespace = f"{request.user.username}"

    # Execute helm get values command
    command = ["helm", "get", "values", "multignb-ue2", "--namespace", user_namespace]
    try:
        helm_output = subprocess.check_output(command, stderr=subprocess.STDOUT)
        values_yaml = helm_output.decode('utf-8')

        # Convert YAML to JSON
        values_json = yaml.safe_load(values_yaml)  # Assumes PyYAML or similar package is used

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

        return JsonResponse({'values': specific_values})

    except subprocess.CalledProcessError as e:
        return JsonResponse({'error': 'Failed to retrieve Helm release values',
                             'details': e.output.decode('utf-8')}, status=500)

    except Exception as e:
        return JsonResponse({'error': 'An unexpected error occurred',
                             'details': str(e)}, status=500)

###MULTIUE - CU###
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def values_multiue_cu(request):
    user_namespace = f"{request.user.username}"

    # Execute helm get values command
    command = ["helm", "get", "values", "multiue-cu", "--namespace", user_namespace]
    try:
        helm_output = subprocess.check_output(command, stderr=subprocess.STDOUT)
        values_yaml = helm_output.decode('utf-8')

        # Convert YAML to JSON
        values_json = yaml.safe_load(values_yaml)  # Assumes PyYAML or similar package is used

        # It seems like the structure might differ. Make sure to access the correct path.
        # Extract specific values assuming 'values' is the top-level key as per your example.
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
        return JsonResponse({'values': specific_values})

    except subprocess.CalledProcessError as e:
        return JsonResponse({'error': 'Failed to retrieve Helm release values',
                             'details': e.output.decode('utf-8')}, status=500)

    except Exception as e:
        return JsonResponse({'error': 'An unexpected error occurred',
                             'details': str(e)}, status=500)

###MULTIUE - DU###
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def values_multiue_du(request):
    user_namespace = f"{request.user.username}"

    # Execute helm get values command
    command = ["helm", "get", "values", "multiue-du", "--namespace", user_namespace]
    try:
        helm_output = subprocess.check_output(command, stderr=subprocess.STDOUT)
        values_yaml = helm_output.decode('utf-8')

        # Convert YAML to JSON
        values_json = yaml.safe_load(values_yaml)  # Assumes PyYAML or similar package is used

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

        return JsonResponse({'values': specific_values})

    except subprocess.CalledProcessError as e:
        return JsonResponse({'error': 'Failed to retrieve Helm release values',
                             'details': e.output.decode('utf-8')}, status=500)

    except Exception as e:
        return JsonResponse({'error': 'An unexpected error occurred',
                             'details': str(e)}, status=500)

###MULTIUE - UE1###
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def values_multiue_ue1(request):
    user_namespace = f"{request.user.username}"

    # Execute helm get values command
    command = ["helm", "get", "values", "multiue-ue1", "--namespace", user_namespace]
    try:
        helm_output = subprocess.check_output(command, stderr=subprocess.STDOUT)
        values_yaml = helm_output.decode('utf-8')

        # Convert YAML to JSON
        values_json = yaml.safe_load(values_yaml)  # Assumes PyYAML or similar package is used

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

        return JsonResponse({'values': specific_values})

    except subprocess.CalledProcessError as e:
        return JsonResponse({'error': 'Failed to retrieve Helm release values',
                             'details': e.output.decode('utf-8')}, status=500)

    except Exception as e:
        return JsonResponse({'error': 'An unexpected error occurred',
                             'details': str(e)}, status=500)

###MULTIUE - UE2###
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def values_multiue_ue2(request):
    user_namespace = f"{request.user.username}"

    # Execute helm get values command
    command = ["helm", "get", "values", "multiue-ue2", "--namespace", user_namespace]
    try:
        helm_output = subprocess.check_output(command, stderr=subprocess.STDOUT)
        values_yaml = helm_output.decode('utf-8')

        # Convert YAML to JSON
        values_json = yaml.safe_load(values_yaml)  # Assumes PyYAML or similar package is used

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

        return JsonResponse({'values': specific_values})

    except subprocess.CalledProcessError as e:
        return JsonResponse({'error': 'Failed to retrieve Helm release values',
                             'details': e.output.decode('utf-8')}, status=500)

    except Exception as e:
        return JsonResponse({'error': 'An unexpected error occurred',
                             'details': str(e)}, status=500)


###SINGLE - CU###
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def config_single_cu(request):
    username = request.user.username
    namespace = f"{username}"

    # Store the original name and update with the new name
    with open(SINGLE_CU_CHART_FILE_PATH, 'r') as file:
        chart_yaml = yaml.safe_load(file)
        original_name = chart_yaml['name']
    update_chart_name(SINGLE_CU_CHART_FILE_PATH, username)

    try:
        # Get current values
        get_values_command = ["helm", "get", "values", "single-cu", "--namespace", namespace, "--output", "yaml"]
        current_values_yaml = subprocess.check_output(get_values_command).decode("utf-8")
        current_values = yaml.safe_load(current_values_yaml)

        # Iterate over expected fields and update if provided in JSON body
        expected_fields = {
            'cu_id': ['config', 'cuId'],
            'cell_id': ['config', 'cellId'],
            'f1_int': ['multus', 'f1Interface', 'IPadd'],
            'f1_cuport': ['config', 'f1cuPort'],
            'f1_duport': ['config', 'f1duPort'],
            'n2_int': ['multus', 'n2Interface', 'IPadd'],
            'n3_int': ['multus', 'n3Interface', 'IPadd'],
            'mcc': ['config', 'mcc'],
            'mnc': ['config', 'mnc'],
            'tac': ['config', 'tac'],
            'sst': ['config', 'sst'],
            'amf_host': ['config', 'amfhost']
        }

        # Update the current_values based on the provided JSON data
        for field, path in expected_fields.items():
            value = request.data.get(field)
            if value:
                target = current_values
                for key in path[:-1]:
                    target = target.setdefault(key, {})
                target[path[-1]] = value

        # Save the updated values to a YAML file
        updated_values_yaml = yaml.dump(current_values)
        with open('updated_values.yaml', 'w') as temp_file:
            temp_file.write(updated_values_yaml)

        # Execute Helm upgrade command with the updated values
        upgrade_command = [
            "helm", "upgrade", "single-cu", SINGLE_CU_BASE_DIR,
            "--namespace", namespace,
            "-f", 'updated_values.yaml'
        ]
        subprocess.run(upgrade_command, check=True)
        os.remove('updated_values.yaml')

        return Response({"message": "Configuration Updated Successfully"}, status=status.HTTP_200_OK)

    except subprocess.CalledProcessError as e:
        return Response({"message": f"Error upgrading Helm chart: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
    finally:
        # Revert the chart name back to its original
        revert_chart_name(SINGLE_CU_CHART_FILE_PATH, original_name)

###SINGLE - DU###
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def config_single_du(request):
    namespace = f"{request.user.username}"

    # Get the current configuration from Helm
    get_values_command = ["helm", "get", "values", "single-du", "--namespace", namespace, "--output", "yaml"]
    current_values_yaml = subprocess.check_output(get_values_command).decode("utf-8")
    current_values = yaml.safe_load(current_values_yaml)

    # Dictionary to map JSON keys to their path in the YAML data structure
    field_mappings = {
        'gnb_id': ['config', 'gnbId'],
        'du_id': ['config', 'duId'],
        'cell_id': ['config', 'cellId'],
        'f1_int': ['multus', 'f1Interface', 'IPadd'],
        'f1_cuport': ['config', 'f1cuPort'],
        'f1_duport': ['config', 'f1duPort'],
        'mcc': ['config', 'mcc'],
        'mnc': ['config', 'mnc'],
        'tac': ['config', 'tac'],
        'sst': ['config', 'sst'],
        'usrp': ['config', 'usrp'],
        'cu_host': ['config', 'cuHost']
    }

    # Update the YAML data structure based on the provided JSON data
    for field, path in field_mappings.items():
        # Check if the field is provided and not empty
        value = request.data.get(field)
        if value:
            # Navigate through the path to set the value
            target = current_values
            for key in path[:-1]:
                target = target.setdefault(key, {})
            target[path[-1]] = value
    
    # Convert updated values back to YAML string
    updated_values_yaml = yaml.dump(current_values)

    # Use a temporary file to pass the updated values to the helm upgrade command
    with open('updated_values.yaml', 'w') as temp_file:
        temp_file.write(updated_values_yaml)
    
    # Execute Helm upgrade command with the updated values
    upgrade_command = [
        "helm", "upgrade", "single-du", SINGLE_DU_BASE_DIR,
        "--namespace", namespace,
        "-f", 'updated_values.yaml'
    ]
    subprocess.run(upgrade_command)
    os.remove('updated_values.yaml')

    return Response({"message": "Configuration Updated Successfully"}, status=status.HTTP_200_OK)

###SINGLE - UE###
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def config_single_ue(request):
    namespace = f"{request.user.username}"

    # Get the current configuration from Helm
    get_values_command = ["helm", "get", "values", "single-ue", "--namespace", namespace, "--output", "yaml"]
    current_values_yaml = subprocess.check_output(get_values_command).decode("utf-8")
    current_values = yaml.safe_load(current_values_yaml)

    # Dictionary to map JSON keys to their path in the YAML data structure
    field_mappings = {
        'multus_ipadd': ['multus', 'ipadd'],
        'rfsimserver': ['config', 'rfSimServer'],
        'fullimsi': ['config', 'fullImsi'],
        'fullkey': ['config', 'fullKey'],
        'opc': ['config', 'opc'],
        'dnn': ['config', 'dnn'],
        'sst': ['config', 'sst'],
        'sd': ['config', 'sd'],
        'usrp': ['config', 'usrp']
    }

    # Update the YAML data structure based on the provided JSON data
    for field, path in field_mappings.items():
        # Check if the field is provided and not empty
        value = request.data.get(field)
        if value:
            # Navigate through the path to set the value
            target = current_values
            for key in path[:-1]:
                target = target.setdefault(key, {})
            target[path[-1]] = value
    
    # Convert updated values back to YAML string
    updated_values_yaml = yaml.dump(current_values)

    # Use a temporary file to pass the updated values to the helm upgrade command
    with open('updated_values.yaml', 'w') as temp_file:
        temp_file.write(updated_values_yaml)
    
    # Execute Helm upgrade command with the updated values
    upgrade_command = [
        "helm", "upgrade", "single-ue", SINGLE_UE_BASE_DIR,
        "--namespace", namespace,
        "-f", 'updated_values.yaml'
    ]
    subprocess.run(upgrade_command)
    os.remove('updated_values.yaml')

    return Response({"message": "Configuration Updated Successfully"}, status=status.HTTP_200_OK)


###MULTIGNB - CU###
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def config_multignb_cu(request):
    namespace = f"{request.user.username}"

    # Get current values
    get_values_command = ["helm", "get", "values", "multignb-cu", "--namespace", namespace, "--output", "yaml"]
    current_values_yaml = subprocess.check_output(get_values_command).decode("utf-8")
    current_values = yaml.safe_load(current_values_yaml)

    # Iterate over expected fields and update if provided in JSON body
    expected_fields = {
        'cu_id': ['config', 'cuId'],
        'cell_id': ['config', 'cellId'],
        'f1_int': ['multus', 'f1Interface', 'IPadd'],
        'f1_cuport': ['config', 'f1cuPort'],
        'f1_duport': ['config', 'f1duPort'],
        'n2_int': ['multus', 'n2Interface', 'IPadd'],
        'n3_int': ['multus', 'n3Interface', 'IPadd'],
        'mcc': ['config', 'mcc'],
        'mnc': ['config', 'mnc'],
        'tac': ['config', 'tac'],
        'sst': ['config', 'sst'],
        'amf_host': ['config', 'amfhost']
    }

    # Update the current_values based on the provided JSON data
    for field, path in expected_fields.items():
        value = request.data.get(field)
        if value:
            target = current_values
            for key in path[:-1]:
                target = target.setdefault(key, {})
            target[path[-1]] = value
    
    # Convert updated values back to YAML string
    updated_values_yaml = yaml.dump(current_values)

    # Use a temporary file to pass the updated values to the helm upgrade command
    with open('updated_values.yaml', 'w') as temp_file:
        temp_file.write(updated_values_yaml)
    
    # Execute Helm upgrade command with the updated values
    upgrade_command = [
        "helm", "upgrade", "multignb-cu", MULTIGNB_CU_BASE_DIR,
        "--namespace", namespace,
        "-f", 'updated_values.yaml'
    ]
    subprocess.run(upgrade_command)
    os.remove('updated_values.yaml')

    return Response({"message": "Configuration Updated Successfully"}, status=status.HTTP_200_OK)

###MULTIGNB - DU1###
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def config_multignb_du1(request):
    namespace = f"{request.user.username}"

    # Get the current configuration from Helm
    get_values_command = ["helm", "get", "values", "multignb-du1", "--namespace", namespace, "--output", "yaml"]
    current_values_yaml = subprocess.check_output(get_values_command).decode("utf-8")
    current_values = yaml.safe_load(current_values_yaml)

    # Dictionary to map JSON keys to their path in the YAML data structure
    field_mappings = {
        'gnb_id': ['config', 'gnbId'],
        'du_id': ['config', 'duId'],
        'cell_id': ['config', 'cellId'],
        'phycell_id': ['config', 'phyCellId'],
        'f1_int': ['multus', 'f1Interface', 'IPadd'],
        'f1_cuport': ['config', 'f1cuPort'],
        'f1_duport': ['config', 'f1duPort'],
        'mcc': ['config', 'mcc'],
        'mnc': ['config', 'mnc'],
        'tac': ['config', 'tac'],
        'sst': ['config', 'sst'],
        'usrp': ['config', 'usrp'],
        'cu_host': ['config', 'cuHost']
    }

    # Update the YAML data structure based on the provided JSON data
    for field, path in field_mappings.items():
        # Check if the field is provided and not empty
        value = request.data.get(field)
        if value:
            # Navigate through the path to set the value
            target = current_values
            for key in path[:-1]:
                target = target.setdefault(key, {})
            target[path[-1]] = value

    # Convert updated values back to YAML string
    updated_values_yaml = yaml.dump(current_values)

    # Use a temporary file to pass the updated values to the helm upgrade command
    with open('updated_values.yaml', 'w') as temp_file:
        temp_file.write(updated_values_yaml)
    
    # Execute Helm upgrade command with the updated values
    upgrade_command = [
        "helm", "upgrade", "multignb-du1", MULTIGNB_DU1_BASE_DIR,
        "--namespace", namespace,
        "-f", 'updated_values.yaml'
    ]
    subprocess.run(upgrade_command)
    os.remove('updated_values.yaml')

    return Response({"message": "Configuration Updated Successfully"}, status=status.HTTP_200_OK)

###MULTIGNB - DU2###
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def config_multignb_du2(request):
    namespace = f"{request.user.username}"

    # Get the current configuration from Helm
    get_values_command = ["helm", "get", "values", "multignb-du2", "--namespace", namespace, "--output", "yaml"]
    current_values_yaml = subprocess.check_output(get_values_command).decode("utf-8")
    current_values = yaml.safe_load(current_values_yaml)

    # Dictionary to map JSON keys to their path in the YAML data structure
    field_mappings = {
        'gnb_id': ['config', 'gnbId'],
        'du_id': ['config', 'duId'],
        'cell_id': ['config', 'cellId'],
        'phycell_id': ['config', 'phyCellId'],
        'f1_int': ['multus', 'f1Interface', 'IPadd'],
        'f1_cuport': ['config', 'f1cuPort'],
        'f1_duport': ['config', 'f1duPort'],
        'mcc': ['config', 'mcc'],
        'mnc': ['config', 'mnc'],
        'tac': ['config', 'tac'],
        'sst': ['config', 'sst'],
        'usrp': ['config', 'usrp'],
        'cu_host': ['config', 'cuHost']
    }

    # Update the YAML data structure based on the provided JSON data
    for field, path in field_mappings.items():
        # Check if the field is provided and not empty
        value = request.data.get(field)
        if value:
            # Navigate through the path to set the value
            target = current_values
            for key in path[:-1]:
                target = target.setdefault(key, {})
            target[path[-1]] = value
    
    # Convert updated values back to YAML string
    updated_values_yaml = yaml.dump(current_values)

    # Use a temporary file to pass the updated values to the helm upgrade command
    with open('updated_values.yaml', 'w') as temp_file:
        temp_file.write(updated_values_yaml)
    
    # Execute Helm upgrade command with the updated values
    upgrade_command = [
        "helm", "upgrade", "multignb-du2", MULTIGNB_DU2_BASE_DIR,
        "--namespace", namespace,
        "-f", 'updated_values.yaml'
    ]
    subprocess.run(upgrade_command)
    os.remove('updated_values.yaml')

    return Response({"message": "Configuration Updated Successfully"}, status=status.HTTP_200_OK)

###MULTIGNB - UE1###
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def config_multignb_ue1(request):
    namespace = f"{request.user.username}"

    # Get the current configuration from Helm
    get_values_command = ["helm", "get", "values", "multignb-ue1", "--namespace", namespace, "--output", "yaml"]
    current_values_yaml = subprocess.check_output(get_values_command).decode("utf-8")
    current_values = yaml.safe_load(current_values_yaml)

    # Dictionary to map JSON keys to their path in the YAML data structure
    field_mappings = {
        'multus_ipadd': ['multus', 'ipadd'],
        'rfsimserver': ['config', 'rfSimServer'],
        'fullimsi': ['config', 'fullImsi'],
        'fullkey': ['config', 'fullKey'],
        'opc': ['config', 'opc'],
        'dnn': ['config', 'dnn'],
        'sst': ['config', 'sst'],
        'sd': ['config', 'sd'],
        'usrp': ['config', 'usrp']
    }

    # Update the YAML data structure based on the provided JSON data
    for field, path in field_mappings.items():
        # Check if the field is provided and not empty
        value = request.data.get(field)
        if value:
            # Navigate through the path to set the value
            target = current_values
            for key in path[:-1]:
                target = target.setdefault(key, {})
            target[path[-1]] = value
    
    # Convert updated values back to YAML string
    updated_values_yaml = yaml.dump(current_values)

    # Use a temporary file to pass the updated values to the helm upgrade command
    with open('updated_values.yaml', 'w') as temp_file:
        temp_file.write(updated_values_yaml)
    
    # Execute Helm upgrade command with the updated values
    upgrade_command = [
        "helm", "upgrade", "multignb-ue", MULTIGNB_UE1_BASE_DIR,
        "--namespace", namespace,
        "-f", 'updated_values.yaml'
    ]
    subprocess.run(upgrade_command)
    os.remove('updated_values.yaml')

    return Response({"message": "Configuration Updated Successfully"}, status=status.HTTP_200_OK)

###MULTIGNB - UE2###
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def config_multignb_ue2(request):
    namespace = f"{request.user.username}"

    # Get the current configuration from Helm
    get_values_command = ["helm", "get", "values", "multignb-ue2", "--namespace", namespace, "--output", "yaml"]
    current_values_yaml = subprocess.check_output(get_values_command).decode("utf-8")
    current_values = yaml.safe_load(current_values_yaml)

    # Dictionary to map JSON keys to their path in the YAML data structure
    field_mappings = {
        'multus_ipadd': ['multus', 'ipadd'],
        'rfsimserver': ['config', 'rfSimServer'],
        'fullimsi': ['config', 'fullImsi'],
        'fullkey': ['config', 'fullKey'],
        'opc': ['config', 'opc'],
        'dnn': ['config', 'dnn'],
        'sst': ['config', 'sst'],
        'sd': ['config', 'sd'],
        'usrp': ['config', 'usrp']
    }

    # Update the YAML data structure based on the provided JSON data
    for field, path in field_mappings.items():
        # Check if the field is provided and not empty
        value = request.data.get(field)
        if value:
            # Navigate through the path to set the value
            target = current_values
            for key in path[:-1]:
                target = target.setdefault(key, {})
            target[path[-1]] = value
    
    # Convert updated values back to YAML string
    updated_values_yaml = yaml.dump(current_values)

    # Use a temporary file to pass the updated values to the helm upgrade command
    with open('updated_values.yaml', 'w') as temp_file:
        temp_file.write(updated_values_yaml)
    
    # Execute Helm upgrade command with the updated values
    upgrade_command = [
        "helm", "upgrade", "multignb-ue", MULTIGNB_UE2_BASE_DIR,
        "--namespace", namespace,
        "-f", 'updated_values.yaml'
    ]
    subprocess.run(upgrade_command)
    os.remove('updated_values.yaml')

    return Response({"message": "Configuration Updated Successfully"}, status=status.HTTP_200_OK)


###MULTIUE - CU###
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def config_multiue_cu(request):
    namespace = f"{request.user.username}"

    # Get current values
    get_values_command = ["helm", "get", "values", "multiue-cu", "--namespace", namespace, "--output", "yaml"]
    current_values_yaml = subprocess.check_output(get_values_command).decode("utf-8")
    current_values = yaml.safe_load(current_values_yaml)

    # Iterate over expected fields and update if provided in JSON body
    expected_fields = {
        'cu_id': ['config', 'cuId'],
        'cell_id': ['config', 'cellId'],
        'f1_int': ['multus', 'f1Interface', 'IPadd'],
        'f1_cuport': ['config', 'f1cuPort'],
        'f1_duport': ['config', 'f1duPort'],
        'n2_int': ['multus', 'n2Interface', 'IPadd'],
        'n3_int': ['multus', 'n3Interface', 'IPadd'],
        'mcc': ['config', 'mcc'],
        'mnc': ['config', 'mnc'],
        'tac': ['config', 'tac'],
        'sst': ['config', 'sst'],
        'amf_host': ['config', 'amfhost']
    }

    # Update the current_values based on the provided JSON data
    for field, path in expected_fields.items():
        value = request.data.get(field)
        if value:
            target = current_values
            for key in path[:-1]:
                target = target.setdefault(key, {})
            target[path[-1]] = value
    
    # Convert updated values back to YAML string
    updated_values_yaml = yaml.dump(current_values)

    # Use a temporary file to pass the updated values to the helm upgrade command
    with open('updated_values.yaml', 'w') as temp_file:
        temp_file.write(updated_values_yaml)
    
    # Execute Helm upgrade command with the updated values
    upgrade_command = [
        "helm", "upgrade", "multiue-cu", MULTIUE_CU_BASE_DIR,
        "--namespace", namespace,
        "-f", 'updated_values.yaml'
    ]
    subprocess.run(upgrade_command)
    os.remove('updated_values.yaml')

    return Response({"message": "Configuration Updated Successfully"}, status=status.HTTP_200_OK)

###MULTIUE - DU###
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def config_multiue_du(request):
    namespace = f"{request.user.username}"

    # Get the current configuration from Helm
    get_values_command = ["helm", "get", "values", "multiue-du", "--namespace", namespace, "--output", "yaml"]
    current_values_yaml = subprocess.check_output(get_values_command).decode("utf-8")
    current_values = yaml.safe_load(current_values_yaml)

    # Dictionary to map JSON keys to their path in the YAML data structure
    field_mappings = {
        'gnb_id': ['config', 'gnbId'],
        'du_id': ['config', 'duId'],
        'cell_id': ['config', 'cellId'],
        'f1_int': ['multus', 'f1Interface', 'IPadd'],
        'f1_cuport': ['config', 'f1cuPort'],
        'f1_duport': ['config', 'f1duPort'],
        'mcc': ['config', 'mcc'],
        'mnc': ['config', 'mnc'],
        'tac': ['config', 'tac'],
        'sst': ['config', 'sst'],
        'usrp': ['config', 'usrp'],
        'cu_host': ['config', 'cuHost']
    }

    # Update the YAML data structure based on the provided JSON data
    for field, path in field_mappings.items():
        # Check if the field is provided and not empty
        value = request.data.get(field)
        if value:
            # Navigate through the path to set the value
            target = current_values
            for key in path[:-1]:
                target = target.setdefault(key, {})
            target[path[-1]] = value
    
    # Convert updated values back to YAML string
    updated_values_yaml = yaml.dump(current_values)

    # Use a temporary file to pass the updated values to the helm upgrade command
    with open('updated_values.yaml', 'w') as temp_file:
        temp_file.write(updated_values_yaml)
    
    # Execute Helm upgrade command with the updated values
    upgrade_command = [
        "helm", "upgrade", "multiue-du", MULTIUE_DU_BASE_DIR,
        "--namespace", namespace,
        "-f", 'updated_values.yaml'
    ]
    subprocess.run(upgrade_command)
    os.remove('updated_values.yaml')

    return Response({"message": "Configuration Updated Successfully"}, status=status.HTTP_200_OK)

###MULTIUE - UE1###
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def config_multiue_ue1(request):
    namespace = f"{request.user.username}"

    # Get the current configuration from Helm
    get_values_command = ["helm", "get", "values", "multiue-ue1", "--namespace", namespace, "--output", "yaml"]
    current_values_yaml = subprocess.check_output(get_values_command).decode("utf-8")
    current_values = yaml.safe_load(current_values_yaml)

    # Dictionary to map JSON keys to their path in the YAML data structure
    field_mappings = {
        'multus_ipadd': ['multus', 'ipadd'],
        'rfsimserver': ['config', 'rfSimServer'],
        'fullimsi': ['config', 'fullImsi'],
        'fullkey': ['config', 'fullKey'],
        'opc': ['config', 'opc'],
        'dnn': ['config', 'dnn'],
        'sst': ['config', 'sst'],
        'sd': ['config', 'sd'],
        'usrp': ['config', 'usrp']
    }

    # Update the YAML data structure based on the provided JSON data
    for field, path in field_mappings.items():
        # Check if the field is provided and not empty
        value = request.data.get(field)
        if value:
            # Navigate through the path to set the value
            target = current_values
            for key in path[:-1]:
                target = target.setdefault(key, {})
            target[path[-1]] = value
    
    # Convert updated values back to YAML string
    updated_values_yaml = yaml.dump(current_values)

    # Use a temporary file to pass the updated values to the helm upgrade command
    with open('updated_values.yaml', 'w') as temp_file:
        temp_file.write(updated_values_yaml)
    
    # Execute Helm upgrade command with the updated values
    upgrade_command = [
        "helm", "upgrade", "multiue-ue1", MULTIUE_UE1_BASE_DIR,
        "--namespace", namespace,
        "-f", 'updated_values.yaml'
    ]
    subprocess.run(upgrade_command)
    os.remove('updated_values.yaml')

    return Response({"message": "Configuration Updated Successfully"}, status=status.HTTP_200_OK)

###MULTIUE - UE2###
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def config_multiue_ue2(request):
    namespace = f"{request.user.username}"

    # Get the current configuration from Helm
    get_values_command = ["helm", "get", "values", "multiue-ue2", "--namespace", namespace, "--output", "yaml"]
    current_values_yaml = subprocess.check_output(get_values_command).decode("utf-8")
    current_values = yaml.safe_load(current_values_yaml)

    # Dictionary to map JSON keys to their path in the YAML data structure
    field_mappings = {
        'multus_ipadd': ['multus', 'ipadd'],
        'rfsimserver': ['config', 'rfSimServer'],
        'fullimsi': ['config', 'fullImsi'],
        'fullkey': ['config', 'fullKey'],
        'opc': ['config', 'opc'],
        'dnn': ['config', 'dnn'],
        'sst': ['config', 'sst'],
        'sd': ['config', 'sd'],
        'usrp': ['config', 'usrp']
    }

    # Update the YAML data structure based on the provided JSON data
    for field, path in field_mappings.items():
        # Check if the field is provided and not empty
        value = request.data.get(field)
        if value:
            # Navigate through the path to set the value
            target = current_values
            for key in path[:-1]:
                target = target.setdefault(key, {})
            target[path[-1]] = value
    
    # Convert updated values back to YAML string
    updated_values_yaml = yaml.dump(current_values)

    # Use a temporary file to pass the updated values to the helm upgrade command
    with open('updated_values.yaml', 'w') as temp_file:
        temp_file.write(updated_values_yaml)
    
    # Execute Helm upgrade command with the updated values
    upgrade_command = [
        "helm", "upgrade", "multiue-ue2", MULTIUE_UE2_BASE_DIR,
        "--namespace", namespace,
        "-f", 'updated_values.yaml'
    ]
    subprocess.run(upgrade_command)
    os.remove('updated_values.yaml')

    return Response({"message": "Configuration Updated Successfully"}, status=status.HTTP_200_OK)


###SINGLE CU - START###
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_single_cu(request):
    try:
        username = request.user.username  # Get the currently logged-in user's username
        namespace = f"{username}"  # Construct the namespace based on the username
        deployment_name = f"oai-cu-level1-{username}"  # Dynamically create the deployment name

        subprocess.run([
            "kubectl", "scale", "deployment", deployment_name, "--replicas=1",
            "--namespace=" + namespace
        ])
        return Response({"message": "CU successfully started"}, status=status.HTTP_200_OK)
    except subprocess.CalledProcessError as e:
        return Response({"error": f"An error occurred: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

###SINGLE DU - START###
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_single_du(request):
    try:
        username = request.user.username  # Get the currently logged-in user's username
        namespace = f"{username}"  # Construct the namespace based on the username
        deployment_name = f"oai-du-level1-{username}"  # Dynamically create the deployment name

        subprocess.run([
            "kubectl", "scale", "deployment", deployment_name, "--replicas=1",
            "--namespace=" + namespace
        ])
        return Response({"message": "DU successfully started"}, status=status.HTTP_200_OK)
    except subprocess.CalledProcessError as e:
        return Response({"error": f"An error occurred: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

###SINGLE UE - START###
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_single_ue(request):
    try:
        username = request.user.username  # Get the currently logged-in user's username
        namespace = f"{username}"  # Construct the namespace based on the username
        deployment_name = f"oai-nr-ue-level1-{username}"  # Dynamically create the deployment name

        subprocess.run([
            "kubectl", "scale", "deployment", deployment_name, "--replicas=1",
            "--namespace=" + namespace
        ])
        return Response({"message": "UE successfully started"}, status=status.HTTP_200_OK)
    except subprocess.CalledProcessError as e:
        return Response({"error": f"An error occurred: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

###MULTIGNB CU - START###
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_multignb_cu(request):
    try:
        username = request.user.username  # Get the currently logged-in user's username
        namespace = f"{username}"  # Construct the namespace based on the username
        deployment_name = f"oai-cu-level2-{username}"  # Dynamically create the deployment name

        subprocess.run([
            "kubectl", "scale", "deployment", deployment_name, "--replicas=1",
            "--namespace=" + namespace
        ])
        return Response({"message": "CU successfully started"}, status=status.HTTP_200_OK)
    except subprocess.CalledProcessError as e:
        return Response({"error": f"An error occurred: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

###MULTIGNB DU1 - START###
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_multignb_du1(request):
    try:
        username = request.user.username  # Get the currently logged-in user's username
        namespace = f"{username}"  # Construct the namespace based on the username
        deployment_name = f"oai-du1-level2-{username}"  # Dynamically create the deployment name

        subprocess.run([
            "kubectl", "scale", "deployment", deployment_name, "--replicas=1",
            "--namespace=" + namespace
        ])
        return Response({"message": "DU successfully started"}, status=status.HTTP_200_OK)
    except subprocess.CalledProcessError as e:
        return Response({"error": f"An error occurred: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

###MULTIGNB DU2 - START###
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_multignb_du2(request):
    try:
        username = request.user.username  # Get the currently logged-in user's username
        namespace = f"{username}"  # Construct the namespace based on the username
        deployment_name = f"oai-du2-level2-{username}"  # Dynamically create the deployment name

        subprocess.run([
            "kubectl", "scale", "deployment", deployment_name, "--replicas=1",
            "--namespace=" + namespace
        ])
        return Response({"message": "DU successfully started"}, status=status.HTTP_200_OK)
    except subprocess.CalledProcessError as e:
        return Response({"error": f"An error occurred: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

###MULTIGNB UE1 - START###
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_multignb_ue1(request):
    try:
        username = request.user.username  # Get the currently logged-in user's username
        namespace = f"{username}"  # Construct the namespace based on the username
        deployment_name = f"oai-nr-ue1-level2-{username}"  # Dynamically create the deployment name

        subprocess.run([
            "kubectl", "scale", "deployment", deployment_name, "--replicas=1",
            "--namespace=" + namespace
        ])
        return Response({"message": "UE successfully started"}, status=status.HTTP_200_OK)
    except subprocess.CalledProcessError as e:
        return Response({"error": f"An error occurred: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

###MULTIGNB UE2 - START###
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_multignb_ue2(request):
    try:
        username = request.user.username  # Get the currently logged-in user's username
        namespace = f"{username}"  # Construct the namespace based on the username
        deployment_name = f"oai-nr-ue2-level2-{username}"  # Dynamically create the deployment name

        subprocess.run([
            "kubectl", "scale", "deployment", deployment_name, "--replicas=1",
            "--namespace=" + namespace
        ])
        return Response({"message": "UE successfully started"}, status=status.HTTP_200_OK)
    except subprocess.CalledProcessError as e:
        return Response({"error": f"An error occurred: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

###MULTIUE CU - START###
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_multiue_cu(request):
    try:
        username = request.user.username  # Get the currently logged-in user's username
        namespace = f"{username}"  # Construct the namespace based on the username
        deployment_name = f"oai-cu-level3-{username}"  # Dynamically create the deployment name

        subprocess.run([
            "kubectl", "scale", "deployment", deployment_name, "--replicas=1",
            "--namespace=" + namespace
        ])
        return Response({"message": "CU successfully started"}, status=status.HTTP_200_OK)
    except subprocess.CalledProcessError as e:
        return Response({"error": f"An error occurred: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

###MULTIUE DU - START###
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_multiue_du(request):
    try:
        username = request.user.username  # Get the currently logged-in user's username
        namespace = f"{username}"  # Construct the namespace based on the username
        deployment_name = f"oai-du-level3-{username}"  # Dynamically create the deployment name

        subprocess.run([
            "kubectl", "scale", "deployment", deployment_name, "--replicas=1",
            "--namespace=" + namespace
        ])
        return Response({"message": "DU successfully started"}, status=status.HTTP_200_OK)
    except subprocess.CalledProcessError as e:
        return Response({"error": f"An error occurred: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

###MULTIUE UE1 - START###
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_multiue_ue1(request):
    try:
        username = request.user.username  # Get the currently logged-in user's username
        namespace = f"{username}"  # Construct the namespace based on the username
        deployment_name = f"oai-nr-ue1-level3-{username}"  # Dynamically create the deployment name

        subprocess.run([
            "kubectl", "scale", "deployment", deployment_name, "--replicas=1",
            "--namespace=" + namespace
        ])
        return Response({"message": "UE successfully started"}, status=status.HTTP_200_OK)
    except subprocess.CalledProcessError as e:
        return Response({"error": f"An error occurred: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

###MULTIUE UE2 - START###
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_multiue_ue2(request):
    try:
        username = request.user.username  # Get the currently logged-in user's username
        namespace = f"{username}"  # Construct the namespace based on the username
        deployment_name = f"oai-nr-ue2-level3-{username}"  # Dynamically create the deployment name

        subprocess.run([
            "kubectl", "scale", "deployment", deployment_name, "--replicas=1",
            "--namespace=" + namespace
        ])
        return Response({"message": "UE successfully started"}, status=status.HTTP_200_OK)
    except subprocess.CalledProcessError as e:
        return Response({"error": f"An error occurred: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


###SINGLE CU - STOP###
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def stop_single_cu(request):
    try:
        username = request.user.username  # Get the currently logged-in user's username
        namespace = f"{username}"  # Construct the namespace based on the username
        deployment_name = f"oai-cu-level1-{username}"  # Dynamically create the deployment name

        subprocess.run([
            "kubectl", "scale", "deployment", deployment_name, "--replicas=0",
            "--namespace=" + namespace
        ])
        return Response({"message": "CU successfully stopped"}, status=status.HTTP_200_OK)
    except subprocess.CalledProcessError as e:
        return Response({"error": f"An error occurred: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

###SINGLE DU - STOP###
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def stop_single_du(request):
    try:
        username = request.user.username  # Get the currently logged-in user's username
        namespace = f"{username}"  # Construct the namespace based on the username
        deployment_name = f"oai-du-level1-{username}"  # Dynamically create the deployment name

        subprocess.run([
            "kubectl", "scale", "deployment", deployment_name, "--replicas=0",
            "--namespace=" + namespace
        ])
        return Response({"message": "DU successfully stopped"}, status=status.HTTP_200_OK)
    except subprocess.CalledProcessError as e:
        return Response({"error": f"An error occurred: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

###SINGLE UE - STOP###
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def stop_single_ue(request):
    try:
        username = request.user.username  # Get the currently logged-in user's username
        namespace = f"{username}"  # Construct the namespace based on the username
        deployment_name = f"oai-nr-ue-level1-{username}"  # Dynamically create the deployment name

        subprocess.run([
            "kubectl", "scale", "deployment", deployment_name, "--replicas=0",
            "--namespace=" + namespace
        ])
        return Response({"message": "UE successfully stopped"}, status=status.HTTP_200_OK)
    except subprocess.CalledProcessError as e:
        return Response({"error": f"An error occurred: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

###MULTIGNB CU - STOP###
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def stop_multignb_cu(request):
    try:
        username = request.user.username  # Get the currently logged-in user's username
        namespace = f"{username}"  # Construct the namespace based on the username
        deployment_name = f"oai-cu-level2-{username}"  # Dynamically create the deployment name

        subprocess.run([
            "kubectl", "scale", "deployment", deployment_name, "--replicas=0",
            "--namespace=" + namespace
        ])
        return Response({"message": "CU successfully stopped"}, status=status.HTTP_200_OK)
    except subprocess.CalledProcessError as e:
        return Response({"error": f"An error occurred: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

###MULTIGNB DU1 - STOP###
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def stop_multignb_du1(request):
    try:
        username = request.user.username  # Get the currently logged-in user's username
        namespace = f"{username}"  # Construct the namespace based on the username
        deployment_name = f"oai-du1-level2-{username}"  # Dynamically create the deployment name

        subprocess.run([
            "kubectl", "scale", "deployment", deployment_name, "--replicas=0",
            "--namespace=" + namespace
        ])
        return Response({"message": "DU-1 successfully stopped"}, status=status.HTTP_200_OK)
    except subprocess.CalledProcessError as e:
        return Response({"error": f"An error occurred: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

###MULTIGNB DU2 - STOP###
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def stop_multignb_du2(request):
    try:
        username = request.user.username  # Get the currently logged-in user's username
        namespace = f"{username}"  # Construct the namespace based on the username
        deployment_name = f"oai-du2-level2-{username}"  # Dynamically create the deployment name

        subprocess.run([
            "kubectl", "scale", "deployment", deployment_name, "--replicas=0",
            "--namespace=" + namespace
        ])
        return Response({"message": "DU-2 successfully stopped"}, status=status.HTTP_200_OK)
    except subprocess.CalledProcessError as e:
        return Response({"error": f"An error occurred: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

###MULTIGNB UE1 - STOP###
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def stop_multignb_ue1(request):
    try:
        username = request.user.username  # Get the currently logged-in user's username
        namespace = f"{username}"  # Construct the namespace based on the username
        deployment_name = f"oai-nr-ue1-level2-{username}"  # Dynamically create the deployment name

        subprocess.run([
            "kubectl", "scale", "deployment", deployment_name, "--replicas=0",
            "--namespace=" + namespace
        ])
        return Response({"message": "UE-1 successfully stopped"}, status=status.HTTP_200_OK)
    except subprocess.CalledProcessError as e:
        return Response({"error": f"An error occurred: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

###MULTIGNB UE2 - STOP###
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def stop_multignb_ue2(request):
    try:
        username = request.user.username  # Get the currently logged-in user's username
        namespace = f"{username}"  # Construct the namespace based on the username
        deployment_name = f"oai-nr-ue2-level2-{username}"  # Dynamically create the deployment name

        subprocess.run([
            "kubectl", "scale", "deployment", deployment_name, "--replicas=0",
            "--namespace=" + namespace
        ])
        return Response({"message": "UE-2 successfully stopped"}, status=status.HTTP_200_OK)
    except subprocess.CalledProcessError as e:
        return Response({"error": f"An error occurred: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

###MULTIUE CU - STOP###
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def stop_multiue_cu(request):
    try:
        username = request.user.username  # Get the currently logged-in user's username
        namespace = f"{username}"  # Construct the namespace based on the username
        deployment_name = f"oai-cu-level3-{username}"  # Dynamically create the deployment name

        subprocess.run([
            "kubectl", "scale", "deployment", deployment_name, "--replicas=0",
            "--namespace=" + namespace
        ])
        return Response({"message": "CU successfully stopped"}, status=status.HTTP_200_OK)
    except subprocess.CalledProcessError as e:
        return Response({"error": f"An error occurred: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

###MULTIUE DU - STOP###
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def stop_multiue_du(request):
    try:
        username = request.user.username  # Get the currently logged-in user's username
        namespace = f"{username}"  # Construct the namespace based on the username
        deployment_name = f"oai-du-level3-{username}"  # Dynamically create the deployment name

        subprocess.run([
            "kubectl", "scale", "deployment", deployment_name, "--replicas=0",
            "--namespace=" + namespace
        ])
        return Response({"message": "DU successfully stopped"}, status=status.HTTP_200_OK)
    except subprocess.CalledProcessError as e:
        return Response({"error": f"An error occurred: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

###MULTIUE UE1 - STOP###
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def stop_multiue_ue1(request):
    try:
        username = request.user.username  # Get the currently logged-in user's username
        namespace = f"{username}"  # Construct the namespace based on the username
        deployment_name = f"oai-nr-ue1-level3-{username}"  # Dynamically create the deployment name

        subprocess.run([
            "kubectl", "scale", "deployment", deployment_name, "--replicas=0",
            "--namespace=" + namespace
        ])
        return Response({"message": "UE-1 successfully stopped"}, status=status.HTTP_200_OK)
    except subprocess.CalledProcessError as e:
        return Response({"error": f"An error occurred: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

###MULTIUE UE2 - STOP###
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def stop_multiue_ue2(request):
    try:
        username = request.user.username  # Get the currently logged-in user's username
        namespace = f"{username}"  # Construct the namespace based on the username
        deployment_name = f"oai-nr-ue1-level3-{username}"  # Dynamically create the deployment name

        subprocess.run([
            "kubectl", "scale", "deployment", deployment_name, "--replicas=0",
            "--namespace=" + namespace
        ])
        return Response({"message": "UE-2 successfully stopped"}, status=status.HTTP_200_OK)
    except subprocess.CalledProcessError as e:
        return Response({"error": f"An error occurred: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_helm_deployments(request):
    # Construct the namespace from the username
    namespace = f"{request.user.username}"

    try:
        result = subprocess.run(
            ["helm", "list", "--namespace", namespace, "-q"],
            capture_output=True,
            text=True
        )

        # Split the output by newlines to get a list of deployments
        deployments = result.stdout.strip().split('\n')

        # Filter out any empty strings in case there are extra newlines
        deployments = [deployment for deployment in deployments if deployment]

        return Response({'deployments': deployments})

    except subprocess.CalledProcessError as e:
        # If there's an error executing the command, return the error
        return Response({'error': str(e)}, status=400)
