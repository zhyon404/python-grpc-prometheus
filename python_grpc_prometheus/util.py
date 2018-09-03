import grpc

Unary = "unary"
ClientStream = "client_stream"
ServerStream = "server_stream"
BidiStream = "bidi_stream"


def type_from_method(request_streaming, response_streaming):
    if not request_streaming and not response_streaming:
        return Unary
    elif request_streaming and not response_streaming:
        return ClientStream
    elif not request_streaming and response_streaming:
        return ServerStream
    else:
        return BidiStream


GRPC_STATUS_CODE_TO_STRING = {
    grpc.StatusCode.OK: "OK",
    grpc.StatusCode.CANCELLED: "Canceled",
    grpc.StatusCode.UNKNOWN: "Unknown",
    grpc.StatusCode.INVALID_ARGUMENT: "InvalidArgument",
    grpc.StatusCode.DEADLINE_EXCEEDED: "DeadlineExceeded",
    grpc.StatusCode.NOT_FOUND: "NotFound",
    grpc.StatusCode.ALREADY_EXISTS: "AlreadyExists",
    grpc.StatusCode.PERMISSION_DENIED: "PermissionDenied",
    grpc.StatusCode.UNAUTHENTICATED: "Unauthenticated",
    grpc.StatusCode.RESOURCE_EXHAUSTED: "ResourceExhausted",
    grpc.StatusCode.FAILED_PRECONDITION: "FailedPrecondition",
    grpc.StatusCode.ABORTED: "Aborted",
    grpc.StatusCode.OUT_OF_RANGE: "OutOfRange",
    grpc.StatusCode.UNIMPLEMENTED: "Unimplemented",
    grpc.StatusCode.INTERNAL: "Internal",
    grpc.StatusCode.UNAVAILABLE: "Unavailable",
    grpc.StatusCode.DATA_LOSS: "DataLoss",
}


def code_to_string(code):
    if code is None:
        return None
    s = GRPC_STATUS_CODE_TO_STRING.get(code)
    if s:
        return s
    else:
        return code.name
