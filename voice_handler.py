import asyncio
import websockets
import json
import grpc
from typing import Generator
import json
import wave
import numpy as np
from riva.client.audio_io import AudioIO
from riva.client.argparse_utils import add_connection_argparse_parameters
from riva.client import AuthType
from riva.client.proto import riva_asr_pb2, riva_asr_pb2_grpc

class VoiceHandler:
    def __init__(self):
        # Updated Riva server connection settings to match Docker configuration
        self.auth = AuthType.NONE
        self.server = "localhost:50051"  # Matches the NIM_GRPC_API_PORT
        self.channel = grpc.insecure_channel(
            self.server,
            options=[
                ('grpc.max_send_message_length', 83886080),
                ('grpc.max_receive_message_length', 83886080)
            ]
        )
        self.asr_client = riva_asr_pb2_grpc.RivaSpeechRecognitionStub(self.channel)
    
    async def process_audio_stream(self, websocket) -> Generator[str, None, None]:
        # Update config to match Riva's optimized settings
        config = riva_asr_pb2.RecognitionConfig(
            encoding=riva_asr_pb2.LINEAR_PCM,
            sample_rate_hertz=16000,
            audio_channel_count=1,
            language_code="en-US",
            max_alternatives=1,
            enable_automatic_punctuation=True,
            verbatim_transcripts=False,
            profanity_filter=True
        )
        
        streaming_config = riva_asr_pb2.StreamingRecognitionConfig(
            config=config,
            interim_results=True
        )

        # Create request generator
        def request_generator():
            # First request contains config
            yield riva_asr_pb2.StreamingRecognizeRequest(streaming_config=streaming_config)
            
            while True:
                try:
                    message = yield
                    if message == "DONE":
                        break
                    
                    # Convert audio data to proper format if needed
                    audio_chunk = message
                    yield riva_asr_pb2.StreamingRecognizeRequest(audio_content=audio_chunk)
                except StopIteration:
                    break

        req_gen = request_generator()
        next(req_gen)  # Prime the generator

        try:
            # Start streaming recognition
            responses = self.asr_client.StreamingRecognize(req_gen)
            
            async for message in websocket:
                if isinstance(message, str) and message == "DONE":
                    req_gen.send("DONE")
                    break
                else:
                    # Send audio chunk to Riva
                    req_gen.send(message)
                    
                    # Process any available responses
                    for response in responses:
                        if response.results:
                            result = response.results[0]
                            if result.alternatives:
                                transcript = result.alternatives[0].transcript
                                is_final = result.is_final
                                await websocket.send(json.dumps({
                                    "text": transcript,
                                    "is_final": is_final
                                }))
        
        except Exception as e:
            print(f"Error in voice processing: {str(e)}")
            await websocket.send(json.dumps({
                "error": str(e)
            }))
        finally:
            try:
                req_gen.close()
            except:
                pass
