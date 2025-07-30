from setuptools import setup, find_packages

setup(
    name="mftfwscan",
    version="0.1.0",
    description="Simulate and audit firewall/NAT rules for Managed File Transfer (MFT) environments",
    author="Your Name",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'mftfwscan = main:main',
        ],
    },
    python_requires='>=3.7',
    install_requires=[],
)
