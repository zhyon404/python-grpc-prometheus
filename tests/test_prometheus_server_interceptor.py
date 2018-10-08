from unittest import TestCase
from unittest.mock import Mock

from nose.tools import assert_equal
from parameterized import parameterized

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
