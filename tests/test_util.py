from unittest import TestCase
from unittest.mock import Mock

from nose.tools import assert_equal
from parameterized import parameterized

import grpc
from python_grpc_prometheus import util


class TestUtil(TestCase):
    # Mock(name=) would overlap with Mock's own name kwarg
    mock_status = Mock()
    mock_status.name = "bar"

    @parameterized.expand([
        (False, False, util.Unary),
        (False, True, util.ServerStream),
        (True, False, util.ClientStream),
        (True, True, util.BidiStream),
    ])
    def test_type_from_method(self, request_streaming, response_streaming, expected_type):
        grpc_type = util.type_from_method(request_streaming, response_streaming)
        assert_equal(grpc_type, expected_type)

    @parameterized.expand([
        (None, None),
        (grpc.StatusCode.OK, "OK"),
        (grpc.StatusCode.CANCELLED, "Canceled"),
        (grpc.StatusCode.UNKNOWN, "Unknown"),
        (grpc.StatusCode.INVALID_ARGUMENT, "InvalidArgument"),
        (grpc.StatusCode.DEADLINE_EXCEEDED, "DeadlineExceeded"),
        (grpc.StatusCode.NOT_FOUND, "NotFound"),
        (grpc.StatusCode.ALREADY_EXISTS, "AlreadyExists"),
        (grpc.StatusCode.PERMISSION_DENIED, "PermissionDenied"),
        (grpc.StatusCode.UNAUTHENTICATED, "Unauthenticated"),
        (grpc.StatusCode.RESOURCE_EXHAUSTED, "ResourceExhausted"),
        (grpc.StatusCode.FAILED_PRECONDITION, "FailedPrecondition"),
        (grpc.StatusCode.ABORTED, "Aborted"),
        (grpc.StatusCode.OUT_OF_RANGE, "OutOfRange"),
        (grpc.StatusCode.UNIMPLEMENTED, "Unimplemented"),
        (grpc.StatusCode.INTERNAL, "Internal"),
        (grpc.StatusCode.UNAVAILABLE, "Unavailable"),
        (grpc.StatusCode.DATA_LOSS, "DataLoss"),
        (mock_status, "bar")
    ])
    def test_code_to_string(self, code, expected):
        res = util.code_to_string(code)
        assert_equal(res, expected)
