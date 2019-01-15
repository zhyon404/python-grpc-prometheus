from unittest import TestCase
from unittest.mock import Mock

from nose.tools import assert_equal, assert_is_none
from parameterized import parameterized

import requests
from concurrent import futures
import grpc
import prometheus_client
import tests.greeter_pb2_grpc as rpc
from tests.greeter_pb2 import HelloReply, HelloRequest

from python_grpc_prometheus import prometheus_server_interceptor as psi


class TestPrometheusServerInterceptor(TestCase):
    def setUp(self):
        self.psi = psi.PromServerInterceptor()

    @parameterized.expand([
        (True, True, 1),
        (True, False, 1),
        (False, True, 1),
        (False, False, 2),
    ])
    def test_intercept_service_unary(self, request_streaming, response_streaming, calls):
        mock_handler_call_details = Mock(method="/grp-service")
        mock_handler = Mock(request_streaming=request_streaming, response_streaming=response_streaming)
        mock_continuation = Mock(return_value=mock_handler)

        self.psi.intercept_service(mock_continuation, mock_handler_call_details)
        assert_equal(calls, mock_continuation.call_count)

    @parameterized.expand([
        ("/grpc-service-only"),
        ("/grpc-service/grpc-method"),
    ])
    def test_intercept_service_method_name_too_short(self, method):
        mock_handler_call_details = Mock(method=method)
        mock_handler = Mock(request_streaming=False, response_streaming=False)
        mock_continuation = Mock(return_value=mock_handler)

        self.psi.intercept_service(mock_continuation, mock_handler_call_details)
        assert_equal(2, mock_continuation.call_count)

    def test_none_handler(self):
        mock_continuation = Mock(return_value=None)

        ret = self.psi.intercept_service(mock_continuation, Mock())
        assert_is_none(ret)

class TestServiceLatencyInterceptor(TestCase):
    def setUp(self):
        self.sli = psi.ServiceLatencyInterceptor()

    @parameterized.expand([
        ("/grpc-service-only"),
        ("/grpc-service/grpc-method"),
    ])
    def test_intercept_service_method_name_too_short(self, method):
        mock_handler_call_details = Mock(method=method)
        mock_handler = Mock(request_streaming=False, response_streaming=False)
        mock_continuation = Mock(return_value=mock_handler)

        self.sli.intercept_service(mock_continuation, mock_handler_call_details)
        assert_equal(1, mock_continuation.call_count)


class Test_wrap_rpc_behavior(TestCase):

    @parameterized.expand([
        (True, True, "stream_stream"),
        (True, False, "stream_unary"),
        (False, True, "unary_stream"),
        (False, False, "unary_unary"),
    ])
    def test_wrap_rpc_behavior(self, request_streaming, response_streaming, behavior):
        mock_handler = Mock(request_streaming=request_streaming, response_streaming=response_streaming)
        mock_fn = Mock()
        res = psi._wrap_rpc_behavior(mock_handler, mock_fn)
        assert_equal(1, mock_fn.call_count)
        assert getattr(res, behavior) is not None

    def test_wrap_rpc_behavior_none(self):
        assert_equal(None, psi._wrap_rpc_behavior(None, Mock()))


# simple gRPC server for interception tests
class Greeter(rpc.GreeterServicer):
    def SayHello(self, request, context):
        return HelloReply(message='Hello, %s!' % request.name)


def grpc_serve(interceptor):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10),
                         interceptors=(interceptor,))
    rpc.add_GreeterServicer_to_server(Greeter(), server)
    server.add_insecure_port('localhost:50051')
    server.start()
    return server


def get_free_port():
    from socket import socket
    with socket() as s:
        s.bind(('', 0))
        return s.getsockname()[1]


class TestMetrics(TestCase):
    def setUp(self):
        # gRPC server
        self.server = grpc_serve(interceptor=psi.PromServerInterceptor())

        # metrics server
        self.port = get_free_port()
        prometheus_client.start_http_server(self.port)

        # gRPC client
        channel = grpc.insecure_channel('localhost:50051')
        self.stub = rpc.GreeterStub(channel)

    def tearDown(self):
        self.server.stop(grace=1)

    @parameterized.expand([
        ('grpc_server_msg_received_total{grpc_method="SayHello",grpc_service="Greeter",grpc_type="unary"}', 1.0),
        ('grpc_server_msg_sent_total{grpc_method="SayHello",grpc_service="Greeter",grpc_type="unary"}', 2.0),
        ('grpc_server_started_total{grpc_method="SayHello",grpc_service="Greeter",grpc_type="unary"}', 3.0),
        ('grpc_server_handled_total{grpc_code="OK",grpc_method="SayHello",grpc_service="Greeter",grpc_type="unary"}', 4.0),
    ])
    def test_grpc_server_metrics(self, metric_name, value):
        _ = self.stub.SayHello(request=HelloRequest(name="foo"))
        r = requests.get("http://localhost:{port}".format(port=self.port))
        assert '{metric} {value}'.format(metric=metric_name, value=value) in r.text, \
            "expected metric {metric}={value} not found in server response:\n{resp}".format(metric=metric_name, value=value, resp=r.text)
