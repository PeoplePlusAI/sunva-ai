# API Documentation

## Endpoints

### 1. Check Server Health
- **Endpoint**: `GET /is-alive`
- **Description**: Check if the server is running and responsive.
- **Response**:
  - **Status Code**: `200 OK`
  - **Response Body**:
    ```json
    {
        "status": "alive"
    }
    ```

---

### 2. Get All Transcriptions
- **Endpoint**: `GET /v1/transcriptions`
- **Description**: Retrieve a list of all transcriptions stored in the database.
- **Response**:
  - **Status Code**: `200 OK`
  - **Response Body**:
    ```json
    {
        "transcriptions": [
            {
                "id": 1,
                "transcription": "This is a sample transcription."
            },
            {
                "id": 2,
                "transcription": "Another example transcription."
            }
        ]
    }
    ```
  - **Response Model**: `TranscriptionResponse`
    - **transcriptions**: A list of `Transcription` objects, each containing:
      - `id` (int): The unique identifier of the transcription.
      - `transcription` (str): The text of the transcription.

---

### 3. Get Transcription by ID
- **Endpoint**: `GET /v1/transcriptions/{transcription_id}`
- **Description**: Retrieve a specific transcription by its ID.
- **Path Parameters**:
  - `transcription_id` (int): The ID of the transcription to retrieve.
- **Response**:
  - **Status Code**: `200 OK`
  - **Response Body**:
    ```json
    {
        "transcription": {
            "id": 1,
            "transcription": "This is a sample transcription."
        }
    }
    ```
  - **Response Model**: `SingleTranscriptionResponse`
    - **transcription**: A `Transcription` object containing:
      - `id` (int): The unique identifier of the transcription.
      - `transcription` (str): The text of the transcription.
- **Error Responses**:
  - **404 Not Found**: If the transcription with the specified ID does not exist.
    ```json
    {
        "detail": "Transcription not found"
    }
    ```

---

### 4. WebSocket: Real-Time Transcription and Processing
- **Endpoint**: `WebSocket /v1/ws/transcription`
- **Description**: Establish a WebSocket connection to stream audio data in real-time for transcription and processing.
- **WebSocket Communication**:
  - **Client to Server**:
    - The client sends a JSON message containing the audio data and optional language:
      ```json
      {
          "language": "en",
          "user_id": "<uuid>",
          "audio": "<base64_encoded_audio_data>"
      }
      ```
  - **Server to Client**:
    - The server response for transcription:
      ```json
      {
          "message_id": "<uuid>",
          "text" : "This is a partial transcription.",
          "type": "transcription"
      }
      ```
    - The server response for processed text:
      ```json
      {
          "message_id": "<uuid>",
          "text" : "This is a processed text.",
          "type": "concise"
      }
      ```
      ```json
      {
          "message_id": "<uuid>",
          "text" : "This is a <b>processed text</b>.",
          "type": "highlight"
      }
      ```
  - **Processing Logic**:
    - The server processes audio chunks, updates the transcription, and sends it back to the client in real-time.
    - The processed text is also returned after reaching a word threshold.
  - **WebSocket Closure**:
    - The server saves the final transcription and processed text to Redis upon client disconnection.

---

### 5. Save Transcription
- **Endpoint**: `POST /v1/transcription/save`
- **Description**: Save the most recent transcription session for a specific user to the database.
- **Query Parameters**:
  - `user_id` (str): The unique identifier of the user whose transcription data should be saved.
  - `language` (str): The language code of the transcription data.
- **Response**:
  - **Status Code**: `200 OK`
  - **Response Body**:
    ```json
    {
        "status": "success",
        "message": "Transcription saved successfully."
    }
    ```
- **Error Responses**:
  - **404 Not Found**: If no active transcription session exists for the user.
    ```json
    {
        "detail": "No active transcription session for this user."
    }
    ```
  - **500 Internal Server Error**: If there is an issue retrieving session data.
    ```json
    {
        "detail": "Failed to retrieve session data."
    }
    ```
---

### 6. WebSocket: Text-to-Speech (TTS) Processing
- **Endpoint**: `WebSocket /v1/ws/speech`
- **Description**: Establish a WebSocket connection to send text data and receive synthesized speech audio in real-time.
- **WebSocket Communication**:
  - **Client to Server**:
    - The client sends a JSON message containing the text and optional language for TTS processing:
      ```json
      {
          "language": "en",
          "user_id": "<uuid>",
          "text": "Hello, how are you?"
      }
      ```
  - **Server to Client**:
    - The server responds with the synthesized audio in base64 format:
      ```json
      {
          "audio": "<base64_encoded_audio_data>"
      }
      ```
  - **Processing Logic**:
    - The server processes the text using TTS, caches the result in Redis, and returns the audio data to the client.
    - At the end of the session, the cached data is persisted to the database, and the cache is cleared.
  - **WebSocket Closure**:
    - When the client disconnects, the server saves the cached TTS data to the database and clears the cache.

---

### 7. Get all available languages
- **Endpoint**: `GET /v1/languages`
- **Description**: Retrieve a list of all available languages for transcription and TTS processing.
- **Response**:
  - **Status Code**: `200 OK`
  - **Response Body**:
    ```json
    {
        "languages": [
            "en",
            "hi"
        ]
    }
    ```

---

### 8. User Registration
- **Endpoint**: `POST /user/register`
- **Description**: Create a new user with a unique identifier.
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "securepassword"
  }
  ```
- **Response**:
  ```json
  {
    "user_id": "uuid",
    "email": "user@example.com",
    "access_token": "jwt_token"
  }
  ```

### 9. User Login (Create Session)
- **Endpoint**: `POST /user/login`
- **Description**: Authenticate a user and create a new session.
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "securepassword"
  }
  ```
- **Response**:
  - **Status Code**: `200 OK`
  - **Response Body**:
    ```json
    {
      "user_id": "uuid",
      "email": "user@example.com",
      "access_token": "jwt_token"
    }
    ```
- **Note**: If a valid token is provided in the Authorization header, the endpoint will return the existing session information.

### 10. User Logout (Delete Session)
- **Endpoint**: `POST /user/logout`
- **Description**: Log out the user and delete their session.
- **Headers**: 
  - `Authorization: Bearer <access_token>`
- **Response**:
  ```json
  {
    "message": "Successfully logged out"
  }
  ```

---