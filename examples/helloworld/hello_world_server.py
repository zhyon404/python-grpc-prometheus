from concurrent import futures
import time
import logging

import grpc

import helloworld_pb2
import helloworld_pb2_grpc

import prometheus_client
from python_grpc_prometheus.prometheus_server_interceptor import PromServerInterceptor

_ONE_DAY_IN_SECONDS = 60 * 60 * 24


class Greeter(helloworld_pb2_grpc.GreeterServicer):

    def SayHello(self, request, context):
        return helloworld_pb2.HelloReply(message='Hello, %s!' % request.name)


def serve():
    # Add the required interceptor(s) where you create your grpc server, e.g.
    psi = PromServerInterceptor()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10), interceptors=(psi,))
    helloworld_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    prometheus_client.start_http_server(8000)
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    logging.basicConfig()
    serve()
