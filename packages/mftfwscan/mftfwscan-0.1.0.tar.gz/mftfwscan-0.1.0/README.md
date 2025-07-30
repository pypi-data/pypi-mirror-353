"""
# mftfwscan

`mftfwscan` is a Python CLI tool to simulate and audit firewall/NAT rules for Managed File Transfer (MFT) environments.

## Features
- Simulate rules for SFTP, FTPS, AS2, and Passive FTP
- Detect risky firewall configurations
- Export iptables, GCP firewall, or AWS Security Group templates

## Installation
```bash
pip install .
```

## Usage
```bash
mftfwscan --service SFTP --export iptables
```

## Requirements
- Python 3.7+

"""

