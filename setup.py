#!/usr/bin/env python

from setuptools import find_packages
from setuptools import setup


with open("README.md", "r") as fh:
    long_description = fh.read()
with open('requirements.txt', 'r') as f:
    requirements = f.read().split()

setup(name='python_grpc_prometheus',
      version='0.2.0',
      description='Python gRPC Prometheus Interceptors',
      long_description=long_description,
      long_description_content_type="text/markdown",
      author='Zhang Yong',
      author_email='yongzhang1@foxmail.com',
      url="https://github.com/zhyon404/python-grpc-prometheus",
      install_requires=requirements,
      license='MIT',
      packages=find_packages(exclude=["tests"]),
      )
