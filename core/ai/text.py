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

def concise_transcription(transcription: str, language: str) -> str:
    prompt = concise_prompt.format(transcription)
    response = LLM(language).inference(prompt, ProcessedText)
    return response.processed_text

def highlight_keywords(transcription: str, language: str) -> str:
    prompt = highlight_prompt.format(transcription)
    response = LLM(language).inference(prompt, ProcessedText)
    return response.processed_text

def should_summarize(transcription: str, language: str) -> bool:
    prompt = decision_prompt.format(transcription)
    response = LLM(language).inference(prompt, ProcessingDecision)
    return response.decision

def correct_transcription(transcription: str, base_model: str) -> str:
    prompt = correction_prompt.format(transcription)
    response = LLM(base_model).inference(prompt, ProcessedText)
    return response.processed_text

def process_transcription(transcription: str, language: str) -> str:
    if should_summarize(transcription, language):
        response = concise_transcription(transcription, language)
        type = "concise"
    else:
        response = highlight_keywords(transcription, language)
        type = "highlight"
    return {"text": response, "type": type} if response else {} 