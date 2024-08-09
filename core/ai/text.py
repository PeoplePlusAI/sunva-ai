from groq import Groq

with open("prompts/concise.txt", "r") as f:
    concise_prompt = f.read()

with open("prompts/highlight.txt", "r") as f:
    highlight_prompt = f.read()

with open("prompts/decision.txt", "r") as f:
    decision_prompt = f.read()

with open("prompts/correction.txt", "r") as f:
    correction_prompt = f.read()

def concise_transcription(transcription: str, client: Groq) -> str:
    chat_completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {
                "role": "system",
                "content": concise_prompt.format(transcription)
            }
        ]
    )
    return chat_completion.choices[0].message.content

def highlight_keywords(transcription: str, client: Groq) -> str:
    chat_completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {
                "role": "system",
                "content": highlight_prompt.format(transcription)
            }
        ]
    )
    return chat_completion.choices[0].message.content

def should_summarize(transcription: str, client: Groq) -> bool:
    chat_completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {
                "role": "system",
                "content": decision_prompt.format(transcription)
            }
        ]
    )
    response = chat_completion.choices[0].message.content
    return response.lower() == "yes"

def correct_transcription(transcription: str, client: Groq) -> str:
    chat_completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {
                "role": "system",
                "content": correction_prompt.format(transcription)
            }
        ]
    )
    return chat_completion.choices[0].message.content

def process_transcription(transcription: str, client: Groq) -> str:
    if should_summarize(transcription, client):
        response = concise_transcription(transcription, client)
    else:
        response = highlight_keywords(transcription, client)
    print("Processed text:", response)
    if response == '0' or 0:
        return ""
    else:
        return response