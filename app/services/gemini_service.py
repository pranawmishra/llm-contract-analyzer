from google import genai
from google.genai import types
from app.utils.utils import load_prompts
from pydantic import BaseModel

class ClauseSchema(BaseModel):
    termination_clause: str
    confidentiality_clause: str
    liability_clause: str

class GeminiService:
    """
    Service for interacting with the Gemini API.

    Attributes:
        client: The Gemini client.
        prompts: The prompts for the Gemini API.

    """
    def __init__(self):
        self.client = genai.Client()
        self.prompts = load_prompts()

    async def extract_clauses(self, contract_text):
        try:
            print("Extracting clauses...")
            response = await self.client.aio.models.generate_content(
                model="gemini-2.5-flash",
                config=types.GenerateContentConfig(
                    system_instruction=self.prompts["extract_clause_prompt"],
                    temperature=0.0,
                    response_mime_type="application/json",
                    response_schema=ClauseSchema
                ),
                contents=contract_text
            )

            clauses = response.parsed

            return clauses
        except Exception as e:
            print(f"Error extracting clauses: {e}")
            return None
    
    async def extract_summary(self, contract_text):
        try:
            print("Extracting summary...")
            response = await self.client.aio.models.generate_content(
                model="gemini-2.5-flash",
                config=types.GenerateContentConfig(
                    system_instruction=self.prompts["extract_summary_prompt"]
                ),
                contents=contract_text
            )

            return response.text
        except Exception as e:
            print(f"Error extracting summary: {e}")
            return ""