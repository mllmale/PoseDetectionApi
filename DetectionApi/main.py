# Importa as bibliotecas necessárias
import asyncio  # Para operações assíncronas
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException  # Para criar a aplicação web e lidar com WebSocket
from fastapi.responses import HTMLResponse, JSONResponse  # Para retornar respostas HTML e JSON
from fastapi.staticfiles import StaticFiles  # Para servir arquivos estáticos
import cv2  # OpenCV para processamento de vídeo
from detection import Detection  # Importa a classe Detection para detecção de poses

# Cria uma instância da aplicação FastAPI
app = FastAPI()

# Monta a pasta estática para servir arquivos como CSS, JavaScript e imagens
app.mount("/static", StaticFiles(directory="static"), name="static")

# Inicializa a classe de detecção de pose
detector = Detection()

# Define uma rota padrão para a página inicial
@app.get("/")
async def get():
    return HTMLResponse(open("static/index.html").read())

# Define um ponto de extremidade WebSocket para lidar com a comunicação WebSocket
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()  # Aceita a conexão WebSocket
    cap = cv2.VideoCapture(0)  # Inicia a captura de vídeo da webcam
    if not cap.isOpened():  # Verifica se a captura de vídeo foi aberta com sucesso
        print("Error: Could not open video device.")
        return

    try:
        while True:
            ret, frame = cap.read()  # Lê um frame do vídeo
            if not ret:  # Verifica se o frame foi lido com sucesso
                print("Error: Failed to read frame from video device.")
                break

            frame = cv2.flip(frame, 1)  # Espelha o frame horizontalmente
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Converte o frame para o espaço de cores RGB
            results = detector.pose.process(frame_rgb)  # Processa o frame em busca de poses humanas

            if results.pose_landmarks:  # Verifica se foram encontradas landmarks de pose no frame
                if detector.side:  # Verifica se o lado da detecção foi especificado
                    detector.detect_side(frame, results.pose_landmarks.landmark)  # Usa o lado especificado

            _, buffer = cv2.imencode('.jpg', frame)  # Codifica o frame como JPEG
            frame_bytes = buffer.tobytes()  # Converte o frame codificado em bytes
            await websocket.send_bytes(frame_bytes)  # Envia o frame via WebSocket
            await asyncio.sleep(0)  # Aguarda um curto período para permitir que outras tarefas sejam executadas

    # Captura possíveis exceções durante a comunicação WebSocket
    except WebSocketDisconnect:
        cap.release()  # Libera o recurso da webcam
        print("WebSocket disconnected.")
    except Exception as e:
        print(f"Error: {e}")  # Exibe possíveis erros
        cap.release()  # Libera o recurso da webcam

    # Garante que o recurso da webcam seja liberado mesmo em caso de exceção
    finally:
        cap.release()  # Libera o recurso da webcam

# Define um ponto de extremidade POST que permite definir o lado para a detecção de pose
@app.post("/set_side/{side}")
async def set_side(side: str):
    print(f"Received side: {side}")  # Exibe o lado recebido
    detector.side = side  # Define o lado para a detecção de pose
    print(f"Setting side to: {detector.side}")  # Exibe o lado definido
    return JSONResponse(content={"side": detector.side}, status_code=200)  # Retorna o lado definido como resposta JSON
