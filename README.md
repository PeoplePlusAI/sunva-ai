# SUNVA AI: Seamless conversation loop for the deaf

## About SUNVA AI

Having conversations leveraging existing communication tools can be a challenge for deafs. While so many live transcription and text-to-speech tools are available in the market, they do not cater to the needs of the deaf and hard of hearing and aren't designed with an accessibility focus. 

We are building this focusing on the problem deaf people are facing in India by building prototypes, testing it with the deaf community, and iterating based on the feedback.

### STT 

Often it could take a lot of time for the deaf person to read transcriptions and respond to them depending on various factors from person to person. SUNVA AI intelligently simplifies and provides various filters on the transcriptions to minimize the time taken to read the transcription and switch gaze between the screen and the person while communicating.

### TTS

SUNVA AI provides a text-to-speech + LLM layer features that help the deaf person having speech irregularities to type less and respond more. For example, if the deaf person types "I coffee", SUNVA AI will convert it to "I would like to have a coffee" and speak it out.

### Sunva Frontend

[Sunva frontend](https://github.com/PeoplePlusAI/sunva-frontend) is a single-screen UI where you can read the intelligently simplified transcriptions and write your response, which will be spoken back in the selected speech. Our idea is to build this app, take it to our deaf community volunteers, and based on their feedback, iterate the UI to make it even better. 
  


## SUNVA AI workplan 

The [first version of the POC](https://www.figma.com/proto/xK0fvVJL9wRWTkwdBeRu2U/Sunva.Ai?page-id=84%3A803&node-id=84-805&viewport=917%2C520%2C0.14&t=ZpNPT9hGNjHWzrqy-1&scaling=min-zoom&content-scaling=fixed&starting-point-node-id=84%3A805&show-proto-sidebar=1) will have the following features along with speaker diarization and text to speech. 

1. Text (transcript) simplification using LLM
2. Text highlighting of important and critical keywords (transcript) using LLM
3. Intelligently apply simplification/highlighting to the transcriptions and provide easy summarizations.

Based on the user feedback from our focus groups, we will refine and add more features to the POC.

## SUNVA AI Architecture

Please go through the [architecture diagram](https://www.figma.com/board/INrqk911VUw8uF29VrVnMw/Sunva-p1-flow-diagram?node-id=0-1&t=HF91DJzPwA6QnQT6-1) to understand how SUNVA AI works. Please raise your questions in the issues section if you have any.

## How to run POC

1. Clone the repository
2. Install the dependencies
```
poetry install
```
3. Install Redis and start the server in the background
```
redis-server &
```
4. Create a .env file inside ops dir and add the following variables
```
DATABASE_URL=YOURPOSTGRES_URL
GROQ_API_KEY=your_api_key
CLAUDE_API_KEY=your_api_key
OPENAI_API_KEY=your_api_key
BASE_MODEL=model_name (eg: Claude 3 Sonnet)
SPEECH_BASE_MODEL=model_name (eg: Whisper Large)
TTS_BASE_MODEL=model_name (eg: coqui-tacotron2)
JWT_SECRET_KEY=your_secret_key
```
5. Run the POC
```
uvicorn main:app --reload
```
6. Open the browser and go to
```
http://localhost:8000/
```

### Using Poetry installer

1. Run this to enter virtual env
```
poetry shell
```
2. Install the dependencies
```
poetry install
```

## How to contribute

There are few ways you can contribute to SUNVA AI.

1. By providing feedback on the POC
2. By raising issues in the issues section
3. By contributing to the codebase based on the issues
4. Join the SUNVA AI team by filling the [p+ai volunteer form](https://peopleplus.ai/volunteer) and select the SUNVA AI project.




