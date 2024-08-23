import json
from core.llm.llm import LLM
from groq import Groq
from core.models.instructor import (
    ProcessedText, 
    ProcessingDecision
)
from core.utils.instructor_utils import patch_client

with open("prompts/concise.txt", "r") as f:
    concise_prompt = f.read()

with open("prompts/highlight.txt", "r") as f:
    highlight_prompt = f.read()

with open("prompts/decision.txt", "r") as f:
    decision_prompt = f.read()

with open("prompts/correction.txt", "r") as f:
    correction_prompt = f.read()

def concise_transcription(transcription: str, base_model: str) -> str:
    prompt = concise_prompt.format(transcription)
    response = LLM(base_model).inference(prompt, ProcessedText)
    return response.processed_text

def highlight_keywords(transcription: str, base_model: str) -> str:
    prompt = highlight_prompt.format(transcription)
    response = LLM(base_model).inference(prompt, ProcessedText)
    return response.processed_text

def should_summarize(transcription: str, base_model: str) -> bool:
    prompt = decision_prompt.format(transcription)
    response = LLM(base_model).inference(prompt, ProcessingDecision)
    return response.decision

def correct_transcription(transcription: str, base_model: str) -> str:
    prompt = correction_prompt.format(transcription)
    response = LLM(base_model).inference(prompt, ProcessedText)
    return response.processed_text

def process_transcription(transcription: str, base_model: str) -> dict:
    style = ""
    if should_summarize(transcription, base_model):
        response = concise_transcription(transcription, base_model)
        style = "concise"
    else:
        response = highlight_keywords(transcription, base_model)
        style = "highlight"
    return {} if response == '0' or 0 else {
        "original_text": transcription,
        "processed_text": response,
        "style": style
    }