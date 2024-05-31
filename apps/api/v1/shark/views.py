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
import os
import subprocess
import json
from datetime import datetime

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def capture_and_return_packets(request, pod_name):
    namespace = f"{request.user.username}"
    pcap_filename = f"{namespace}_{pod_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pcap"
    pcap_filepath = os.path.join(settings.MEDIA_ROOT, pcap_filename)
    
    try:
        # Capture the packets to a pcap file
        capture_cmd = f"kubectl sniff -n {namespace} {pod_name} -o - | tshark -r - -c 20 -Y 'nas-5gs or f1ap or ngap or sctp or pfcp or gtp or tcp or dhcp or udp' -w {pcap_filepath}"
        capture_result = subprocess.run(capture_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if capture_result.returncode != 0 or not os.path.exists(pcap_filepath):
            error_message = f"Command failed or produced no output. Return code: {capture_result.returncode}. STDERR: {capture_result.stderr}"
            return Response({"error": error_message}, status=400)
        
        # Parse the captured pcap file to JSON
        parse_cmd = f"tshark -r {pcap_filepath} -T json"
        parse_result = subprocess.run(parse_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if parse_result.returncode != 0:
            error_message = f"Parsing command failed. Return code: {parse_result.returncode}. STDERR: {parse_result.stderr}"
            return Response({"error": error_message}, status=400)

        packets = json.loads(parse_result.stdout)

        # Create a new PcapFile entry in the database
        pcap_file = PcapFile.objects.create(user=request.user, filename=pcap_filename)

        return Response({"message": "PCAP file captured successfully", "pcap_file": pcap_file.filename, "packets": packets})
    
    except json.JSONDecodeError as e:
        return Response({"error": f"JSON decoding error: {str(e)}"}, status=500)
    except Exception as e:
        return Response({"error": f"Unexpected error: {str(e)}"}, status=500)


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
        user = request.user
        pcap_files = PcapFile.objects.filter(user=user)
        file_data = [
            {
                "filename": pcap_file.filename,
                "url": request.build_absolute_uri(settings.MEDIA_URL + pcap_file.filename),
                "created_at": pcap_file.created_at
            }
            for pcap_file in pcap_files
        ]
        return Response(file_data)
    except Exception as e:
        return Response({"error": str(e)}, status=500)


