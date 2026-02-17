from google import genai
from google.genai import types

from authentication.models import ARUser

def test():
    user = ARUser.objects.get(id=1)
    api_key = user.gemini_key_encrypted
    