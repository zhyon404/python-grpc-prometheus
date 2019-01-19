from prometheus_client import Counter
from prometheus_client import Histogram


CLIENT_STARTED_COUNTER = Counter(
    'grpc_client_started_total',
    'Total number of RPCs started on the client.',
    ["grpc_type", "grpc_service", "grpc_method"])

CLIENT_HANDLED_COUNTER = Counter(
    'grpc_client_handled_total',
    'Total number of RPCs completed by the client, regardless of success or failure.',
    ["grpc_type", "grpc_service", "grpc_method", "grpc_code"])

CLIENT_HANDLED_LATENCY_SECONDS = Histogram(
    'grpc_client_handling_seconds',
    'Histogram of response latency (seconds) of the gRPC until it is finished by the application.',
    ["grpc_type", "grpc_service", "grpc_method"])

CLIENT_MSG_RECEIVED_TOTAL = Counter(
    'grpc_client_msg_received_total',
    'Total number of RPC stream messages received by the client.',
    ["grpc_type", "grpc_service", "grpc_method"])

CLIENT_MSG_SENT_TOTAL = Counter(
    'grpc_client_msg_sent_total',
    'Total number of gRPC stream messages sent by the client.',
    ["grpc_type", "grpc_service", "grpc_method"])
