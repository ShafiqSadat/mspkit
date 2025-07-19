from setuptools import setup, find_packages
import os

# Read README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "A comprehensive Python SDK for iNav and Betaflight flight controllers"

setup(
    name="mspkit",
    version="0.2.0",
    description="SDK for iNav and Betaflight using MSP v1/v2",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="MSPKit Contributors",
    author_email="",  # Add your email here
    url="https://github.com/ShafiqSadat/mspkit",  # Add your repo URL
    project_urls={
        "Bug Reports": "https://github.com/ShafiqSadat/mspkit/issues",
        "Source": "https://github.com/ShafiqSadat/mspkit",
        "Documentation": "https://github.com/ShafiqSadat/mspkit/wiki",
    },
    packages=find_packages(),
    include_package_data=True,
    
    # Dependencies
    install_requires=[
        "pyserial>=3.4",
    ],
    
    # Optional dependencies for development
    extras_require={
        'dev': [
            'pytest>=6.0',
            'pytest-cov>=2.0',
            'black>=21.0',
            'isort>=5.0',
            'flake8>=3.8',
            'mypy>=0.812',
        ],
        'examples': [
            'matplotlib>=3.0',
            'numpy>=1.19',
        ]
    },
    
    # Classifiers
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator",
        "Topic :: System :: Hardware :: Hardware Drivers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8", 
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Environment :: Console",
    ],
    
    # Requirements
    python_requires=">=3.7",
    
    # Keywords for PyPI search
    keywords="inav betaflight msp drone uav flight-controller multiwii cleanflight mspkit",
    
    # Entry points (CLI tools)
    entry_points={
        'console_scripts': [
            'mspkit=mspkit.cli:main',
        ],
    },
    
    # License
    license="MIT",
    
    # Zip safe
    zip_safe=False,
)
