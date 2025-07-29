from setuptools import setup, find_packages

setup(
    name='pcap-analyzer',
    version='1.0.1',
    description='A lightweight CLI tool to analyze PCAP files',
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author='Daniël Schiffers',
    author_email='daniel.schiffers@hva.nl',
    url='https://github.com/schiffd/pcap-analyzer',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "scapy==2.6.1"
    ],
    extras_require={
        "dev": [
            "pytest"
        ]
    },
    entry_points={
        'console_scripts': [
            'pcap-analyser=analyser.main:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: System :: Networking :: Monitoring",
    ],
    python_requires='>=3.7',
    license='MIT'
)
