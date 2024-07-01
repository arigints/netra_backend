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

import json
import logging
import subprocess
import threading
from datetime import datetime
from time import sleep

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

logger = logging.getLogger(__name__)
sniffing_results = {}
sniffing_threads = {}
pcap_files = {}
lock = threading.Lock()

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def start_sniffing(request, pod_name):
    namespace = f"{request.user.username}"
    sniffing_id = f"{namespace}_{pod_name}"
    pcap_filename = f"{namespace}_{pod_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pcap"
    pcap_file_path = f"/tmp/{pcap_filename}"  # Temporary path for pcap file
    pcap_files[sniffing_id] = pcap_file_path  # Store the file path

    logger.debug(f"Starting packet sniffing for {sniffing_id}, saving to {pcap_file_path}")

    def sniff_packets():
        capture_cmd = f"kubectl sniff -n {namespace} {pod_name} -o {pcap_file_path}"
        process = subprocess.Popen(capture_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        with lock:
            sniffing_threads[sniffing_id] = process
            sniffing_results[sniffing_id] = {"packets": [], "status": "running"}
        
        process.wait()
        if process.returncode != 0:
            error_message = f"Command failed or produced no output. Return code: {process.returncode}. STDERR: {process.stderr.read()}"
            logger.error(error_message)
            with lock:
                sniffing_results[sniffing_id] = {"error": error_message, "status": "failed"}
        else:
            with lock:
                sniffing_results[sniffing_id]["status"] = "completed"
            logger.debug(f"Packet sniffing completed for {sniffing_id}")

    def process_packets():
        while True:
            with lock:
                if sniffing_results[sniffing_id]["status"] != "running":
                    break

            parse_cmd = f"tshark -r {pcap_file_path} -Y 'nas-5gs or f1ap or ngap or sctp or pfcp or gtp or tcp or dhcp or udp' -T json"
            parse_result = subprocess.run(parse_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            if parse_result.returncode == 0:
                packets = json.loads(parse_result.stdout.decode('utf-8'))
                with lock:
                    sniffing_results[sniffing_id]["packets"].extend(packets)
                    logger.debug(f"Processed {len(packets)} packets for {sniffing_id}")
            else:
                logger.error(f"Packet processing failed for {sniffing_id}. Return code: {parse_result.returncode}")
            
            sleep(5)  # Poll every 5 seconds

    capture_thread = threading.Thread(target=sniff_packets)
    capture_thread.start()

    process_thread = threading.Thread(target=process_packets)
    process_thread.start()

    return JsonResponse({"message": "Packet sniffing started successfully", "sniffing_id": sniffing_id})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_sniffing_status(request, sniffing_id):
    try:
        with lock:
            if sniffing_id in sniffing_results:
                return JsonResponse(sniffing_results[sniffing_id])
            else:
                return JsonResponse({"message": "Sniffing process not found"}, status=404)
    except Exception as e:
        logger.error(f"Unexpected error checking sniffing status: {str(e)}")
        return JsonResponse({"error": f"Unexpected error: {str(e)}"}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def stop_sniffing(request, sniffing_id):
    try:
        if sniffing_id in sniffing_threads:
            process = sniffing_threads[sniffing_id]
            process.terminate()
            process.wait()  # Ensure the process has terminated

            sniffing_results[sniffing_id]["status"] = "stopped"
            logger.debug(f"Packet sniffing stopped for {sniffing_id}")

            # Save the pcap file to the database if not already saved
            if "pcap_file_id" not in sniffing_results[sniffing_id]:
                if sniffing_id in pcap_files:
                    pcap_file_path = pcap_files[sniffing_id]

                    if os.path.exists(pcap_file_path):
                        try:
                            with open(pcap_file_path, 'rb') as f:
                                pcap_data = f.read()
                            logger.debug(f"Read pcap file {pcap_file_path} for {sniffing_id}")

                            # Save the pcap file directly to the database
                            pcap_file = PcapFile.objects.create(
                                user=request.user,
                                filename=os.path.basename(pcap_file_path),
                                file_data=pcap_data,
                                file_size=len(pcap_data)
                            )
                            logger.debug(f"Saved pcap file to database for {sniffing_id}")

                            sniffing_results[sniffing_id]["pcap_file_id"] = pcap_file.id
                        except Exception as e:
                            error_message = f"Failed to save pcap file: {str(e)}"
                            logger.error(error_message)
                            sniffing_results[sniffing_id] = {"error": error_message, "status": "failed"}
                    else:
                        error_message = f"PCAP file not found: {pcap_file_path}"
                        logger.error(error_message)
                        sniffing_results[sniffing_id] = {"error": error_message, "status": "failed"}

            return JsonResponse({"message": "Packet sniffing stopped successfully", "sniffing_id": sniffing_id})
        else:
            logger.error(f"Sniffing process not found for {sniffing_id}")
            return JsonResponse({"message": "Sniffing process not found"}, status=404)
    except Exception as e:
        logger.error(f"Unexpected error stopping sniffing: {str(e)}")
        return JsonResponse({"error": f"Unexpected error: {str(e)}"}, status=500)