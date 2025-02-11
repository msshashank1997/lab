from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from voice_handler import VoiceHandler
from conclude_answer import return_answer
import uvicorn
from pydantic import BaseModel

app = FastAPI()
voice_handler = VoiceHandler()

class TextRequest(BaseModel):
    text: str

@app.websocket("/ws/audio")
async def websocket_endpoint(websocket: WebSocket):
    try:
        await websocket.accept()
        await voice_handler.process_audio_stream(websocket)
    except WebSocketDisconnect:
        print("WebSocket disconnected")
    except Exception as e:
        print(f"Error: {str(e)}")

@app.post("/process-text")
async def process_text(request: TextRequest):
    try:
        # Process the text through your existing flow
        result = return_answer(request.text, None)
        return {"response": result}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
