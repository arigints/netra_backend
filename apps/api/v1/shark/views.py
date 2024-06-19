from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.conf import settings
from apps.models import PcapFile
from apps.serializers import PcapFileSerializer
import os
import subprocess
import json
from datetime import datetime

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
        capture_cmd = f"kubectl sniff -n {namespace} {pod_name} -o - | tshark -r - -c 20 -Y 'nas-5gs or f1ap or ngap or sctp or pfcp or gtp or tcp or dhcp or udp' -w -"
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

import subprocess
import json
import asyncio
import logging
import tempfile
from datetime import datetime
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from apps.models import PcapFile
from apps.serializers import PcapFileSerializer

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

capture_processes = {}

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_sniffing(request):
    try:
        pod_name = request.data.get('pod_name')
        namespace = request.user.username
        group_name = f"packets_{namespace}_{pod_name}"

        logger.debug(f"Starting packet sniffing for pod: {pod_name} in namespace: {namespace}")

        # Start the packet capture asynchronously
        async_to_sync(start_capture)(namespace, pod_name, group_name, request.user.id)

        return Response({"message": "Packet sniffing started"}, status=200)
    except Exception as e:
        logger.error(f"Error in start_sniffing: {str(e)}")
        return Response({"error": str(e)}, status=500)

async def start_capture(namespace, pod_name, group_name, user_id):
    channel_layer = get_channel_layer()
    logger.debug(f"Starting async capture for pod: {pod_name} in namespace: {namespace}")

    async def capture_packets():
        capture_cmd = f"kubectl sniff -n {namespace} {pod_name} -o -"
        capture_process = await asyncio.create_subprocess_shell(
            capture_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        capture_processes[pod_name] = capture_process

        logger.debug(f"Capture process started for pod: {pod_name}")

        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            try:
                while True:
                    output = await capture_process.stdout.read(1024)
                    if not output:
                        break
                    temp_file.write(output)

                temp_file.flush()
                temp_file.seek(0)

                logger.debug(f"Temporary file created at {temp_file.name} with captured packets.")

                pcap_filename = f"{namespace}_{pod_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pcap"
                with open(temp_file.name, 'rb') as pcap_file:
                    pcap_data = pcap_file.read()

                try:
                    # Save the captured packets directly to the database
                    pcap_file_record = PcapFile.objects.create(
                        user_id=user_id,
                        filename=pcap_filename,
                        file_data=pcap_data,
                        file_size=len(pcap_data)
                    )
                    logger.debug(f"PCAP file saved to database with id: {pcap_file_record.id}")

                    parse_cmd = ["tshark", "-r", temp_file.name, "-Y", "nas-5gs or f1ap or ngap or sctp or pfcp or gtp or tcp or dhcp or udp", "-T", "json"]
                    parse_process = await asyncio.create_subprocess_exec(
                        *parse_cmd,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    parse_result, parse_stderr = await parse_process.communicate()

                    if parse_process.returncode != 0:
                        error_message = f"Parsing command failed. Return code: {parse_process.returncode}. STDERR: {parse_stderr.decode('utf-8')}"
                        logger.error(error_message)
                        await channel_layer.group_send(
                            group_name,
                            {
                                "type": "packet_message",
                                "message": {"error": error_message}
                            }
                        )
                        return

                    packets = json.loads(parse_result.decode('utf-8'))
                    logger.debug(f"Packets parsed successfully: {packets}")
                    await channel_layer.group_send(
                        group_name,
                        {
                            "type": "packet_message",
                            "message": {"packets": packets}
                        }
                    )

                    # Return the captured packets in the response
                    return packets

                except Exception as e:
                    logger.error(f"Error saving PCAP file to database: {str(e)}")
                    return []
            finally:
                temp_file.close()

    try:
        packets = await capture_packets()
        return packets
    except Exception as e:
        logger.error(f"Error in start_capture: {str(e)}")
        return []

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def stop_sniffing(request):
    try:
        pod_name = request.data.get('pod_name')
        namespace = request.user.username

        logger.debug(f"Stopping packet sniffing for pod: {pod_name} in namespace: {namespace}")

        capture_process = capture_processes.pop(pod_name, None)
        if capture_process:
            capture_process.terminate()

        return Response({"message": "Packet sniffing stopped"}, status=200)
    except Exception as e:
        logger.error(f"Error in stop_sniffing: {str(e)}")
        return Response({"error": str(e)}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_packets(request, pod_name):
    try:
        namespace = request.user.username
        pcap_file_record = PcapFile.objects.filter(user=request.user, filename__icontains=pod_name).latest('created_at')

        parse_cmd = ["tshark", "-r", "-", "-T", "json"]
        parse_process = subprocess.Popen(
            parse_cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        parse_result, parse_stderr = parse_process.communicate(input=pcap_file_record.file_data)

        if parse_process.returncode != 0:
            error_message = f"Parsing command failed. Return code: {parse_process.returncode}. STDERR: {parse_stderr.decode('utf-8')}"
            logger.error(error_message)
            return Response({"error": error_message}, status=500)

        packets = json.loads(parse_result.decode('utf-8'))
        return Response({"packets": packets}, status=200)

    except Exception as e:
        logger.error(f"Error in get_packets: {str(e)}")
        return Response({"error": str(e)}, status=500)


