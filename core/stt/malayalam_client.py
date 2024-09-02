import io
import torch
import numpy as np
import logging
from transformers import AutoModelForCTC, AutoProcessor

class MalayalamSTT:
    def __init__(self, model_id="Bajiyo/w2v-bert-2.0-nonstudio_and_studioRecords_final", language="ml"):
        self.model_id = model_id
        self.language = language
        self.fs = 16000  # Sampling rate
        self.device = torch.device("cpu")
        
        logging.info(f"Initializing MalayalamSTT with model: {self.model_id} and language: {self.language}")

        # Load ASR model and processor
        self.asr_processor = AutoProcessor.from_pretrained(self.model_id)
        self.asr_model = AutoModelForCTC.from_pretrained(self.model_id).to(self.device)
        
        logging.info("ASR model and processor loaded successfully")

    async def transcribe_stream(self, audio_buffer: io.BytesIO):
        """Transcribe audio stream from the buffer, yielding text chunks."""
        # Convert the BytesIO buffer to bytes
        audio_data = np.frombuffer(audio_buffer.getvalue(), dtype=np.int16)

        # Check if audio data is valid
        if len(audio_data) == 0:
            logging.error("Audio data is empty.")
            yield "<EOF>"  # Return <EOF> if there's no valid audio data

        logging.info(f"Audio data length: {len(audio_data)}")

        # Normalize and prepare input for the model
        audio_tensor = torch.FloatTensor(audio_data.astype(np.float32) / np.iinfo(np.int16).max).to(self.device)

        logging.info(f"Audio tensor shape: {audio_tensor.shape}")

        # Ensure the tensor is not empty and has a valid shape
        if audio_tensor.numel() == 0 or audio_tensor.shape[0] < 160:
            logging.warning(f"Invalid tensor shape: {audio_tensor.shape}. Returning <EOF>.")
            yield "<EOF>"  # Return <EOF> if the audio data is too short

        try:
            # Process the audio tensor with the processor
            inputs = self.asr_processor(audio_tensor, sampling_rate=16000, return_tensors="pt", padding=True).to(self.device)

            # Debugging: check the structure of the inputs
            logging.info(f"Processor output keys: {inputs.keys()}")

            # Use 'input_features' instead of 'input_values'
            if 'input_features' in inputs:
                input_features = inputs['input_features']
                logging.info(f"Input features shape: {input_features.shape}")
            else:
                logging.error(f"'input_features' key not found in inputs. Available keys: {inputs.keys()}")
                yield "<EOF>"
                return

            # Perform inference
            with torch.no_grad():
                outputs = self.asr_model(input_features=input_features, attention_mask=inputs['attention_mask']).logits

            # Decode the model output to text
            predicted_ids = torch.argmax(outputs, dim=-1)[0]
            transcription = self.asr_processor.batch_decode(predicted_ids.unsqueeze(0))[0].strip()

            if transcription:
                logging.info(f"Transcription result: {transcription}")
                yield transcription
            else:
                logging.info("Empty transcription result, returning <EOF>")
                yield "<EOF>"

        except Exception as e:
            logging.error(f"Error during transcription: {e}")
            yield "<EOF>"  # Yield <EOF> in case of error