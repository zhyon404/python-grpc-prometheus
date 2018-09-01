#!/usr/bin/env python
from setuptools import find_packages
from setuptools import setup

setup(name='python_grpc_prometheus',
      version='0.1.0',
      description='Python gRPC Prometheus Interceptors',
      author='Zhang Yong',
      author_email='yongzhang1@foxmail.com',
      install_requires=[
          'setuptools==39.0.1',
          'prometheus_client==0.3.1'
      ],
      packages=find_packages(exclude=["tests.*", "tests"]),
      )
