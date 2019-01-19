from __future__ import print_function
import logging
import time

import grpc

import helloworld_pb2
import helloworld_pb2_grpc

import prometheus_client
from python_grpc_prometheus.prometheus_client_interceptor import PromClientInterceptor

_ONE_DAY_IN_SECONDS = 60 * 60 * 24


def run():
    interceptor = PromClientInterceptor()
    with grpc.insecure_channel('localhost:50051') as channel:
        intercept_channel = grpc.intercept_channel(channel,
                                                   interceptor)
        stub = helloworld_pb2_grpc.GreeterStub(intercept_channel)
        response = stub.SayHello.future(helloworld_pb2.HelloRequest(name='you'))
        response=response.result()
    print("Greeter client received: " + response.message)


if __name__ == '__main__':
    logging.basicConfig()
    try:
        run()
    except Exception as e:
        print(e)
    prometheus_client.start_http_server(8001)
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        pass