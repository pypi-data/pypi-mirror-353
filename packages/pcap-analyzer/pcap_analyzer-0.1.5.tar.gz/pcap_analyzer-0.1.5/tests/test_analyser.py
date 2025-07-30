import analyser.main as am
import tests.packet_generator as pg
import ipaddress


# Checks whether a given string is a valid IPv4 or IPv6 address
def is_valid_ip(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False


def test_printall():
    """ This test checks if the function 'printall' prints correctly the unique IP source →
    destination pairs in the network"""

    input1 = pg.unique_addresses()  # 5 unique addresses
    input2 = pg.duplicate_addresses()  # duplicate addresses

    # Call the function with a set of 5 unique (src, dst) IP address pairs
    result1 = am.showipaddresses(input1)

    # Validate that each source and destination is a valid IP address
    for src, dst in result1:
        assert is_valid_ip(src), f"Invalid source IP: {src}"
        assert is_valid_ip(dst), f"Invalid destination IP: {dst}"

    # Call the function with a set of 5 unique (src, dst) IP address pairs
    result2 = am.showipaddresses(input1)

    # Verify that the function returns exactly 5 unique pairs as expected
    assert len(result2) == 5, f"Expected 5 unique pairs, got {len(result2)}"

    # Call the function with duplicated (src, dst) IP pairs
    result3 = am.showipaddresses(input2)

    # Validate that duplicates are properly collapsed into a single unique pair
    assert len(result3) == 1, f"Expected 1 unique pair, got {len(result3)}"


def test_showprotocols():
    """Test whether the function'showprotocols' correctly counts and returns known protocols, sorted by frequency."""

    input1 = pg.multiple_dest_ports()  # Returns 5 www-http packets
    input2 = pg.multiple_diff_dest_ports()  # Returns 4 www-http, 2 https and 3 ssh packets

    # Test whether the function retrieves and counts the protocols from the packets
    result1 = am.showprotocols(input1)
    for proto, count in result1:
        if proto == "www-http":
            assert count == 5, f"Expected 5 HTTP packets, got {count}"
            break
    else:
        assert False, "HTTP protocol not found in result"

    # Test whether the function sorts the protocols based on their frequency in descending order
    result2 = am.showprotocols(input2)
    counts = []

    for _, count in result2:  # Extract the counts from the result list of (protocol, count) tuples
        counts.append(count)

    # Check if the list is sorted in descending order
    assert counts == sorted(counts, reverse=True), f"Counts not sorted: {counts}"


def test_showtoptalkers():
    """This test checks whether the function `showtoptalkers` correctly identifies
    and returns the top IP talkers based on the number of packets they sent.
    Results should be sorted by frequency (i.e., packet count)."""

    input1 = pg.multiple_ip_addresses()  # Multiple IP packets with different source IP addresses and varying frequencies

    # Run the function
    result = am.showtoptalkers(input1)

    # Check that the top talker is 192.168.1.4 with 5 packets
    assert result[0][0] == "192.168.1.4", f"Expected 192.168.1.4, got {result[0][0]}"
    assert result[0][1] == 5, f"Expected 5 packets, got {result[0][1]}"

    # Check that the second talker is 192.168.1.2 with 4 packets
    assert result[1][0] == "192.168.1.2", f"Expected 192.168.1.2, got {result[1][0]}"
    assert result[1][1] == 4, f"Expected 4 packets, got {result[1][1]}"

    # Check that the third talker is 192.168.1.1 with 3 packets
    assert result[2][0] == "192.168.1.1", f"Expected 192.168.1.1, got {result[2][0]}"
    assert result[2][1] == 3, f"Expected 3 packets, got {result[2][1]}"

    # Check that the fourth talker is 192.168.1.3 with 2 packets
    assert result[3][0] == "192.168.1.3", f"Expected 192.168.1.3, got {result[3][0]}"
    assert result[3][1] == 2, f"Expected 2 packets, got {result[3][1]}"

    # Check that the fifth talker is 192.168.1.5 with 1 packet
    assert result[4][0] == "192.168.1.5", f"Expected 192.168.1.5, got {result[4][0]}"
    assert result[4][1] == 1, f"Expected 1 packet, got {result[4][1]}"


def test_throughput():
    """Test that the `throughput` function returns the correct duration and throughput
    (in Mbps) for a given list of packets."""

    input1 = pg.fixed_lenght_packets()  # 5 packets: fixed lenght (10000 bytes) and fixed timestamp (+1 second per packet)

    # Run the function
    result = am.throughput(input1)

    # Verify the calculation of the function
    # result[0] = duration in seconds
    # result[1] = throughput in Mbps
    # Expected duration: 4 seconds
    # Expected throughput: 0.1 Mbps (50,000 bytes = 0.4 Mb / 4 seconds)
    assert result[0] == 4, f"Expected duration 4, got {result[0]}"
    assert result[1] == 0.1, f"Expected throughput 0.1, got {result[1]}"


def test_identify_broadcast_multicast():
    """
    Identifies and classifies packets as broadcast, multicast, or unicast
    based on their destination MAC or IP addresses.

    Broadcast: MAC = ff:ff:ff:ff:ff:ff
    Multicast: IP in the range 224.0.0.0 to 239.255.255.255
    Unicast: All other destination addresses
    """

    # 2 broadcast packets (ff:ff:ff:ff:ff:ff), 3 multicast packets (224.0.0.0 to 239.255.255.255), 1 unicast packet
    input1 = pg.broadcast_multicast_packets()

    # Run the function
    result = am.identify_broadcast_multicast(input1)

    # Test whether the function correctly counts the number of packets per category:
    # result[0] = number of broadcast packets
    # result[1] = number of multicast packets
    # result[2] = number of unicast packets
    assert result[0] == 2
    assert result[1] == 3
    assert result[2] == 1


def test_extract_dns_domains():
    """This test checks whether the function extracts domain names from DNS request packets
    and returns them as a sorted list."""

    input1 = pg.dns_req()  # Unsorted packet list containing multiple domain queries, including duplicates

    # Run the function
    result = am.extract_dns_domains(input1)

    # Test whether the function retrieves the domain names, filters out duplicates, and sorts them alphabetically
    expected = ["apple.com", "dell.com", "google.com", "meta.com", "samsung.com"]
    assert result == expected










