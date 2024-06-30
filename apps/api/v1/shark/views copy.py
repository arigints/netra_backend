from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.conf import settings
from apps.models import PcapFile
from apps.serializers import PcapFileSerializer
import os
import subprocess
import json
from datetime import datetime, timezone

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def capture_and_return_packets(request, pod_name):
    namespace = f"{request.user.username}"
    pcap_filename = f"{namespace}_{pod_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pcap"
    
    try:
        # Capture the packets into a variable
        capture_cmd = f"kubectl sniff -n {namespace} {pod_name} -o - | tshark -r - -c 100 -Y 'nas-5gs or f1ap or ngap or sctp or pfcp or gtp or tcp or dhcp or udp' -w -"
        capture_result = subprocess.run(capture_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if capture_result.returncode != 0:
            error_message = f"Command failed or produced no output. Return code: {capture_result.returncode}. STDERR: {capture_result.stderr.decode('utf-8')}"
            return Response({"error": error_message}, status=400)
        
        pcap_data = capture_result.stdout

        # Save the captured packets directly to the database
        pcap_file = PcapFile.objects.create(
            user=request.user,
            filename=pcap_filename,
            file_data=pcap_data,
            file_size=len(pcap_data)
        )

        # Parse the captured data to JSON
        parse_cmd = "tshark -r - -T json"
        parse_result = subprocess.run(parse_cmd, input=pcap_data, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if parse_result.returncode != 0:
            error_message = f"Parsing command failed. Return code: {parse_result.returncode}. STDERR: {parse_result.stderr.decode('utf-8')}"
            return Response({"error": error_message}, status=400)

        packets = json.loads(parse_result.stdout.decode('utf-8'))

        # Serialize the PcapFile object
        serializer = PcapFileSerializer(pcap_file)

        return Response({
            "message": "PCAP file captured successfully",
            "pcap_file": serializer.data,
            "packets": packets
        })
    
    except json.JSONDecodeError as e:
        return Response({"error": f"JSON decoding error: {str(e)}"}, status=500)
    except Exception as e:
        return Response({"error": f"Unexpected error: {str(e)}"}, status=500)

###################################################################################

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def capture_and_return_packets_no_save(request, pod_name):
    namespace = f"{request.user.username}"
    
    try:
        # Capture the packets into a variable
        capture_cmd = f"kubectl sniff -n {namespace} {pod_name} -o - | tshark -r - -c 100 -Y 'nas-5gs or f1ap or ngap or sctp or pfcp or gtp or tcp or dhcp or udp' -w -"
        capture_result = subprocess.run(capture_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if capture_result.returncode != 0:
            error_message = f"Command failed or produced no output. Return code: {capture_result.returncode}. STDERR: {capture_result.stderr.decode('utf-8')}"
            return Response({"error": error_message}, status=400)
        
        pcap_data = capture_result.stdout

        # Parse the captured data to JSON
        parse_cmd = "tshark -r - -T json"
        parse_result = subprocess.run(parse_cmd, input=pcap_data, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if parse_result.returncode != 0:
            error_message = f"Parsing command failed. Return code: {parse_result.returncode}. STDERR: {parse_result.stderr.decode('utf-8')}"
            return Response({"error": error_message}, status=400)

        packets = json.loads(parse_result.stdout.decode('utf-8'))

        return Response({
            "message": "PCAP file captured successfully",
            "packets": packets
        })
    
    except json.JSONDecodeError as e:
        return Response({"error": f"JSON decoding error: {str(e)}"}, status=500)
    except Exception as e:
        return Response({"error": f"Unexpected error: {str(e)}"}, status=500)

###################################################################################      

from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from apps.models import PcapFile
from apps.serializers import PcapFileSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_pcap_file(request, file_id):
    try:
        pcap_file = PcapFile.objects.get(id=file_id, user=request.user)
        response = HttpResponse(pcap_file.file_data, content_type='application/vnd.tcpdump.pcap')
        response['Content-Disposition'] = f'attachment; filename="{pcap_file.filename}"'
        return response
    except PcapFile.DoesNotExist:
        return Response({"error": "File not found"}, status=404)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_pcap_file(request, file_id):
    try:
        pcap_file = PcapFile.objects.get(id=file_id, user=request.user)
        pcap_file.delete()
        return Response({"message": "File deleted successfully"}, status=204)
    except PcapFile.DoesNotExist:
        return Response({"error": "File not found"}, status=404)

###################################################################################

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from apps.models import PcapFile
from django.conf import settings
import os

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_pcap_files(request):
    try:
        pcap_files = PcapFile.objects.filter(user=request.user)
        serializer = PcapFileSerializer(pcap_files, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response({"error": str(e)}, status=500)

###################################################################################

import threading
import subprocess
import json
from datetime import datetime
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from apps.models import PcapFile  # Import your PcapFile model
from apps.serializers import PcapFileSerializer  # Import your PcapFileSerializer
import pytz

# Dictionary to hold running sniffing threads and their results
sniffing_threads = {}
sniffing_results = {}

def convert_timestamp(timestamp):
    """Convert milliseconds since epoch to a human-readable date-time string in Jakarta timezone."""
    utc_dt = datetime.fromtimestamp(int(timestamp) / 1000.0, tz=timezone.utc)
    jakarta_tz = pytz.timezone('Asia/Jakarta')
    jakarta_dt = utc_dt.astimezone(jakarta_tz)
    return jakarta_dt.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]  # Format with milliseconds

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def start_sniffing(request, pod_name):
    namespace = f"{request.user.username}"
    sniffing_id = f"{namespace}_{pod_name}"
    pcap_filename = f"{namespace}_{pod_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pcap"

    def sniff_packets():
        capture_cmd = f"kubectl sniff -n {namespace} {pod_name} -o - | tshark -i - -Y 'nas-5gs or f1ap or ngap or sctp or pfcp or gtp or tcp or dhcp or udp' -T ek"
        process = subprocess.Popen(capture_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1, universal_newlines=True)

        sniffing_threads[sniffing_id] = process
        sniffing_results[sniffing_id] = {"packets": [], "status": "running"}

        try:
            for line in process.stdout:
                line = line.strip()
                if line.startswith('{') and line.endswith('}'):
                    try:
                        packet = json.loads(line)
                        # Convert the timestamp
                        if 'timestamp' in packet:
                            packet['timestamp'] = convert_timestamp(packet['timestamp'])
                        sniffing_results[sniffing_id]["packets"].append(packet)
                    except json.JSONDecodeError as e:
                        print(f"Invalid JSON line: {line}, error: {str(e)}")

            process.wait()
            if process.returncode != 0:
                error_message = f"Command failed or produced no output. Return code: {process.returncode}. STDERR: {process.stderr.read()}"
                sniffing_results[sniffing_id] = {"error": error_message, "status": "failed"}
            else:
                sniffing_results[sniffing_id]["status"] = "completed"
        except Exception as e:
            sniffing_results[sniffing_id] = {"error": f"Unexpected error: {str(e)}", "status": "failed"}

    thread = threading.Thread(target=sniff_packets)
    thread.start()

    return JsonResponse({"message": "Packet sniffing started successfully", "sniffing_id": sniffing_id})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def stop_sniffing(request, pod_name):
    namespace = f"{request.user.username}"
    sniffing_id = f"{namespace}_{pod_name}"
    pcap_filename = f"{namespace}_{pod_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pcap"

    if sniffing_id in sniffing_threads:
        process = sniffing_threads[sniffing_id]
        process.terminate()
        process.wait()
        del sniffing_threads[sniffing_id]

        if sniffing_id in sniffing_results:
            pcap_data = json.dumps(sniffing_results[sniffing_id]["packets"]).encode('utf-8')

            # Save the captured packets directly to the database
            pcap_file = PcapFile.objects.create(
                user=request.user,
                filename=pcap_filename,
                file_data=pcap_data,
                file_size=len(pcap_data)
            )

            # Serialize the PcapFile object
            serializer = PcapFileSerializer(pcap_file)

            sniffing_results[sniffing_id]["status"] = "stopped"
            sniffing_results[sniffing_id]["pcap_file"] = serializer.data

        return JsonResponse({"message": "Packet sniffing stopped successfully", "pcap_file": sniffing_results[sniffing_id].get("pcap_file", {})})
    else:
        return JsonResponse({"error": "No active sniffing process for this pod"}, status=400)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_sniffing_status(request, sniffing_id):
    try:
        if sniffing_id in sniffing_results:
            return JsonResponse(sniffing_results[sniffing_id])
        else:
            return JsonResponse({"message": "Sniffing process not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": f"Unexpected error: {str(e)}"}, status=500)

