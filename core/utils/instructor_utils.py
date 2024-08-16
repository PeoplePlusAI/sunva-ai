import json
import instructor
from pydantic import BaseModel
from groq import Groq

def patch_client(client: Groq):
    """
    Patch the client with the instructor
    """
    return instructor.patch(client)