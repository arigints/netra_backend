import pyshark
from django.http import JsonResponse
import pytz
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

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
