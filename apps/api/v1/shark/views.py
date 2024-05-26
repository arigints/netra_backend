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

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def capture_and_return_packets(request, pod_name):
    namespace = f"{request.user.username}"
    try:
        # Update the tshark filter expression to include the desired protocols
        cmd = f"kubectl sniff -n {namespace} {pod_name} -o - | tshark -r - -c 100 -Y 'nas-5gs or f1ap or ngap or sctp or pfcp or gtp or tcp or dhcp or udp' -T json"
        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode != 0 or not result.stdout.strip():
            error_message = f"Command failed or produced no output. Return code: {result.returncode}. STDERR: {result.stderr}"
            return Response({"error": error_message}, status=400)
        
        packets = json.loads(result.stdout)
        return Response(packets)
    
    except json.JSONDecodeError as e:
        return Response({"error": f"JSON decoding error: {str(e)}"}, status=500)
    except Exception as e:
        return Response({"error": f"Unexpected error: {str(e)}"}, status=500)


