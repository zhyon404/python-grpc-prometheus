#!/usr/bin/env python
from setuptools import find_packages
from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='python_grpc_prometheus',
      version='0.1.1',
      description='Python gRPC Prometheus Interceptors',
      long_description=long_description,
      long_description_content_type="text/markdown",
      author='Zhang Yong',
      author_email='yongzhang1@foxmail.com',
      url="https://github.com/zhyon404/python-grpc-prometheus",
      install_requires=[
          'setuptools>=39.0.1',
          'prometheus_client>=0.3.1'
      ],
      license='MIT',
      packages=find_packages(exclude=["tests.*", "tests"]),
      )
