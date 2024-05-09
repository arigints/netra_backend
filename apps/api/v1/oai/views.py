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
    try:        
        original_names = {}

        # Store original names and update with new names
        for chart_file_path in [SINGLE_CU_CHART_FILE_PATH, SINGLE_DU_CHART_FILE_PATH, SINGLE_UE_CHART_FILE_PATH, MULTI_GNB_CU_CHART_FILE_PATH, MULTI_GNB_DU1_CHART_FILE_PATH, MULTI_GNB_DU2_CHART_FILE_PATH, MULTI_GNB_UE1_CHART_FILE_PATH, MULTI_GNB_UE2_CHART_FILE_PATH, MULTI_UE_CU_CHART_FILE_PATH, MULTI_UE_DU_CHART_FILE_PATH, MULTI_UE_UE1_CHART_FILE_PATH, MULTI_UE_UE2_CHART_FILE_PATH]:
            with open(chart_file_path, 'r') as file:
                chart_yaml = yaml.safe_load(file)
                original_names[chart_file_path] = chart_yaml['name']
            update_chart_name(chart_file_path, namespace)

        #SINGLE - CU
        subprocess.run([
            "helm", "install", "single-cu", "--values", "values.yaml",
            ".", "--namespace", namespace
        ], cwd=SINGLE_CU_BASE_DIR)

        #SINGLE - DU
        subprocess.run([
            "helm", "install", "single-du", "--values", "values.yaml",
            ".", "--namespace", namespace
        ], cwd=SINGLE_DU_BASE_DIR)

        #SINGLE - UE
        subprocess.run([
            "helm", "install", "single-ue", "--values", "values.yaml",
            ".", "--namespace", namespace
        ], cwd=SINGLE_UE_BASE_DIR)

        #MULTI-GNB - CU
        subprocess.run([
            "helm", "install", "multignb-cu", "--values", "values.yaml",
            ".", "--namespace", namespace
        ], cwd=MULTI_GNB_CU_BASE_DIR)

        #MULTI-GNB - DU1
        subprocess.run([
            "helm", "install", "multignb-du1", "--values", "values.yaml",
            ".", "--namespace", namespace
        ], cwd=MULTI_GNB_DU1_BASE_DIR)

        #MULTI-GNB - DU2
        subprocess.run([
            "helm", "install", "multignb-du2", "--values", "values.yaml",
            ".", "--namespace", namespace
        ], cwd=MULTI_GNB_DU2_BASE_DIR)

        #MULTI-GNB - UE1
        subprocess.run([
            "helm", "install", "multignb-ue1", "--values", "values.yaml",
            ".", "--namespace", namespace
        ], cwd=MULTI_GNB_UE1_BASE_DIR)

        #MULTI-GNB - UE2
        subprocess.run([
            "helm", "install", "multignb-ue2", "--values", "values.yaml",
            ".", "--namespace", namespace
        ], cwd=MULTI_GNB_UE2_BASE_DIR)

        #MULTI-UE - CU
        subprocess.run([
            "helm", "install", "multiue-cu", "--values", "values.yaml",
            ".", "--namespace", namespace
        ], cwd=MULTI_UE_CU_BASE_DIR)

        #MULTI-UE - DU
        subprocess.run([
            "helm", "install", "multiue-du", "--values", "values.yaml",
            ".", "--namespace", namespace
        ], cwd=MULTI_UE_DU_BASE_DIR)

        #MULTI-UE - UE1
        subprocess.run([
            "helm", "install", "multiue-ue1", "--values", "values.yaml",
            ".", "--namespace", namespace
        ], cwd=MULTI_UE_UE1_BASE_DIR)

        #MULTI-UE - UE2
        subprocess.run([
            "helm", "install", "multiue-ue2", "--values", "values.yaml",
            ".", "--namespace", namespace
        ], cwd=MULTI_UE_UE2_BASE_DIR)

        return "Success"

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
    namespace = f"{request.user.username}"

    get_values_command = ["helm", "get", "values", "single-cu", "--namespace", namespace, "--output", "yaml"]
    current_values_yaml = subprocess.check_output(get_values_command).decode("utf-8")
    current_values = yaml.safe_load(current_values_yaml)

    # Check if each field is provided in the form and update accordingly
    if 'cu_id' in request.POST and request.POST['cu_id']:
        current_values['config']['cuId'] = request.POST['cu_id']
    if 'cell_id' in request.POST and request.POST['cell_id']:
        current_values['config']['cellId'] = request.POST['cell_id']
    if 'f1_int' in request.POST and request.POST['f1_int']:
        current_values['multus']['f1Interface']['IPadd'] = request.POST['f1_int']
    if 'f1_cuport' in request.POST and request.POST['f1_cuport']:
        current_values['config']['f1cuPort'] = request.POST['f1_cuport']
    if 'f1_duport' in request.POST and request.POST['f1_duport']:
        current_values['config']['f1duPort'] = request.POST['f1_duport']
    if 'n2_int' in request.POST and request.POST['n2_int']:
        current_values['multus']['n2Interface']['IPadd'] = request.POST['n2_int']
    if 'n3_int' in request.POST and request.POST['n3_int']:
        current_values['multus']['n3Interface']['IPadd'] = request.POST['n3_int']
    if 'mcc' in request.POST and request.POST['mcc']:
        current_values['config']['mcc'] = request.POST['mcc']
    if 'mnc' in request.POST and request.POST['mnc']:
        current_values['config']['mnc'] = request.POST['mnc']
    if 'tac' in request.POST and request.POST['tac']:
        current_values['config']['tac'] = request.POST['tac']
    if 'sst' in request.POST and request.POST['sst']:
        current_values['config']['sst'] = request.POST['sst']
    if 'amf_host' in request.POST and request.POST['amf_host']:
        current_values['config']['amfhost'] = request.POST['amf_host']
    
    # Convert updated values back to YAML string
    updated_values_yaml = yaml.dump(current_values)

    # Use a temporary file to pass the updated values to the helm upgrade command
    with open('updated_values.yaml', 'w') as temp_file:
        temp_file.write(updated_values_yaml)
    
    # Execute Helm upgrade command with the updated values
    upgrade_command = [
        "helm", "upgrade", "single-cu", SINGLE_CU_BASE_DIR,
        "--namespace", namespace,
        "-f", 'updated_values.yaml'
    ]
    subprocess.run(upgrade_command)
    os.remove('updated_values.yaml')

    return Response({"message": "Configuration Updated Successfully"}, status=status.HTTP_200_OK)

