from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import cv2
import asyncio
import base64

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

camera = cv2.VideoCapture(0)  # Initialize the USB camera

@app.get("/")
async def root():
    return {"message": "This shit works"}

@app.websocket("/ws/video")
async def video_stream(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Capture a frame from the camera
            success, frame = camera.read()
            if not success:
                break

            # Add timestamp to the frame
            from datetime import datetime
            now = datetime.now()
            timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.7
            color = (255, 255, 255)  # White color in BGR
            thickness = 1
            position = (10, frame.shape[0] - 10)  # Bottom-left corner
            cv2.putText(frame, timestamp, position, font, font_scale, color, thickness, cv2.LINE_AA)

            # Encode the frame as JPEG
            _, encoded_frame = cv2.imencode(".jpg", frame)

            # Convert to base64 to send as text over WebSocket
            frame_data = base64.b64encode(encoded_frame).decode("utf-8")
            await websocket.send_text(frame_data)

            await asyncio.sleep(0.03)  # ~30 FPS
    except WebSocketDisconnect:
        print("Client disconnected")