from prometheus_client import Counter
from prometheus_client import Histogram

SERVER_STARTED_COUNTER = Counter(
    'grpc_server_started_total',
    'Total number of RPCs started on the server.',
    ["grpc_type", "grpc_service", "grpc_method"])

SERVER_HANDLED_COUNTER = Counter(
    'grpc_server_handled_total',
    'Total number of RPCs completed on the server, regardless of success or failure.',
    ["grpc_type", "grpc_service", "grpc_method", "grpc_code"])

SERVER_HANDLED_LATENCY_SECONDS = Histogram(
    'grpc_server_handling_seconds',
    'Histogram of response latency (seconds) of gRPC that had been application-level handled by the server.',
    ["grpc_type", "grpc_service", "grpc_method"])

SERVER_MSG_RECEIVED_TOTAL = Counter(
    'grpc_server_msg_received_total',
    'Total number of RPC stream messages received on the server.',
    ["grpc_type", "grpc_service", "grpc_method"])

SERVER_MSG_SENT_TOTAL = Counter(
    'grpc_server_msg_sent_total',
    'Total number of gRPC stream messages sent by the server.',
    ["grpc_type", "grpc_service", "grpc_method"])
