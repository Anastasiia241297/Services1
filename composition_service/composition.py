import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import grpc
from auth_pb2 import AuthRequest
from score_pb2 import ScoreRequest
import auth_pb2_grpc
import score_pb2_grpc


app = FastAPI()
THRESHOLD_SCORE = 0.5  # Порог для пропуска

class CompositionRequest(BaseModel):
    login: str
    password: str


def get_score(login):
    # Взаимодействие с gRPC-сервисом score
    with grpc.insecure_channel("score_service:50052") as score_channel:
        score_stub = score_pb2_grpc.ScoreServiceStub(score_channel)
        score_response = score_stub.GetScore(ScoreRequest(login=login))
        if score_response.score < THRESHOLD_SCORE:
            return {"can_enter": False}
        else:
            return {"can_enter": True}

def log_in(login, password):
    # Взаимодействие с gRPC-сервисом auth
    with grpc.insecure_channel("auth_service:50051") as auth_channel:
        auth_stub = auth_pb2_grpc.AuthServiceStub(auth_channel)
        auth_response = auth_stub.Authenticate(AuthRequest(login=login, password=password))
        if not auth_response.can_enter:
            # raise HTTPException(status_code=401, detail="Unauthorized")
            return {"can_enter": False}
        return {"can_enter": True}

@app.post("/composition/")
def composition(request: CompositionRequest):

    score_resp = get_score(request.login)
    login_resp = log_in(request.login, request.password)

    if score_resp.get("can_enter") and login_resp.get("can_enter"):
        return {"msg": "Авторизация успешна"}
    elif not login_resp.get("can_enter"):
        return {"msg": "Авторизация не успешна, неверный логин или пароль"}
    elif not score_resp.get("can_enter"):
        return {"msg": "Авторизация не успешна, score меньше порогового значения"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)

