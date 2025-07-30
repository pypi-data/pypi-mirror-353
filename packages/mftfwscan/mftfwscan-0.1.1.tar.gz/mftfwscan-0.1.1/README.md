# == README.md ==

# mftfwscan

`mftfwscan` is a command-line toolkit to simulate and audit firewall/NAT rules commonly used in Managed File Transfer (MFT) environments.

## Features
- Simulate inbound port rules for SFTP, FTPS, AS2, and Passive FTP
- Identify potential misconfigurations like open high ports or unrestricted sources
- Export rules as iptables, GCP firewall, or AWS security group formats

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

---

## Example Output

```bash
$ mftfwscan --service SFTP --export iptables
-A INPUT -p tcp --dport 22 -s 0.0.0.0/0 -j ACCEPT
[!] Rule open to all IPs for port 22
```


# == LICENSE (MIT) ==

MIT License

Copyright (c) 2025 Raghava Chellu

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

