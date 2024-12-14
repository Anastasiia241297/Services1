from concurrent import futures
import grpc
from auth_pb2 import AuthResponse
import auth_pb2_grpc

users_db = {
    "user1": "password1",
    "user2": "password2",
    "user3": "password3",
}

class AuthService(auth_pb2_grpc.AuthServiceServicer):
    def Authenticate(self, request, context):
        if request.login in users_db and users_db[request.login] == request.password:
            return AuthResponse(can_enter=True)
        return AuthResponse(can_enter=False)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    auth_pb2_grpc.add_AuthServiceServicer_to_server(AuthService(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()


