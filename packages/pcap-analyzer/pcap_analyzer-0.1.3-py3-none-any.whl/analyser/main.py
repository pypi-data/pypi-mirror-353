import argparse
from scapy.all import rdpcap
from scapy.layers.inet import IP, TCP, UDP
from collections import Counter
from scapy.layers.dns import DNS
from analyser.common_ports_full import COMMON_PORTS

protocol_names = {
    1: "ICMP",
    6: "TCP",
    17: "UDP"
}


def showipaddresses(packets):
    """Return unique IP source and destination pairs from packet capture"""
    pairs = set()
    for packet in packets:
        if IP in packet:
            pairs.add((packet[IP].src, packet[IP].dst))
    return pairs


def showprotocols(packets):
    """Count and return number of packets for known common ports only (skip unknowns and non-TCP/UDP)."""
    protocol_counter = Counter()
    result = []

    for packet in packets:
        if TCP in packet:
            port = packet[TCP].dport
            if (port, 'tcp') in COMMON_PORTS:
                proto_name = COMMON_PORTS[(port, 'tcp')]
                protocol_counter[proto_name] += 1
        elif UDP in packet:
            port = packet[UDP].dport
            if (port, 'udp') in COMMON_PORTS:
                proto_name = COMMON_PORTS[(port, 'udp')]
                protocol_counter[proto_name] += 1

    for proto, count in sorted(protocol_counter.items(), key=lambda item: item[1], reverse=True):
        result.append((proto, count))
    return result


def showtoptalkers(packets):
    """Return the top talkers on the network (most packets sent)"""
    ip_counter = Counter()
    for packet in packets:
        if IP in packet:
            ip_counter[packet[IP].src] += 1
    return ip_counter.most_common(5)


def throughput(packets):
    """Return the total throughput calculated from the captured packets in Mbps."""
    start_time = packets[0].time
    end_time = packets[-1].time
    total_bytes = sum(len(pkt) for pkt in packets)
    duration = end_time - start_time

    if duration == 0:
        throughput_mbps = 0.0
    else:
        throughput_mbps = (total_bytes * 8) / (duration * 1_000_000)

    return duration, throughput_mbps


def identify_broadcast_multicast(packets):
    """Identify and count broadcast and multicast packets in the capture."""
    broadcast_count = 0
    multicast_count = 0
    unicast_count = 0

    for pkt in packets:
        if pkt.haslayer('Ether'):
            dst_mac = pkt['Ether'].dst
            if dst_mac == 'ff:ff:ff:ff:ff:ff':
                broadcast_count += 1
                continue

        if pkt.haslayer(IP):
            dst_ip = pkt[IP].dst
            first_octet = int(dst_ip.split('.')[0])
            if 224 <= first_octet <= 239:
                multicast_count += 1
                continue

        unicast_count += 1

    return broadcast_count, multicast_count, unicast_count


def extract_dns_domains(packets):
    """Extract and return a sorted list of visited domain names from DNS queries in the packet capture."""
    domains = set()
    for pkt in packets:
        if pkt.haslayer(DNS) and pkt[DNS].qr == 0:
            try:
                qname = pkt[DNS].qd[0].qname.decode().strip('.')
                domains.add(qname)
            except (UnicodeDecodeError, AttributeError):
                continue
    return sorted(domains)


def main():
    parser = argparse.ArgumentParser(description="PCAP Analyser")
    parser.add_argument("--file", required=True, help="Path to .pcap or .pcapng file")
    parser.add_argument("--printall", action="store_true", help="Print all the IP packets source -> destination")
    parser.add_argument("--showprotocols", action="store_true", help="Show the frequency of the used protocols")
    parser.add_argument("--toptalkers", action="store_true", help="Show the 5 most active IP addresses")
    parser.add_argument("--throughput", action="store_true", help="Shows the throughput on the analysed link")
    parser.add_argument("--broadcast_multicast", action="store_true", help="Shows the amount of multicast & broadcast traffic")
    parser.add_argument("--extract_dns_domains", action="store_true", help="Shows the domain names DNS resolved")

    args = parser.parse_args()
    packets = rdpcap(args.file)

    print(f"Loaded {len(packets)} .pcap packets")

    if args.printall:
        pairs = showipaddresses(packets)
        print("Source → Destination IP pairs:")
        for src, dst in pairs:
            print(f"{src} → {dst}")

    if args.showprotocols:
        protocols = showprotocols(packets)
        print("Protocol usage:")
        for proto, count in protocols:
            print(f"{proto}: {count} packets")

    if args.toptalkers:
        talkers = showtoptalkers(packets)
        print("Top talkers:")
        for ip, count in talkers:
            print(f"{ip} → {count} packets sent")

    if args.throughput:
        duration, tput = throughput(packets)
        print(f"Duration: {duration:.2f} seconds")
        print(f"Throughput: {tput:.2f} Mbps")

    if args.broadcast_multicast:
        broadcast, multicast, unicast = identify_broadcast_multicast(packets)
        print(f"Broadcast packets: {broadcast}")
        print(f"Multicast packets: {multicast}")
        print(f"Unicast packets: {unicast}")

    if args.extract_dns_domains:
        domains = extract_dns_domains(packets)
        print("Domains Resolved via DNS:")
        for domain in domains:
            print(domain)


if __name__ == "__main__":
    main()

