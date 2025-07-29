#  PCAP Analyzer

This project is a lightweight, simple CLI tool written in Python designed to analyse .pcap files and offer insight in the network traffic without the overhead of full packet inspections.

---

## Introduction 
Network administrators often need to quickly analyze `.pcap` files to understand traffic patterns, protocol usage, and network performance. Tools like Wireshark offer deep inspection but can be heavy and overkill for simple summaries.

PCAP Analyzer fills this gap by offering a lightweight, scriptable CLI tool that provides essential network insights without the overhead.

## Features
| Option                  | Description                                                              |
|-------------------------|--------------------------------------------------------------------------|
| `--printall`            | Shows all IP traffic as source → destination.                            |
| `--showprotocols`       | Displays the number of packets per IP protocol (such as TCP, UDP, ICMP). |
| `--toptalkers`          | Shows the top 5 most active sending IP addresses.                        |
| `--throughput`          | Calculates total throughput in Mbps over the duration of the capture.    |
| `--data_packet_rtt`     | Measures average latency (RTT) between data packets and their ACKs.      |
| `--extract_dns_domains` | Lists unique domains queried via DNS.                                    |
---
## Non-functional Specifications
- **Performance:** Analyze `.pcap` files up to 100MB in under 5 seconds on modern hardware.
- **Platform Support:** Compatible with Windows, Linux, and macOS; requires Python 3.8 or higher.
- **Usability:** Simple CLI with one-command execution; help available via `--help` flag.
- **Maintainability:** Modular, clean codebase for easy future expansion.
- **Security:** Only reads `.pcap` files; no packet modification or network interaction.
---
## Installation
### Gitlab
Clone the repository:
```bash
git clone https://gitlab.fdmci.hva.nl/schiffd/pcap-analyzer
cd pcap-analyzer
````
### Requirements
Install dependencies:
```bash
pip install -r requirements.txt
````
Or with UV:
```bash
uv pip install .
````
Include optional dependencies:
```bash
uv pip install .[dev]
````
---
## Usage
Run:
```bash
python -m analyser --file <path/to/file.pcapng> [options]
````
---
## Examples
##### Show the toptalkers (most active IP addresses):
```bash
python -m analyser --file capture.pcapng --toptalkers
````
![Demo --showprotocols](images/toptalkers.gif)
##### Show all the used protocols:
```bash
python -m analyser --file capture.pcapng --showprotocols
````
![Demo --showprotocols](images/showprotocols.gif)
---

## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

---
## Author
**Daniël Schiffers**  
Amsterdam University of Applied Sciences  
📧 [daniel.schiffers@hva.nl](mailto:daniel.schiffers@hva.nl)



