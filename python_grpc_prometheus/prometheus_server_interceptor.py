import grpc
import time

from timeit import default_timer

from python_grpc_prometheus.server_metrics import SERVER_HANDLED_LATENCY_SECONDS
from python_grpc_prometheus.server_metrics import SERVER_HANDLED_COUNTER
from python_grpc_prometheus.server_metrics import SERVER_STARTED_COUNTER

from python_grpc_prometheus.util import type_from_method
from python_grpc_prometheus.util import code_to_string


def _wrap_rpc_behavior(handler, fn):
    if handler is None:
        return None

    if handler.request_streaming and handler.response_streaming:
        behavior_fn = handler.stream_stream
        handler_factory = grpc.stream_stream_rpc_method_handler
    elif handler.request_streaming and not handler.response_streaming:
        behavior_fn = handler.stream_unary
        handler_factory = grpc.stream_unary_rpc_method_handler
    elif not handler.request_streaming and handler.response_streaming:
        behavior_fn = handler.unary_stream
        handler_factory = grpc.unary_stream_rpc_method_handler
    else:
        behavior_fn = handler.unary_unary
        handler_factory = grpc.unary_unary_rpc_method_handler

    return handler_factory(fn(behavior_fn,
                              handler.request_streaming,
                              handler.response_streaming),
                           request_deserializer=handler.request_deserializer,
                           response_serializer=handler.response_serializer)


class PromServerInterceptor(grpc.ServerInterceptor):

    def intercept_service(self, continuation, handler_call_details):

        handler = continuation(handler_call_details)

        # only support unary
        if handler.request_streaming or handler.response_streaming:
            return handler

        # TODO ss = handler_call_details.method.split("/")
        client_call_method = handler_call_details.method
        ss = client_call_method.split("/")
        if len(ss) < 3:
            return continuation(handler_call_details)

        # TODO grpc_service, grpc_method = ss[1:3]
        grpc_service = ss[1]
        grpc_method = ss[2]
        grpc_type = type_from_method(handler.request_streaming, handler.response_streaming)

        SERVER_STARTED_COUNTER.labels(
            grpc_type=grpc_type,
            grpc_service=grpc_service,
            grpc_method=grpc_method).inc()

        def latency_wrapper(behavior, request_streaming, response_streaming):
            def new_behavior(request_or_iterator, service_context):
                start = default_timer()
                try:
                    rsp = behavior(request_or_iterator, service_context)
                    if service_context._state.code is None:
                        SERVER_HANDLED_COUNTER.labels(
                            grpc_type=grpc_type,
                            grpc_service=grpc_service,
                            grpc_method=grpc_method,
                            grpc_code=code_to_string(grpc.StatusCode.OK)
                        ).inc()
                    else:
                        SERVER_HANDLED_COUNTER.labels(
                            grpc_type=grpc_type,
                            grpc_service=grpc_service,
                            grpc_method=grpc_method,
                            grpc_code=code_to_string(service_context._state.code)
                        ).inc()
                    return rsp
                except grpc.RpcError as e:
                    if isinstance(e, grpc.Call):
                        SERVER_HANDLED_COUNTER.labels(
                            grpc_type=grpc_type,
                            grpc_service=grpc_service,
                            grpc_method=grpc_method,
                            grpc_code=code_to_string(e.code())
                        ).inc()
                    else:
                        SERVER_HANDLED_COUNTER.labels(
                            grpc_type=grpc_type,
                            grpc_service=grpc_service,
                            grpc_method=grpc_method,
                            grpc_code=code_to_string(grpc.StatusCode.UNKNOWN)
                        ).inc()
                    raise e
                finally:
                    SERVER_HANDLED_LATENCY_SECONDS.labels(
                        grpc_type=grpc_type,
                        grpc_service=grpc_service,
                        grpc_method=grpc_method).observe(max(default_timer() - start, 0))

            return new_behavior

        return _wrap_rpc_behavior(continuation(handler_call_details), latency_wrapper)


class ServiceLatencyInterceptor(grpc.ServerInterceptor):

    # TODO rm no-op
    def __init__(self):
        pass

    def intercept_service(self, continuation, handler_call_details):
        # TODO see above
        client_call_method = handler_call_details.method
        parts = client_call_method.split("/")

        # TODO
        # if len(parts) < 3:
        # TODO ?
        #     return continuation(handler_call_details)

        grpc_service = parts[1]
        grpc_method = parts[2]

        def latency_wrapper(behavior, request_streaming, response_streaming):
            def new_behavior(request_or_iterator, service_context):
                start = time.time()
                try:
                    return behavior(request_or_iterator, service_context)
                finally:
                    SERVER_HANDLED_LATENCY_SECONDS.labels(
                        grpc_type='UNARY',
                        grpc_service=grpc_service,
                        grpc_method=grpc_method).observe(max(time.time() - start, 0))

            return new_behavior

        return _wrap_rpc_behavior(continuation(handler_call_details), latency_wrapper)
