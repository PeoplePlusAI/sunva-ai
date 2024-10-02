import requests
import os
from dotenv import load_dotenv

load_dotenv(
    dotenv_path="ops/.env"
)

class Bhashini:
    ulcaBaseURL = os.getenv("ulcaBaseURL")
    modelPipelineEndpoint = os.getenv("modelPipelineEndpoint")
    userId = os.getenv("userId")
    ulcaApiKey =  os.getenv("ulcaApiKey")

    def __init__(self):
        body = {
            "pipelineTasks" : [
                {
                    "taskType" : "asr"
                },
                {
                    "taskType": "translation"
                },
                {  
                    "taskType": "tts"
                }
            ],
            "pipelineRequestConfig" : {
                "pipelineId": "64392f96daac500b55c543cd"
            }
        }
        
        self.response = requests.post(url=self.ulcaBaseURL + self.modelPipelineEndpoint,
                                      json=body, 
                                      headers={
                                            "userID": self.userId, 
                                            "ulcaApiKey": self.ulcaApiKey}).json()

        self.nmtData = self.response['pipelineResponseConfig'][1]['config']
        self.ttsData = self.response['pipelineResponseConfig'][2]['config']
        availableLang = ['bn', 'en', 'gu', 'hi', 'kn', 'ml', 'mr', 'or', 'pa','ta','te']
        self.asrConfigs = {}
        self.nmtConfigs = {}
        self.ttsConfigs = {}

        for i in availableLang:
            self.nmtConfigs[i] = []

        for i in availableLang:
            data = []
            for j in self.nmtData:
                if (j['language']['sourceLanguage'] == i):
                    data.append({'targetLanguage':j['language']['targetLanguage'],'serviceId': j['serviceId']})
            self.nmtConfigs[i] = data

        for i in self.ttsData:
            if (i['language']['sourceLanguage'] in availableLang):
                self.ttsConfigs[i['language']['sourceLanguage']] = i['serviceId']

        self.inferenceApiKey = {
            "Authorization": "hXd6A71xfDHygwnSEXUjFsmd64Vi8vpmhV4geokrx37JZQYXLf0QKsEaABvz4GRX"
        }

        self.callbackUrl = "https://dhruva-api.bhashini.gov.in/services/inference/pipeline"

    def sendHeaderWithConfig(self, sourceLanguage, targetLanguage):
        header = {
            "pipelineTasks": [
                {
                    "taskType": "asr",
                    "config": {
                        "language": {
                            "sourceLanguage": sourceLanguage
                        }
                    }
                },
                {
                    "taskType": "translation",
                    "config": {
                        "language": {
                            "sourceLanguage": sourceLanguage,
                            "targetLanguage": targetLanguage
                        }
                    }
                },
                {
                    "taskType": "tts",
                    "config": {
                        "language": {
                            "sourceLanguage": targetLanguage
                        }
                    }
                }
            ],
            "pipelineRequestConfig": {
                "pipelineId": os.getenv("pipelineId")
            }
        }
        try:
            response = requests.post(url=self.ulcaBaseURL + self.modelPipelineEndpoint, 
                                     json=header, 
                                     headers={"userID": self.userId, "ulcaApiKey": self.apiKey})
            return response.json()
        except Exception as e:
            print(f"Error: {e}")
            return None
    

    def speechToText(self, sourceLanguage, asrServiceId, payload):
        body = {
                "pipelineTasks": [
                    {
                        "taskType": "asr",
                        "config": {
                            "language": {
                                "sourceLanguage": sourceLanguage
                            },
                            "serviceId": asrServiceId,
                            "audioFormat": "flac",
                            "samplingRate": 16000
                        }
                    }
                ],
                "inputData": {
                    "audio": [
                        {
                            "audioContent": payload
                        }
                    ]
                }
            }

        response = requests.post(self.callbackUrl,
                                 headers=self.inferenceApiKey,
                                 json=body).json()['pipelineResponse'][0]['output'][0]['source']
        return response

    def textToSpeech(self,ttsServiceId,text,targetLanguage):
        body = {
                "pipelineTasks": [       
                {
                    "taskType": "tts",
                    "config": {
                        "language": {
                            "sourceLanguage": targetLanguage
                        },
                        "serviceId": ttsServiceId,
                        "gender": "male",
                        "samplingRate": 8000
                    }
                }
            ],
            "inputData": {
                "input": [
                    {
                        "source": text
                    }
                ]
            }
        }

        response = requests.post(self.callbackUrl,
                                 headers=self.inferenceApiKey,
                                 json=body)
        return response.json() #audiodata in base 64
    
    