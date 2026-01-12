#!/usr/bin/env python3
"""
AI-RecoverOps Setup Script
Universal DevOps Automation Platform
"""

from setuptools import setup, find_packages
import os

# Read README for long description
def read_readme():
    with open('README.md', 'r', encoding='utf-8') as f:
        return f.read()

# Read requirements
def read_requirements():
    with open('requirements.txt', 'r') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name='ai-recoverops',
    version='1.0.0',
    description='Universal DevOps Automation Platform with AI-powered incident detection and remediation',
    long_description=read_readme(),
    long_description_content_type='text/markdown',
    author='AI-RecoverOps Team',
    author_email='team@ai-recoverops.com',
    url='https://github.com/ai-recoverops/ai-recoverops',
    license='MIT',
    
    packages=find_packages(),
    include_package_data=True,
    
    install_requires=[
        'click>=8.0.0',
        'pyyaml>=6.0',
        'requests>=2.25.0',
        'fastapi>=0.104.0',
        'uvicorn>=0.24.0',
        'pydantic>=2.4.0',
        'pandas>=1.5.0',
        'numpy>=1.21.0',
        'scikit-learn>=1.1.0',
        'psutil>=5.8.0',
        'jinja2>=3.0.0',
        'rich>=13.0.0',
        'typer>=0.9.0'
    ],
    
    extras_require={
        'aws': ['boto3>=1.26.0', 'botocore>=1.29.0'],
        'azure': ['azure-mgmt-compute>=29.0.0', 'azure-identity>=1.12.0'],
        'gcp': ['google-cloud-compute>=1.11.0', 'google-auth>=2.16.0'],
        'kubernetes': ['kubernetes>=25.0.0'],
        'docker': ['docker>=6.0.0'],
        'dev': ['pytest>=7.0.0', 'black>=22.0.0', 'flake8>=5.0.0']
    },
    
    entry_points={
        'console_scripts': [
            'aiops=ai_recoverops.cli:main',
            'ai-recoverops=ai_recoverops.cli:main',
        ],
    },
    
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: System :: Systems Administration',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Monitoring',
        'Topic :: System :: Networking :: Monitoring',
    ],
    
    python_requires='>=3.8',
    
    keywords='devops automation monitoring remediation ai infrastructure ansible terraform',
    
    project_urls={
        'Documentation': 'https://docs.ai-recoverops.com',
        'Source': 'https://github.com/ai-recoverops/ai-recoverops',
        'Tracker': 'https://github.com/ai-recoverops/ai-recoverops/issues',
    },
)