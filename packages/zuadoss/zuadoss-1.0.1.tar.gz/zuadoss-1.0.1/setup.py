#!/usr/bin/env python3
"""
ZUAD OSS Python SDK 安装脚本
"""

from setuptools import setup, find_packages
import os

# 读取README文件
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "ZUAD OSS Python SDK - 兼容OSS接口的对象存储Python客户端SDK"

# 直接指定版本号，避免读取问题
def read_version():
    return "1.0.1"

setup(
    name="zuadoss",
    version=read_version(),
    author="ZUAD OSS Team",
    author_email="support@zuadoss.com",
    description="ZUAD OSS Python SDK - 兼容OSS接口的对象存储Python客户端SDK",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/zuadoss/zuadoss-python-sdk",
    packages=["zuadoss"],
    package_data={
        "": ["README.md", "LICENSE", "CHANGELOG.md"],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Archiving",
        "Topic :: Utilities",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
    ],
    keywords=[
        "oss", "object-storage", "cloud-storage", "s3-compatible",
        "zuad", "zuadoss", "storage", "sdk", "python"
    ],
    project_urls={
        "Bug Reports": "https://github.com/zuadoss/zuadoss-python-sdk/issues",
        "Source": "https://github.com/zuadoss/zuadoss-python-sdk",
        "Documentation": "https://zuadoss.readthedocs.io/",
        "Homepage": "https://zuadoss.com",
    },
    include_package_data=True,
    zip_safe=False,
    license="MIT",
) 