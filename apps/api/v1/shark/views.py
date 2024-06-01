import pyshark
from django.http import JsonResponse
import pytz
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
import subprocess
import json
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def capture_packets(request):
    interface = 'ens33'  # Specify the interface you want to capture from
    capture = pyshark.LiveCapture(interface=interface)
    jakarta_tz = pytz.timezone('Asia/Jakarta')

    packets_summary = []
    for packet in capture.sniff_continuously(packet_count=10):
        try:
            packet_details = {
                'protocol': packet.highest_layer,
                'length': packet.length,
                'timestamp': packet.sniff_time.astimezone(jakarta_tz).strftime('%H:%M:%S'),
            }

            # Extract IP layer details if present
            if 'IP' in packet:
                packet_details.update({
                    'src_ip': packet.ip.src,
                    'dst_ip': packet.ip.dst,
                })

            # Extract TCP layer details if present
            if 'TCP' in packet:
                packet_details.update({
                    'src_port': packet.tcp.srcport,
                    'dst_port': packet.tcp.dstport,
                })

            # Extract UDP layer details if present
            elif 'UDP' in packet:
                packet_details.update({
                    'src_port': packet.udp.srcport,
                    'dst_port': packet.udp.dstport,
                })

            packets_summary.append(packet_details)

        except AttributeError as e:
            # Handle packets that might not have the attributes you're trying to access
            continue

    return JsonResponse({'packets': packets_summary}, safe=False)

###################################################################################

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
        capture_cmd = f"kubectl sniff -n {namespace} {pod_name} -o - | tshark -r - -c 20 -Y 'nas-5gs or f1ap or ngap or sctp or pfcp or gtp or tcp or dhcp or udp' -w -"
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


