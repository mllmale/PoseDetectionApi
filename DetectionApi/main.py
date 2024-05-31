import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import cv2
import numpy as np
from detection import Detection

app = FastAPI()

# Monta a pasta estática
app.mount("/static", StaticFiles(directory="static"), name="static")

detector = Detection()
# sides = ''
@app.get("/")
async def get():
    return HTMLResponse(open("static/index.html").read())

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open video device.")
        return

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Failed to read frame from video device.")
                break

            frame = cv2.flip(frame, 1)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = detector.pose.process(frame_rgb)

            if results.pose_landmarks:
                if detector.side:
                    detector.detect_side(frame, results.pose_landmarks.landmark)  # Use the updated side

            _, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            await websocket.send_bytes(frame_bytes)
            await asyncio.sleep(0)
    except WebSocketDisconnect:
        cap.release()
        print("WebSocket disconnected.")
    except Exception as e:
        print(f"Error: {e}")
        cap.release()
    finally:
        cap.release()


@app.post("/set_side/{side}")
async def set_side(side: str):
    print(f"Received side: {side}")
    detector.side = side
    print(f"Setting side to: {detector.side}")
    return JSONResponse(content={"side": detector.side}, status_code=200)