###SINGLE - DU###
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def config_single_du(request):
    namespace = f"{request.user.username}"

    get_values_command = ["helm", "get", "values", "single-du", "--namespace", namespace, "--output", "yaml"]
    current_values_yaml = subprocess.check_output(get_values_command).decode("utf-8")
    current_values = yaml.safe_load(current_values_yaml)

    # Check if each field is provided in the form and update accordingly
    if 'gnb_id' in request.POST and request.POST['gnb_id']:
        current_values['config']['gnbId'] = request.POST['gnb_id']
    if 'du_id' in request.POST and request.POST['du_id']:
        current_values['config']['duId'] = request.POST['du_id']
    if 'cell_id' in request.POST and request.POST['cell_id']:
        current_values['config']['cellId'] = request.POST['cell_id']
    if 'f1_int' in request.POST and request.POST['f1_int']:
        current_values['multus']['f1Interface']['IPadd'] = request.POST['f1_int']
    if 'f1_cuport' in request.POST and request.POST['f1_cuport']:
        current_values['config']['f1cuPort'] = request.POST['f1_cuport']
    if 'f1_duport' in request.POST and request.POST['f1_duport']:
        current_values['config']['f1duPort'] = request.POST['f1_duport']
    if 'mcc' in request.POST and request.POST['mcc']:
        current_values['config']['mcc'] = request.POST['mcc']
    if 'mnc' in request.POST and request.POST['mnc']:
        current_values['config']['mnc'] = request.POST['mnc']
    if 'tac' in request.POST and request.POST['tac']:
        current_values['config']['tac'] = request.POST['tac']
    if 'sst' in request.POST and request.POST['sst']:
        current_values['config']['sst'] = request.POST['sst']
    if 'usrp' in request.POST and request.POST['usrp']:
        current_values['config']['usrp'] = request.POST['usrp']
    if 'cu_host' in request.POST and request.POST['cu_host']:
        current_values['config']['cuHost'] = request.POST['cu_host']
    
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

    get_values_command = ["helm", "get", "values", "single-ue", "--namespace", namespace, "--output", "yaml"]
    current_values_yaml = subprocess.check_output(get_values_command).decode("utf-8")
    current_values = yaml.safe_load(current_values_yaml)

    # Check if each field is provided in the form and update accordingly
    if 'multus_ipadd' in request.POST and request.POST['multus_ipadd']:
        current_values['multus']['ipadd'] = request.POST['multus_ipadd']
    if 'rfsimserver' in request.POST and request.POST['rfsimserver']:
        current_values['config']['rfSimServer'] = request.POST['rfsimserver']
    if 'fullimsi' in request.POST and request.POST['fullimsi']:
        current_values['config']['fullImsi'] = request.POST['fullimsi']
    if 'fullkey' in request.POST and request.POST['fullkey']:
        current_values['config']['fullKey'] = request.POST['fullkey']
    if 'opc' in request.POST and request.POST['opc']:
        current_values['config']['opc'] = request.POST['opc']
    if 'dnn' in request.POST and request.POST['dnn']:
        current_values['config']['dnn'] = request.POST['dnn']
    if 'sst' in request.POST and request.POST['sst']:
        current_values['config']['sst'] = request.POST['sst']
    if 'sd' in request.POST and request.POST['sd']:
        current_values['config']['sd'] = request.POST['sd']
    if 'usrp' in request.POST and request.POST['usrp']:
        current_values['config']['usrp'] = request.POST['usrp']
    
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

    get_values_command = ["helm", "get", "values", "multignb-cu", "--namespace", namespace, "--output", "yaml"]
    current_values_yaml = subprocess.check_output(get_values_command).decode("utf-8")
    current_values = yaml.safe_load(current_values_yaml)

    # Check if each field is provided in the form and update accordingly
    if 'cu_id' in request.POST and request.POST['cu_id']:
        current_values['config']['cuId'] = request.POST['cu_id']
    if 'cell_id' in request.POST and request.POST['cell_id']:
        current_values['config']['cellId'] = request.POST['cell_id']
    if 'f1_int' in request.POST and request.POST['f1_int']:
        current_values['multus']['f1Interface']['IPadd'] = request.POST['f1_int']
    if 'f1_cuport' in request.POST and request.POST['f1_cuport']:
        current_values['config']['f1cuPort'] = request.POST['f1_cuport']
    if 'f1_duport' in request.POST and request.POST['f1_duport']:
        current_values['config']['f1duPort'] = request.POST['f1_duport']
    if 'n2_int' in request.POST and request.POST['n2_int']:
        current_values['multus']['n2Interface']['IPadd'] = request.POST['n2_int']
    if 'n3_int' in request.POST and request.POST['n3_int']:
        current_values['multus']['n3Interface']['IPadd'] = request.POST['n3_int']
    if 'mcc' in request.POST and request.POST['mcc']:
        current_values['config']['mcc'] = request.POST['mcc']
    if 'mnc' in request.POST and request.POST['mnc']:
        current_values['config']['mnc'] = request.POST['mnc']
    if 'tac' in request.POST and request.POST['tac']:
        current_values['config']['tac'] = request.POST['tac']
    if 'sst' in request.POST and request.POST['sst']:
        current_values['config']['sst'] = request.POST['sst']
    if 'amf_host' in request.POST and request.POST['amf_host']:
        current_values['config']['amfhost'] = request.POST['amf_host']
    
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

    get_values_command = ["helm", "get", "values", "multignb-du1", "--namespace", namespace, "--output", "yaml"]
    current_values_yaml = subprocess.check_output(get_values_command).decode("utf-8")
    current_values = yaml.safe_load(current_values_yaml)

    # Check if each field is provided in the form and update accordingly
    if 'gnb_id' in request.POST and request.POST['gnb_id']:
        current_values['config']['gnbId'] = request.POST['gnb_id']
    if 'du_id' in request.POST and request.POST['du_id']:
        current_values['config']['duId'] = request.POST['du_id']
    if 'cell_id' in request.POST and request.POST['cell_id']:
        current_values['config']['cellId'] = request.POST['cell_id']
    if 'phycell_id' in request.POST and request.POST['phycell_id']:
        current_values['config']['phyCellId'] = request.POST['phycell_id']
    if 'f1_int' in request.POST and request.POST['f1_int']:
        current_values['multus']['f1Interface']['IPadd'] = request.POST['f1_int']
    if 'f1_cuport' in request.POST and request.POST['f1_cuport']:
        current_values['config']['f1cuPort'] = request.POST['f1_cuport']
    if 'f1_duport' in request.POST and request.POST['f1_duport']:
        current_values['config']['f1duPort'] = request.POST['f1_duport']
    if 'mcc' in request.POST and request.POST['mcc']:
        current_values['config']['mcc'] = request.POST['mcc']
    if 'mnc' in request.POST and request.POST['mnc']:
        current_values['config']['mnc'] = request.POST['mnc']
    if 'tac' in request.POST and request.POST['tac']:
        current_values['config']['tac'] = request.POST['tac']
    if 'sst' in request.POST and request.POST['sst']:
        current_values['config']['sst'] = request.POST['sst']
    if 'usrp' in request.POST and request.POST['usrp']:
        current_values['config']['usrp'] = request.POST['usrp']
    if 'cu_host' in request.POST and request.POST['cu_host']:
        current_values['config']['cuHost'] = request.POST['cu_host']
    
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

    get_values_command = ["helm", "get", "values", "multignb-du2", "--namespace", namespace, "--output", "yaml"]
    current_values_yaml = subprocess.check_output(get_values_command).decode("utf-8")
    current_values = yaml.safe_load(current_values_yaml)

    # Check if each field is provided in the form and update accordingly
    if 'gnb_id' in request.POST and request.POST['gnb_id']:
        current_values['config']['gnbId'] = request.POST['gnb_id']
    if 'du_id' in request.POST and request.POST['du_id']:
        current_values['config']['duId'] = request.POST['du_id']
    if 'cell_id' in request.POST and request.POST['cell_id']:
        current_values['config']['cellId'] = request.POST['cell_id']
    if 'phycell_id' in request.POST and request.POST['phycell_id']:
        current_values['config']['phyCellId'] = request.POST['phycell_id']
    if 'f1_int' in request.POST and request.POST['f1_int']:
        current_values['multus']['f1Interface']['IPadd'] = request.POST['f1_int']
    if 'f1_cuport' in request.POST and request.POST['f1_cuport']:
        current_values['config']['f1cuPort'] = request.POST['f1_cuport']
    if 'f1_duport' in request.POST and request.POST['f1_duport']:
        current_values['config']['f1duPort'] = request.POST['f1_duport']
    if 'mcc' in request.POST and request.POST['mcc']:
        current_values['config']['mcc'] = request.POST['mcc']
    if 'mnc' in request.POST and request.POST['mnc']:
        current_values['config']['mnc'] = request.POST['mnc']
    if 'tac' in request.POST and request.POST['tac']:
        current_values['config']['tac'] = request.POST['tac']
    if 'sst' in request.POST and request.POST['sst']:
        current_values['config']['sst'] = request.POST['sst']
    if 'usrp' in request.POST and request.POST['usrp']:
        current_values['config']['usrp'] = request.POST['usrp']
    if 'cu_host' in request.POST and request.POST['cu_host']:
        current_values['config']['cuHost'] = request.POST['cu_host']
    
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

    get_values_command = ["helm", "get", "values", "multignb-ue1", "--namespace", namespace, "--output", "yaml"]
    current_values_yaml = subprocess.check_output(get_values_command).decode("utf-8")
    current_values = yaml.safe_load(current_values_yaml)

    # Check if each field is provided in the form and update accordingly
    if 'multus_ipadd' in request.POST and request.POST['multus_ipadd']:
        current_values['multus']['ipadd'] = request.POST['multus_ipadd']
    if 'rfsimserver' in request.POST and request.POST['rfsimserver']:
        current_values['config']['rfSimServer'] = request.POST['rfsimserver']
    if 'fullimsi' in request.POST and request.POST['fullimsi']:
        current_values['config']['fullImsi'] = request.POST['fullimsi']
    if 'fullkey' in request.POST and request.POST['fullkey']:
        current_values['config']['fullKey'] = request.POST['fullkey']
    if 'opc' in request.POST and request.POST['opc']:
        current_values['config']['opc'] = request.POST['opc']
    if 'dnn' in request.POST and request.POST['dnn']:
        current_values['config']['dnn'] = request.POST['dnn']
    if 'sst' in request.POST and request.POST['sst']:
        current_values['config']['sst'] = request.POST['sst']
    if 'sd' in request.POST and request.POST['sd']:
        current_values['config']['sd'] = request.POST['sd']
    if 'usrp' in request.POST and request.POST['usrp']:
        current_values['config']['usrp'] = request.POST['usrp']
    
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

    get_values_command = ["helm", "get", "values", "multignb-ue2", "--namespace", namespace, "--output", "yaml"]
    current_values_yaml = subprocess.check_output(get_values_command).decode("utf-8")
    current_values = yaml.safe_load(current_values_yaml)

    # Check if each field is provided in the form and update accordingly
    if 'multus_ipadd' in request.POST and request.POST['multus_ipadd']:
        current_values['multus']['ipadd'] = request.POST['multus_ipadd']
    if 'rfsimserver' in request.POST and request.POST['rfsimserver']:
        current_values['config']['rfSimServer'] = request.POST['rfsimserver']
    if 'fullimsi' in request.POST and request.POST['fullimsi']:
        current_values['config']['fullImsi'] = request.POST['fullimsi']
    if 'fullkey' in request.POST and request.POST['fullkey']:
        current_values['config']['fullKey'] = request.POST['fullkey']
    if 'opc' in request.POST and request.POST['opc']:
        current_values['config']['opc'] = request.POST['opc']
    if 'dnn' in request.POST and request.POST['dnn']:
        current_values['config']['dnn'] = request.POST['dnn']
    if 'sst' in request.POST and request.POST['sst']:
        current_values['config']['sst'] = request.POST['sst']
    if 'sd' in request.POST and request.POST['sd']:
        current_values['config']['sd'] = request.POST['sd']
    if 'usrp' in request.POST and request.POST['usrp']:
        current_values['config']['usrp'] = request.POST['usrp']
    
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

    get_values_command = ["helm", "get", "values", "multiue-cu", "--namespace", namespace, "--output", "yaml"]
    current_values_yaml = subprocess.check_output(get_values_command).decode("utf-8")
    current_values = yaml.safe_load(current_values_yaml)

    # Check if each field is provided in the form and update accordingly
    if 'cu_id' in request.POST and request.POST['cu_id']:
        current_values['config']['cuId'] = request.POST['cu_id']
    if 'cell_id' in request.POST and request.POST['cell_id']:
        current_values['config']['cellId'] = request.POST['cell_id']
    if 'f1_int' in request.POST and request.POST['f1_int']:
        current_values['multus']['f1Interface']['IPadd'] = request.POST['f1_int']
    if 'f1_cuport' in request.POST and request.POST['f1_cuport']:
        current_values['config']['f1cuPort'] = request.POST['f1_cuport']
    if 'f1_duport' in request.POST and request.POST['f1_duport']:
        current_values['config']['f1duPort'] = request.POST['f1_duport']
    if 'n2_int' in request.POST and request.POST['n2_int']:
        current_values['multus']['n2Interface']['IPadd'] = request.POST['n2_int']
    if 'n3_int' in request.POST and request.POST['n3_int']:
        current_values['multus']['n3Interface']['IPadd'] = request.POST['n3_int']
    if 'mcc' in request.POST and request.POST['mcc']:
        current_values['config']['mcc'] = request.POST['mcc']
    if 'mnc' in request.POST and request.POST['mnc']:
        current_values['config']['mnc'] = request.POST['mnc']
    if 'tac' in request.POST and request.POST['tac']:
        current_values['config']['tac'] = request.POST['tac']
    if 'sst' in request.POST and request.POST['sst']:
        current_values['config']['sst'] = request.POST['sst']
    if 'amf_host' in request.POST and request.POST['amf_host']:
        current_values['config']['amfhost'] = request.POST['amf_host']
    
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

    get_values_command = ["helm", "get", "values", "multiue-du", "--namespace", namespace, "--output", "yaml"]
    current_values_yaml = subprocess.check_output(get_values_command).decode("utf-8")
    current_values = yaml.safe_load(current_values_yaml)

    # Check if each field is provided in the form and update accordingly
    if 'gnb_id' in request.POST and request.POST['gnb_id']:
        current_values['config']['gnbId'] = request.POST['gnb_id']
    if 'du_id' in request.POST and request.POST['du_id']:
        current_values['config']['duId'] = request.POST['du_id']
    if 'cell_id' in request.POST and request.POST['cell_id']:
        current_values['config']['cellId'] = request.POST['cell_id']
    if 'f1_int' in request.POST and request.POST['f1_int']:
        current_values['multus']['f1Interface']['IPadd'] = request.POST['f1_int']
    if 'f1_cuport' in request.POST and request.POST['f1_cuport']:
        current_values['config']['f1cuPort'] = request.POST['f1_cuport']
    if 'f1_duport' in request.POST and request.POST['f1_duport']:
        current_values['config']['f1duPort'] = request.POST['f1_duport']
    if 'mcc' in request.POST and request.POST['mcc']:
        current_values['config']['mcc'] = request.POST['mcc']
    if 'mnc' in request.POST and request.POST['mnc']:
        current_values['config']['mnc'] = request.POST['mnc']
    if 'tac' in request.POST and request.POST['tac']:
        current_values['config']['tac'] = request.POST['tac']
    if 'sst' in request.POST and request.POST['sst']:
        current_values['config']['sst'] = request.POST['sst']
    if 'usrp' in request.POST and request.POST['usrp']:
        current_values['config']['usrp'] = request.POST['usrp']
    if 'cu_host' in request.POST and request.POST['cu_host']:
        current_values['config']['cuHost'] = request.POST['cu_host']
    
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

    get_values_command = ["helm", "get", "values", "multiue-ue1", "--namespace", namespace, "--output", "yaml"]
    current_values_yaml = subprocess.check_output(get_values_command).decode("utf-8")
    current_values = yaml.safe_load(current_values_yaml)

    # Check if each field is provided in the form and update accordingly
    if 'multus_ipadd' in request.POST and request.POST['multus_ipadd']:
        current_values['multus']['ipadd'] = request.POST['multus_ipadd']
    if 'rfsimserver' in request.POST and request.POST['rfsimserver']:
        current_values['config']['rfSimServer'] = request.POST['rfsimserver']
    if 'fullimsi' in request.POST and request.POST['fullimsi']:
        current_values['config']['fullImsi'] = request.POST['fullimsi']
    if 'fullkey' in request.POST and request.POST['fullkey']:
        current_values['config']['fullKey'] = request.POST['fullkey']
    if 'opc' in request.POST and request.POST['opc']:
        current_values['config']['opc'] = request.POST['opc']
    if 'dnn' in request.POST and request.POST['dnn']:
        current_values['config']['dnn'] = request.POST['dnn']
    if 'sst' in request.POST and request.POST['sst']:
        current_values['config']['sst'] = request.POST['sst']
    if 'sd' in request.POST and request.POST['sd']:
        current_values['config']['sd'] = request.POST['sd']
    if 'usrp' in request.POST and request.POST['usrp']:
        current_values['config']['usrp'] = request.POST['usrp']
    
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

    get_values_command = ["helm", "get", "values", "multiue-ue2", "--namespace", namespace, "--output", "yaml"]
    current_values_yaml = subprocess.check_output(get_values_command).decode("utf-8")
    current_values = yaml.safe_load(current_values_yaml)

    # Check if each field is provided in the form and update accordingly
    if 'multus_ipadd' in request.POST and request.POST['multus_ipadd']:
        current_values['multus']['ipadd'] = request.POST['multus_ipadd']
    if 'rfsimserver' in request.POST and request.POST['rfsimserver']:
        current_values['config']['rfSimServer'] = request.POST['rfsimserver']
    if 'fullimsi' in request.POST and request.POST['fullimsi']:
        current_values['config']['fullImsi'] = request.POST['fullimsi']
    if 'fullkey' in request.POST and request.POST['fullkey']:
        current_values['config']['fullKey'] = request.POST['fullkey']
    if 'opc' in request.POST and request.POST['opc']:
        current_values['config']['opc'] = request.POST['opc']
    if 'dnn' in request.POST and request.POST['dnn']:
        current_values['config']['dnn'] = request.POST['dnn']
    if 'sst' in request.POST and request.POST['sst']:
        current_values['config']['sst'] = request.POST['sst']
    if 'sd' in request.POST and request.POST['sd']:
        current_values['config']['sd'] = request.POST['sd']
    if 'usrp' in request.POST and request.POST['usrp']:
        current_values['config']['usrp'] = request.POST['usrp']
    
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
        deployment_name = f"oai-cu-{username}"  # Dynamically create the deployment name

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
        deployment_name = f"oai-du-{username}"  # Dynamically create the deployment name

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
        deployment_name = f"oai-nr-ue-{username}"  # Dynamically create the deployment name

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
        deployment_name = f"oai-cu-mdu-{username}"  # Dynamically create the deployment name

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
        deployment_name = f"oai-du-mdu-1-{username}"  # Dynamically create the deployment name

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
        deployment_name = f"oai-du-mdu-2-{username}"  # Dynamically create the deployment name

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
        deployment_name = f"oai-nr-ue-mdu-1-{username}"  # Dynamically create the deployment name

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
        deployment_name = f"oai-nr-ue-mdu-2-{username}"  # Dynamically create the deployment name

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
        deployment_name = f"oai-cu-mue-{username}"  # Dynamically create the deployment name

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
        deployment_name = f"oai-du-mue-{username}"  # Dynamically create the deployment name

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
        deployment_name = f"oai-nr-ue-mue-1-{username}"  # Dynamically create the deployment name

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
        deployment_name = f"oai-nr-ue-mue-2-{username}"  # Dynamically create the deployment name

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
        deployment_name = f"oai-cu-{username}"  # Dynamically create the deployment name

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
        deployment_name = f"oai-du-{username}"  # Dynamically create the deployment name

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
        deployment_name = f"oai-nr-ue-{username}"  # Dynamically create the deployment name

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
        deployment_name = f"oai-cu-mdu-{username}"  # Dynamically create the deployment name

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
        deployment_name = f"oai-du-mdu-1-{username}"  # Dynamically create the deployment name

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
        deployment_name = f"oai-du-mdu-2-{username}"  # Dynamically create the deployment name

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
        deployment_name = f"oai-nr-ue-mdu-1-{username}"  # Dynamically create the deployment name

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
        deployment_name = f"oai-nr-ue-mdu-2-{username}"  # Dynamically create the deployment name

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
        deployment_name = f"oai-cu-mue-{username}"  # Dynamically create the deployment name

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
        deployment_name = f"oai-du-mue-{username}"  # Dynamically create the deployment name

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
        deployment_name = f"oai-nr-ue-mue-1-{username}"  # Dynamically create the deployment name

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
        deployment_name = f"oai-nr-ue-mue-2-{username}"  # Dynamically create the deployment name

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
