import grpc

import time

from python_grpc_prometheus.client_metrics import (CLIENT_HANDLED_LATENCY_SECONDS,
                                                   CLIENT_HANDLED_COUNTER,
                                                   CLIENT_STARTED_COUNTER,
                                                   CLIENT_MSG_RECEIVED_TOTAL,
                                                   CLIENT_MSG_SENT_TOTAL)

from python_grpc_prometheus import util
from python_grpc_prometheus.util import split_call_details
from python_grpc_prometheus.util import code_to_string


class PromClientInterceptor(grpc.UnaryUnaryClientInterceptor, grpc.UnaryStreamClientInterceptor,
                            grpc.StreamUnaryClientInterceptor,
                            grpc.StreamStreamClientInterceptor):

    @staticmethod
    def _callback(grpc_type, grpc_service, grpc_method, start):
        def callback(future_response):
            exception = future_response.exception()
            code = code_to_string(grpc.StatusCode.OK)
            if exception is not None:
                if isinstance(exception, grpc.Call):
                    code = code_to_string(exception.code())
                else:
                    code = code_to_string(grpc.StatusCode.UNKNOWN)

            CLIENT_HANDLED_COUNTER.labels(
                grpc_type=grpc_type,
                grpc_service=grpc_service,
                grpc_method=grpc_method,
                grpc_code=code
            ).inc()

            CLIENT_HANDLED_LATENCY_SECONDS.labels(
                grpc_type=grpc_type,
                grpc_service=grpc_service,
                grpc_method=grpc_method).observe(max(time.time() - start, 0))

        return callback

    def intercept_unary_unary(self, continuation, client_call_details, request):
        grpc_service, grpc_method, ok = split_call_details(client_call_details, 3)
        if not ok:
            return continuation(client_call_details, request)

        start = time.time()
        grpc_type = util.Unary
        CLIENT_STARTED_COUNTER.labels(
            grpc_type=grpc_type,
            grpc_service=grpc_service,
            grpc_method=grpc_method).inc()
        CLIENT_MSG_SENT_TOTAL.labels(
            grpc_type=grpc_type,
            grpc_service=grpc_service,
            grpc_method=grpc_method).inc()

        try:
            response = continuation(client_call_details, request)
            response.add_done_callback(self._callback(util.Unary, grpc_service, grpc_method, start))
        except grpc.RpcError as e:
            code = code_to_string(grpc.StatusCode.UNKNOWN)
            if isinstance(e, grpc.Call):
                code = code_to_string(e.code())
            CLIENT_HANDLED_COUNTER.labels(
                grpc_type=grpc_type,
                grpc_service=grpc_service,
                grpc_method=grpc_method,
                grpc_code=code
            ).inc()

            CLIENT_HANDLED_LATENCY_SECONDS.labels(
                grpc_type=grpc_type,
                grpc_service=grpc_service,
                grpc_method=grpc_method).observe(max(time.time() - start, 0))
            raise
        return response

    def intercept_unary_stream(self, continuation, client_call_details, request):
        response = continuation(client_call_details, request)
        return response

    def intercept_stream_unary(self, continuation, client_call_details, request_iterator):
        response = continuation(client_call_details, request_iterator)
        return response

    def intercept_stream_stream(self, continuation, client_call_details, request_iterator):
        response = continuation(client_call_details, request_iterator)
        return response
