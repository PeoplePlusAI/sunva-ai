# SUNVA AI : Solving conversation problem for the deaf

## About SUNVA AI

Having conversations with the deaf can be a challenge. While there are so many live transcription and text to speech tools available in the market, they do not cater to the needs of the deaf and hard of hearing and aren't designed from accessibility focus. Often it could take a lot of time for the deaf person to read transcriptions and respond to them depending on various factors from person to person. SUNVA AI intelligently simplifies and provides various filters on the transcriptions to minimize the amount of time taken to read transcription and switch gaze between the screen and the person while having the communication..

## SUNVA AI workplan 

The [first version of the POC](https://www.figma.com/proto/xK0fvVJL9wRWTkwdBeRu2U/Sunva.Ai?page-id=84%3A803&node-id=84-805&viewport=917%2C520%2C0.14&t=ZpNPT9hGNjHWzrqy-1&scaling=min-zoom&content-scaling=fixed&starting-point-node-id=84%3A805&show-proto-sidebar=1) will have the following features along with speaker diarization and text to speech. 

1. Text (transcript) simplification using LLM
2. Text highlighting of important and critical keywords (transcript) using LLM
3. Intelligently apply simplification/highlighting to the transcriptions and provide easy summarizations.

Based on the user feedbacks from our focus groups, we will refine and add more features to the POC.

## SUNVA AI Architecture

Please go through the [architecture diagram](https://www.figma.com/board/INrqk911VUw8uF29VrVnMw/Sunva-p1-flow-diagram?node-id=0-1&t=HF91DJzPwA6QnQT6-1) to understand how SUNVA AI works. Please raise your questions in the issues section if you have any.

## How to run POC

1. Clone the repository
2. Install the dependencies
```
pip install -r requirements.txt
```
3. Create a .env file inside ops dir and add the following variables
```
GROQ_API_KEY=your_api_key
```
4. Run the POC
```
uvicorn main:app --reload
```
5. Open the browser and open the index.html file.
6. Click on the start button to start the conversation.
7. Or run the following to see this in terminal
```
python client.py
```

## How to contribute

There are few ways you can contribute to SUNVA AI.

1. By providing feedback on the POC
2. By raising issues in the issues section
3. By contributing to the codebase based on the issues
4. Join the SUNVA AI team by filling the [p+ai volunteer form](https://peopleplus.ai/volunteer) and select the SUNVA AI project.






